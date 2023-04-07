import os
import re
import threading
import tkinter
from pathlib import Path
from tkinter import filedialog, messagebox
from urllib.parse import urljoin

import customtkinter
import requests
from bs4 import BeautifulSoup

import path_validator as PV


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Scraper")
        self.pdf_links=[]
        
        self.url_label = customtkinter.CTkLabel(self, text="URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.url_entry = customtkinter.CTkEntry(self, width=400)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.folder_label = customtkinter.CTkLabel(self, text="Download Location:")
        self.folder_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.folder_entry = customtkinter.CTkEntry(self, width=400)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.folder_button = customtkinter.CTkButton(self, text="Browse", command=self.select_folder)
        self.folder_button.grid(row=1, column=2, padx=10, pady=10)
        
        self.output_text = customtkinter.CTkTextbox(self, height=200, width=650)
        self.output_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        
        self.range_frame = customtkinter.CTkFrame(self, fg_color=self._fg_color)
        #self.range_frame.grid(row=3, column=1)
        self.range_label = customtkinter.CTkLabel(self.range_frame, text="Range: ")
        self.range_label.grid(row=0, column=0, padx=10, pady=10)

        self.lower_range_entry = customtkinter.CTkEntry(self.range_frame, width=50)
        self.lower_range_entry.grid(row=0, column=1,padx=10,pady=10)

        self.higher_range_entry = customtkinter.CTkEntry(self.range_frame, width=50)
        self.higher_range_entry.grid(row=0, column=2, padx=10, pady=10)

        self.find_button = customtkinter.CTkButton(self, text="Display PDFs", command=self.find_url_button_event)
        self.find_button.grid(row=4, column=0, padx=10, pady=10)
        
        self.download_button = customtkinter.CTkButton(self, text="Download", command=self.download_button_event)
        self.download_button.grid(row=4, column=1, padx=10, pady=10)

        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", state="disabled", command=self.cancel_download)
        self.cancel_button.grid(row=4, column=2, padx=10, pady=10)

        self.mainloop()
    def is_url(self, url):
        if len(url)>0:
            return True
        else:
            messagebox.showerror("PDF Scraper","Please enter a Valid URL")
            return False
    def find_url_button_event(self, download_next=False):
        url=self.url_entry.get()
        self.download_button.configure(state="disabled")
        self.find_button.configure(state="disabled")
        
        if not self.is_url(url):
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return 

        self.new_thread=threading.Thread(target=self.find_urls)
        self.new_thread.start()
        if download_next:
            self.after(2000, self.check_result)
    def check_result(self):
        if len(self.pdf_links)>0:
            self.download_button_event()
        else:
            self.after(2000, self.check_result)
    def find_urls(self):
        url=self.url_entry.get()
        self.url = url
        try:
            response=requests.get(url)
        except requests.exceptions.MissingSchema:
            self.output_text.insert(customtkinter.END, "ERROR: Invalid URL: {}\n".format(url))
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return
        except requests.exceptions.ConnectionError:
            messagebox.showerror("PDF Scraper", "Please check your internet connecion")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return
       
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')
        self.pdf_links=[]
        i = 0
        for link in links:
            if ('.pdf' in link.get('href', [])):
                i+=1
                self.output_text.insert(customtkinter.END, ("File {}: {}".format(i, link['href']+"\n")))
                filename_option_one=re.sub('<[^>]+>', '', str(link))
                filename_option_two=link['href'].split('/')[-1].replace(".pdf","")
                if filename_option_one==filename_option_two:
                    self.output_text.insert(customtkinter.END,("Filename: {} \n".format(filename_option_one)))
                    self.filename_equal = True
                else:
                    self.output_text.insert(customtkinter.END,("Filename Option 1: {} \n".format(filename_option_one)))
                    self.output_text.insert(customtkinter.END,("Filename Option 2: {} \n".format(filename_option_two)))
                    self.filename_equal = False
                self.output_text.see("end")
                self.pdf_links.append(link)
        if i>0:
             message="Total of {} pdfs found on this URL\n".format(i)
        else:
            message="No PDFs were found\n"
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
        self.output_text.insert(customtkinter.END,message)
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_entry.delete(0, customtkinter.END)
        self.folder_entry.insert(0, folder_path)
    
    def valid_directory(self, directory):
        if len(directory)==0:
            if not messagebox.askokcancel("PDF Scraper","You have not specified a download location, the files will download in the current directory."):
                return False
            else:
                self.folder_entry.delete(0, customtkinter.END)
                self.folder_entry.insert(0, os.getcwd())
        
        elif not PV.is_path_exists_or_creatable(directory):
            self.output_text.insert(customtkinter.END, "Invalid Directory provided by user\n")
            self.output_text.see("end")
            return False
        
        return True 
    def download_button_event(self):
        self.download_button.configure(state="disabled")
        self.find_button.configure(state="disabled")
        if len(self.pdf_links) < 1:
            self.find_url_button_event(True)
            return
        if self.url != self.url_entry.get():
            self.find_url_button_event(True)
            return
        if not self.valid_directory(self.folder_entry.get()):
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return
        if not self.filename_equal:
            self.naming_choice = tkinter.messagebox.askyesnocancel("PDF Scraper", "By default, the files will be named according to Option 1. Press No to name them according to Option 2.")
        else:
            self.naming_choice=True
        if self.naming_choice is None:
            self.output_text.insert(customtkinter.END, "Operation cancelled by user\n")
            self.output_text.see("end")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return
        if self.lower_range_entry is None:
            pass
        self.download_thread=threading.Thread(target=self.download_pdf)
        self.download_thread.start()
    def cancel_download(self):
        self.download_cancel_raised = True
    def download_pdf(self):
        self.download_cancel_raised = False
        self.cancel_button.configure(state="normal")
        folder_location=self.folder_entry.get().replace("/","\\")
        success_count=0
        for i, pdf_link in enumerate(self.pdf_links, start=1):   
            if self.download_cancel_raised:
                self.download_cancel_raised=False
                self.cancel_button.configure(state="disabled")
                self.output_text.insert(customtkinter.END, "Operation cancelled by user\n")
                self.download_button.configure(state="normal")
                self.find_button.configure(state="normal")
                return
            if self.naming_choice: 
                filename = re.sub('<[^>]+>', '', str(pdf_link))
            else:
                filename = pdf_link['href'].split('/')[-1]
            
            if not os.path.exists(folder_location):Path(folder_location).mkdir(parents=True, exist_ok=True)
            file_location = os.path.join(folder_location, filename)
            with open(file_location+".pdf", "wb") as pdf:
                try:
                    self.output_text.insert(customtkinter.END,("File {}: {}\n".format(i, filename)))
                    self.output_text.see("end")
                    pdf.write((requests.get(pdf_link.get('href'))).content)
                    success_count+=1
                except:
                    self.output_text.insert(customtkinter.END,("Download failed, attempting alternative method\n"))
                    self.output_text.insert(customtkinter.END,("Downloading file {} with alternative method: {}\n".format(i, filename)))
                    self.output_text.see("end")
                    pdf.write(requests.get(urljoin(self.url_entry.get(),pdf_link['href'])).content)
                    success_count+=1
        if success_count==len(self.pdf_links):
            self.output_text.insert(customtkinter.END,("All {} PDF files successfully downloaded to {}\n".format(success_count, folder_location)))
        else:
            self.output_text.insert(customtkinter.END("{} / {} PDF files downloaded\n".format(success_count, len(self.pdf_links))))
        self.cancel_button.configure(state="disabled")  
        self.download_button.configure(state="normal")
        self.find_button.configure(state="normal") 
#-------------------------------------------------------------





PDFScraper = App()




