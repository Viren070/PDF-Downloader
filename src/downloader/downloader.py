
import os
import requests
from urllib.parse import urljoin
from io import BytesIO
import re
from time import perf_counter
class FileDownloadError(Exception):
    def __init__(self, downloaded_size, total_size, elapsed_time):
        self.downloaded_size = downloaded_size
        self.total_size = total_size
        self.elapsed_time = elapsed_time
        super().__init__(self.__str__())

    def __str__(self):
        return (f"File was not completely downloaded "
                f"{self.downloaded_size/1024/1024:.1f} MB / {self.total_size/1024/1024:.1f} MB\n"
                f"Exited after {self.elapsed_time:.1f} s. after 3 attempts")
        
        
class AbortDownload(Exception):
    def __init__(self):
        super().__init__(self.__str__())

    def __str__(self):
        return (f"Download was aborted by user")
class PDF:
    def __init__(self, pdf_id, filename, url, download_folder):
        self.pdf_id = pdf_id
        self.filename = filename
        self.url = url 
        self.download_folder = download_folder 
        self.response = None 
        self.download_attempts = 1
        self.session_attempts = 1
        
        self.file_path = os.path.join(self.download_folder, self.filename+".pdf")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
    def create_session(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36', # user agent 
            'Accept-Encoding': 'identity' # Disable compression
        }

        try:
            session = requests.Session()
            
            self.response = session.get(self.url, headers=headers, stream=True, timeout=10)
            self.response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.session_attempts+=1
            if self.session_attempts > 3:
                raise requests.exceptions.RequestException(error) from error
            else:
                print("retrying to create session for session")
                self.create_session()
                return

        
    
        # response=requests.get(link, headers=headers, stream=True)
        self.filesize = int(self.response.headers.get('content-length', 0))
        
        if self.filesize == 0:
            self.session_attempts+=1
            if self.session_attempts > 3:
                print("After 3 retries, filesize was still 0 so set as None")
                self.filesize = None
            else:
                print("retrying to create session for filesize")
                self.create_session()
                return
        

            
    def download_pdf(self, progress_bar):
        initial_value = progress_bar.get()
        print(f"Downloading {self.filename} on attempt number {self.download_attempts}... ")
        with BytesIO() as f:

            start_time = perf_counter()
        
            if self.filesize is None:
                if progress_bar.cancel_raised:
                    raise AbortDownload()
                progress_bar.update_progress(0)
                progress_bar.update_progress_label(f"0 MB / 0 MB")
                data = self.response.content
                progress_bar.update_progress_label(f"0 MB / {len(data)} MB")
                f.write(data)
                progress_bar.downloaded_bytes += len(data)
                progress_bar.total_bytes += len(data)
                progress_bar.update_total_progress_label(f"{progress_bar.downloaded_bytes/1024/1024:.1f}")
                progress_bar.update_progress_label(f"{len(data)/1024/1024:.1f} MB / {len(data)/1024/1024:.1f} MB")
                progress_bar.downloaded_files += 1
                progress_bar.update_total_progress(progress_bar.downloaded_files/progress_bar.total)
                progress_bar.update_progress(1)
                downloaded_bytes = None
            else:
                downloaded_bytes = 0
                for data in self.response.iter_content(chunk_size=1024*128):
                    if progress_bar.cancel_raised:
                        raise AbortDownload()
                    downloaded_bytes += len(data)
                    progress_bar.downloaded_bytes+=len(data)
                    f.write(data)
                    pbar_value = downloaded_bytes / self.filesize
                    pbar_total_value = progress_bar.downloaded_bytes / progress_bar.total_bytes
                    progress_bar.update_progress(pbar_value)
                    progress_bar.update_total_progress(pbar_total_value)
                    progress_bar.update_speed(f"{((progress_bar.downloaded_bytes / (perf_counter() - progress_bar.start_time))/1024/1024):.1f}" )
                    progress_bar.update_progress_label(f"{downloaded_bytes/1024/1024:.1f} MB / {self.filesize/1024/1024:.1f} MB")
                    progress_bar.update_total_progress_label(f"{progress_bar.downloaded_bytes/1024/1024:.1f}")
            if downloaded_bytes != self.filesize:
                self.download_attempts += 1
                if self.download_attempts < 3:
                    print(f"ERROR WHILE DOWNLOADING {self.filename}. Attempting again...\nReceived file size of {self.filesize} but only downloaded {downloaded_bytes}")

                    progress_bar.downloaded_bytes -= downloaded_bytes
                    self.create_session()
                    self.download_pdf(progress_bar)
                    print("returning")
                    return
                else:
                    print("exceeded 3 retries")
                    raise FileDownloadError(downloaded_bytes, self.filesize, perf_counter() - start_time)
            try:
                with open(self.file_path, 'wb') as file:
                    file.write(f.getvalue())
                    print(f"Downloaded {self.filename} on attempt number {self.download_attempts} to {self.file_path} ")
            except PermissionError as error:
                progress_bar.downloaded_bytes -= self.filesize
                print("should raise permission error")
                raise PermissionError(error) from error
        return self.file_path
        