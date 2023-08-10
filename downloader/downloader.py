
import customtkinter
import os
from pathlib import Path
import requests
from urllib.parse import urljoin
from tkinter import messagebox
from io import BytesIO
from time import perf_counter

class PDF:
    def __init__(self, filename, url, download_folder):
        self.filename = filename
        self.url = url 
        self.download_folder = download_folder 
        self.filesize = 0
        self.response = None 

        

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        headers = {
            'Accept-Encoding': 'identity'  # Disable compression
        }
        try:
            session = requests.Session()
            self.response = session.get(self.url, headers=headers, stream=True)
            self.response.raise_for_status()
        except requests.exceptions.MissingSchema as error:
            messagebox.showerror("Missing Schema Error", error)
            return
        except requests.exceptions.InvalidSchema as error:
            messagebox.showerror("Invalid Schema Error", error)
            return
        except requests.exceptions.ConnectionError as error:
            messagebox.showerror("Connection Error", error)
            return
        except Exception as error:
            return None
    
        # response=requests.get(link, headers=headers, stream=True)
        self.filesize = int(self.response.headers.get('content-length', 0))
        self.file_path = os.path.join(download_folder, filename+".pdf")


            
    def download_pdf(self, progress_bar):
            initial_value = progress_bar.get()
            with BytesIO() as f:

                start_time = perf_counter()
            
                if self.filesize is None:
                    f.write(self.response.content)
                else:
                    downloaded_bytes = 0
                    for data in self.response.iter_content(chunk_size=1024*512):
                        
                        downloaded_bytes += len(data)
                        f.write(data)
                        new_value = initial_value + (downloaded_bytes / progress_bar.total_bytes)
                        progress_bar.update_progress(new_value)
                        progress_bar.update_speed(f"{((downloaded_bytes / (perf_counter() - start_time))/1024/1024):.2f}" )
                        progress_bar.progress_label.configure(text=f"{downloaded_bytes/1024/1024:.2f} MB / {self.filesize/1024/1024:.2f} MB")
                if downloaded_bytes != self.filesize:
                    raise Exception(
                        f"File was not completely downloaded {(downloaded_bytes/1024/1024):.2f} MB / {(self.filesize/1024/1024):.2f} MB\n Exited after {(perf_counter() - start_time):.2f} s.")

                with open(self.file_path, 'wb') as file:
                    file.write(f.getvalue())

            return self.file_path
        