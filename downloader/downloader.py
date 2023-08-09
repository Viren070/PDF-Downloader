
import customtkinter
import os
from pathlib import Path
import requests
from urllib.parse import urljoin
from tkinter import messagebox
from io import BytesIO
from time import perf_counter

def download_pdf(link, filename, download_folder):
    download_failures = ""
    if not os.path.exists(download_folder):
        Path(download_folder).mkdir(parents=True, exist_ok=True)
    file_location = os.path.join(download_folder, filename+".pdf") 
    with open(file_location, "wb") as pdf:
        try:
            pdf.write(requests.get(link).content)
        except:
            download_failures+=f"Failed to download {filename} with link {link}"
            os.unlink(file_location)
       
            
def download_pdf_alt(link, filename, download_folder):
        # link = "https://speed.hetzner.de/1GB.bin"
        headers = {
            'Accept-Encoding': 'identity'  # Disable compression
        }
        try:
            session = requests.Session()
            response = session.get(link, headers=headers, stream=True)
            response.raise_for_status()
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
        total_size = int(response.headers.get('content-length', 0))
        file_path = os.path.join(download_folder, filename+".pdf")
        with BytesIO() as f:

            start_time = perf_counter()
          
            if total_size is None:
                f.write(response.content)
            else:
                downloaded_bytes = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded_bytes += len(data)
                    f.write(data)
            
            if downloaded_bytes != total_size:
                raise Exception(
                    f"File was not completely downloaded {(downloaded_bytes/1024/1024):.2f} MB / {(total_size/1024/1024):.2f} MB\n Exited after {(perf_counter() - start_time):.2f} s.")

            with open(file_path, 'wb') as file:
                file.write(f.getvalue())

        return file_path
       