import os
import re
import threading
import tkinter
import time
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
    def range_is_valid(self):
        lower_range = int(self.lower_range_entry.get()) if self.lower_range_entry.get() else 1
        upper_range = int(self.upper_range_entry.get()) if self.upper_range_entry.get() else len(self.pdf_links)
        if upper_range < lower_range or lower_range > len(self.pdf_links) or upper_range > len(self.pdf_links) or lower_range < 1:
            return False
        else:
            return True
    def find_url_button_event(self, download_next=False):
        url=self.url_entry.get()
        self.download_button.configure(state="disabled")
        self.find_button.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.lower_range_entry.configure(state="disabled")
        self.upper_range_entry.configure(state="disabled")
        if not self.is_url(url):
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            return 

        self.new_thread=threading.Thread(target=self.find_urls)
        self.new_thread.start()
        if download_next:
            self.result_thread=threading.Thread(target=self.check_result, args=(url,))
            self.result_thread.start()
            self.waiting_for_result=True
            
    def check_result(self, url):
        print("started check result thread")
        count=1
        while self.waiting_for_result:
            print("count: {}".format(count))
            if not self.waiting_for_result:
                print("waiting for result - false, breaking")
                break
            if self.url_entry.get() != url or self.download_button.cget("state")=="normal":
                print("url changed or other error")
                return
            count+=1
            time.sleep(1)
        if len(self.pdf_links)>0:
            print("starting download button event")
            self.download_button_event()
       
            
     
            
    def find_urls(self):
        url=self.url_entry.get()
        self.url = url
        try:
            response=requests.get(url)
        except requests.exceptions.MissingSchema:
            self.output_text.insert(customtkinter.END, "ERROR: Invalid URL: {}\n".format(url))
            self.output_text.see("end")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            return
        except requests.exceptions.ConnectionError:
            messagebox.showerror("PDF Scraper", "Please check your internet connecion")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            return
        except requests.exceptions.InvalidSchema:
            self.output_text.insert(customtkinter.END, "ERROR: Invalid URL: {}\n".format(url))
            self.output_text.see("end")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            return

        except requests.exceptions.ConnectionError:
            messagebox.showerror("PDF Scraper", "Could not connect to URL")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
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
            
            
            if self.range_is_valid():
                self.lower_range = int(self.lower_range_entry.get()) if self.lower_range_entry.get() else 1
                self.upper_range = int(self.upper_range_entry.get()) if self.upper_range_entry.get() else len(self.pdf_links)
                self.waiting_for_result=False  
            else:
                self.download_button.configure(state="normal")
                self.find_button.configure(state="normal")
                self.lower_range_entry.configure(state="normal")
                self.upper_range_entry.configure(state="normal")
                self.url_entry.configure(state="normal")
                messagebox.showerror("PDF Scraper", "Please enter a valid range")
                return
            if not self.waiting_for_result:
                self.download_button.configure(state="normal")
                self.find_button.configure(state="normal")
                self.lower_range_entry.configure(state="normal")
                self.upper_range_entry.configure(state="normal")
                self.url_entry.configure(state="normal")
             
        else:
            message="No PDF files were found\n"
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
        
        self.output_text.insert(customtkinter.END,message)
        self.output_text.see("end")
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
        self.lower_range_entry.configure(state="disabled")
        self.upper_range_entry.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        if len(self.pdf_links) < 1:
            print("length of array smaller than 1")
            self.find_url_button_event(True)
            return
        if self.url != self.url_entry.get():
            print("self.url is not the url in the entry")
            self.find_url_button_event(True)
            return
        if not self.range_is_valid():
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            messagebox.showerror("PDF Scraper","Please enter a valid range")
            
            return

        if not self.valid_directory(self.folder_entry.get()):
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            print("directory not valid")
            return
        if not self.filename_equal:
            self.naming_choice = tkinter.messagebox.askyesnocancel("PDF Scraper", "The files will be named according to option 1. Press No for option 2.")
        else:
            self.naming_choice=True
        if self.naming_choice is None:
            self.output_text.insert(customtkinter.END, "Operation cancelled by user\n")
            self.output_text.see("end")
            self.download_button.configure(state="normal")
            self.find_button.configure(state="normal")
            self.lower_range_entry.configure(state="normal")
            self.upper_range_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            self.pdf_links=[]
            return
        if self.lower_range != self.lower_range_entry.get() or self.upper_range != self.upper_range_entry.get():
            print("ranges changed")
            self.lower_range = int(self.lower_range_entry.get()) if self.lower_range_entry.get() else 1
            self.upper_range = int(self.upper_range_entry.get()) if self.upper_range_entry.get() else len(self.pdf_links)
        self.download_thread=threading.Thread(target=self.download_pdf)
        self.download_thread.start()
        print("starting download thread")
    def cancel_download(self):
        self.download_cancel_raised = True
    
    def download_pdf(self):
        self.download_cancel_raised = False
        self.cancel_button.configure(state="normal")
        folder_location=self.folder_entry.get().replace("/","\\")
        success_count=0
        

        for i, pdf_link in enumerate(self.pdf_links, start=1):   
            if i < self.lower_range or i > self.upper_range:
                continue
            if self.download_cancel_raised:
                self.download_cancel_raised=False
                self.cancel_button.configure(state="disabled")
                self.output_text.insert(customtkinter.END, "Operation cancelled by user\n")
                self.output_text.see("end")
                self.download_button.configure(state="normal")
                self.find_button.configure(state="normal")
                self.lower_range_entry.configure(state="normal")
                self.upper_range_entry.configure(state="normal")
                self.url_entry.configure(state="normal")
                return
            if self.naming_choice: 
                filename = re.sub('<[^>]+>', '', str(pdf_link))
            else:
                filename = pdf_link['href'].split('/')[-1]
            
            if not os.path.exists(folder_location):Path(folder_location).mkdir(parents=True, exist_ok=True)
            file_location = os.path.join(folder_location, filename)
            with open(file_location+".pdf", "wb") as pdf:
                try:
                    self.output_text.see("end")
                    pdf.write((requests.get(pdf_link.get('href'))).content)
                    self.output_text.insert(customtkinter.END,("Downloaded File {}: {}\n".format(i, filename)))
                    success_count+=1
                except:
                    pass
                try:
                    pdf.write(requests.get(urljoin(self.url_entry.get(),pdf_link['href'])).content)
                    self.output_text.insert(customtkinter.END,("Downloaded file {} with alternative method: {}\n".format(i, filename)))
                    success_count+=1
                except:
                    self.output_text.insert(customtkinter.END,("Failed to download file {}: {}\n".format(i, filename)))
        if success_count==len(self.pdf_links):
            self.output_text.insert(customtkinter.END,("All {} PDF files successfully downloaded to {}\n".format(success_count, folder_location)))  
        elif success_count == (self.upper_range - self.lower_range)+1:
            self.output_text.insert(customtkinter.END,("All {} PDF files within the range {} - {} downloaded to {}\n".format(success_count, self.lower_range, self.upper_range, folder_location)))
        else:
            self.output_text.insert(customtkinter.END, "{} / {} PDF files downloaded\n".format(success_count, len(self.pdf_links)))
        self.output_text.see("end")
        self.cancel_button.configure(state="disabled") 
        self.download_button.configure(state="normal")
        self.find_button.configure(state="normal") 
        self.lower_range_entry.configure(state="normal")
        self.upper_range_entry.configure(state="normal")
        self.url_entry.configure(state="normal")
#-------------------------------------------------------------





PDFScraper = App()




