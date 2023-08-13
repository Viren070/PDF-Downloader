
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
        self.download_attempts = 0

        

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
    def create_session(self):
        headers = {
            'Accept-Encoding': 'identity',  # Disable compression
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
      
        session = requests.Session()
        
        self.response = session.get(self.url, headers=headers, stream=True)
        self.response.raise_for_status()
        
    
        # response=requests.get(link, headers=headers, stream=True)
        self.filesize = int(self.response.headers.get('content-length', 0))
        if self.filesize == 0:
            self.response.headers.clear()
            self.filesize = int(self.response.headers.get('content-length', 0))

            
        if self.filesize == 0:
            headers = {
                'Accept-Encoding': 'identity',  # Disable compression
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Range': 'bytes=0-1023'  # Fetch the first 1024 bytes
            }
            self.response.headers.update(headers)
            print(self.response.headers)

            # Calculate file size based on the content range
            content_range = self.response.headers.get('content-range')
            if content_range:
                start, end, total = map(int, re.findall(r'\d+', content_range))
                self.filesize = end - start + 1
            else:
                print("content range was empty")
        if self.filesize == 0:
            self.filesize = None
        self.file_path = os.path.join(self.download_folder, self.filename+".pdf")


            
    def download_pdf(self, progress_bar):
        initial_value = progress_bar.get()
        with BytesIO() as f:

            start_time = perf_counter()
        
            if self.filesize is None:
                if progress_bar.cancel_raised:
                    raise AbortDownload()
                progress_bar.update_progress(0)
                data = self.response.content
                f.write(data)
                progress_bar.downloaded_bytes += len(data)
                progress_bar.total_bytes = progress_bar.downloaded_bytes
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
                print(f"ERROR WHILE DOWNLOADING {self.filename}. Attempting again...\n\nReceived file size of {self.filesize} but only downloaded {downloaded_bytes}")
                self.download_attempts += 1
                if self.download_attempts <= 3:
                    progress_bar.downloaded_bytes -= downloaded_bytes
                    self.download_pdf(progress_bar)
                else:
                    raise FileDownloadError(downloaded_bytes, self.filesize, perf_counter() - start_time)
            try:
                with open(self.file_path, 'wb') as file:
                    file.write(f.getvalue())
            except PermissionError as error:
                progress_bar.downloaded_bytes -= self.filesize
                
                raise PermissionError(error) from error
        return self.file_path
        