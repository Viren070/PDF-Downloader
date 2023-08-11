
import customtkinter
import os
from pathlib import Path
import requests
from urllib.parse import urljoin
from tkinter import messagebox
from io import BytesIO
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
                f"Exited after {self.elapsed_time:.1f} s.")
        
        
class AbortDownload(Exception):
    def __init__(self):
        super().__init__(self.__str__())

    def __str__(self):
        return (f"Download was aborted by user")
class PDF:
    def __init__(self, filename, url, download_folder):
        self.filename = filename
        self.url = url 
        self.download_folder = download_folder 
        self.response = None 


        

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
    def create_session(self):
        headers = {
            'Accept-Encoding': 'identity'  # Disable compression
        }
      
        session = requests.Session()
        
        self.response = session.get(self.url, headers=headers, stream=True)
        self.response.raise_for_status()
        
    
        # response=requests.get(link, headers=headers, stream=True)
        self.filesize = int(self.response.headers.get('content-length', 0))
        if self.filesize == 0:
            raise ValueError("'0' not valid filesize")
        self.file_path = os.path.join(self.download_folder, self.filename+".pdf")


            
    def download_pdf(self, progress_bar):
        initial_value = progress_bar.get()
        with BytesIO() as f:

            start_time = perf_counter()
        
            if self.filesize is None:
                f.write(self.response.content)
            else:
                downloaded_bytes = 0
                for data in self.response.iter_content(chunk_size=1024*512):
                    if progress_bar.cancel_raised:
                        raise AbortDownload()
                    downloaded_bytes += len(data)
                    progress_bar.downloaded_bytes+=len(data)
                    f.write(data)
                    pbar_value = downloaded_bytes / self.filesize
                    pbar_total_value = progress_bar.downloaded_bytes / progress_bar.total_bytes
                    progress_bar.update_progress(pbar_value)
                    progress_bar.update_total_progress(pbar_total_value)
                    progress_bar.update_speed(f"{((downloaded_bytes / (perf_counter() - start_time))/1024/1024):.1f}" )
                    progress_bar.update_progress_label(f"{downloaded_bytes/1024/1024:.1f} MB / {self.filesize/1024/1024:.1f} MB")
                    progress_bar.update_total_progress_label(f"{progress_bar.downloaded_bytes/1024/1024:.1f}")
            if downloaded_bytes != self.filesize:
                raise FileDownloadError(downloaded_bytes, self.filesize, perf_counter() - start_time)
            try:
                with open(self.file_path, 'wb') as file:
                    file.write(f.getvalue())
            except PermissionError as error:
                progress_bar.downloaded_bytes -= self.filesize
                
                raise PermissionError(error) from error
        return self.file_path
        