import errno
import os
import re
import sys
import threading
import time
import webbrowser
import tkinter
from pathlib import Path
from tkinter import filedialog, messagebox
from urllib.parse import urljoin

import customtkinter
import requests
from bs4 import BeautifulSoup

ERROR_INVALID_NAME = 123

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Downloader")
        self.pdf_links=[]
        self.waiting_for_result = False
        self.geometry("772x577")
        self.resizable(False, False)
        self.title_label = customtkinter.CTkLabel(self, text="PDF Downloader v1.0.0-alpha.2", font=customtkinter.CTkFont(size=24, family="Helvetica", weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.author_label = customtkinter.CTkLabel(self, text="Viren070 on GitHub", cursor="hand2",text_color="blue",font=customtkinter.CTkFont(family="Helvetica", size=15, underline=True))
        self.author_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Viren070"))
        self.author_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.add("Downloader")
        self.tabview.add("Help")
        self.tabview.grid(row=2,column=0, padx=10, pady=10)
        self.url_label = customtkinter.CTkLabel(self.tabview.tab("Downloader"), text="URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.url_entry = customtkinter.CTkEntry(self.tabview.tab("Downloader"), width=400)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.folder_label = customtkinter.CTkLabel(self.tabview.tab("Downloader"), text="Download Location:")
        self.folder_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.folder_entry = customtkinter.CTkEntry(self.tabview.tab("Downloader"), width=400)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.folder_button = customtkinter.CTkButton(self.tabview.tab("Downloader"), text="Browse", command=self.select_folder)
        self.folder_button.grid(row=1, column=2, padx=10, pady=10)
        
        self.output_text = customtkinter.CTkTextbox(self.tabview.tab("Downloader"), height=200, width=650)
        self.output_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        
        self.range_frame = customtkinter.CTkFrame(self.tabview.tab("Downloader"), fg_color=self._fg_color)
        self.range_frame.grid(row=3, column=1)
        self.range_label = customtkinter.CTkLabel(self.range_frame, text="Download within range: ")
        self.range_label.grid(row=0, column=0, padx=10, pady=10)

        self.lower_range_entry = customtkinter.CTkEntry(self.range_frame, width=50)
        self.lower_range_entry.grid(row=0, column=1,padx=10,pady=10)

        self.upper_range_entry = customtkinter.CTkEntry(self.range_frame, width=50)
        self.upper_range_entry.grid(row=0, column=2, padx=10, pady=10)

        self.search_button = customtkinter.CTkButton(self.tabview.tab("Downloader"), text="Search URL for PDFs", command=self.search_url_button_event)
        self.search_button.grid(row=4, column=0, padx=10, pady=10)
        
        self.download_button = customtkinter.CTkButton(self.tabview.tab("Downloader"), text="Download", command=self.download_button_event)
        self.download_button.grid(row=4, column=1, padx=10, pady=10)

        self.cancel_button = customtkinter.CTkButton(self.tabview.tab("Downloader"), text="Cancel Download", state="disabled", command=self.cancel_download)
        self.cancel_button.grid(row=4, column=2, padx=10, pady=10)
        
        self.reset_button = customtkinter.CTkButton(self.tabview.tab("Downloader"), text="Reset", command=self.reset_widgets)
        self.reset_button.grid(row=3, column=2, padx=10, pady=10)

        self.help_one_title_label = customtkinter.CTkLabel(self.tabview.tab("Help"), text="Why are there two options for filenames?", font=customtkinter.CTkFont(size=20, family="Helvetica", weight="bold"))
        self.help_one_title_label.grid(row=0, column=0)
        self.help_one_answer_label = customtkinter.CTkLabel(self.tabview.tab("Help"), text="Option 1 gets the filename from the text that is visible on the website itself whereas Option 2 gets the filename from the end of    \nthe link for the PDF File.")
        self.help_one_answer_label.grid(row=1, column=0, padx=10, pady=10)

        self.help_two_title_label = customtkinter.CTkLabel(self.tabview.tab("Help"), text="What does the 'Reset' button do?", font=customtkinter.CTkFont(size=20, family="Helvetica", weight="bold"))
        self.help_two_title_label.grid(row=2, column=0)
        self.help_two_answer_label = customtkinter.CTkLabel(self.tabview.tab("Help"), text="Incase all the widgets become disabled due to an unhandled error, you can click the 'Reset' button to essentially reset the \napplication")
        self.help_two_answer_label.grid(row=3, column=0, padx=10, pady=10)
        
        self.mainloop()
        
    def reset_widgets(self):
        self.change_widget_state("normal")
        self.cancel_download()
        self.pdf_links=[]
        self.url=None
        self.url_entry.delete(0, "end")
        self.folder_entry.delete(0, "end")
        self.lower_range_entry.delete(0, "end")
    def is_url(self, url):
        if len(url)>0:
            return True
        else:
            messagebox.showerror("PDF Scraper","Please enter a Valid URL")
            
            return False
    def range_is_valid(self):
        try:
            lower_range = int(self.lower_range_entry.get()) if self.lower_range_entry.get() else 1
            upper_range = int(self.upper_range_entry.get()) if self.upper_range_entry.get() else len(self.pdf_links)
        except ValueError:
            return False
        if upper_range < lower_range or lower_range > len(self.pdf_links) or upper_range > len(self.pdf_links) or lower_range < 1:
            return False
        else:
            return True
        
    def check_result(self, url):
        while self.waiting_for_result:
            if not self.waiting_for_result:
                break
            if self.url_entry.get() != url or self.download_button.cget("state")=="normal":
                return
            time.sleep(1)
        

        if len(self.pdf_links)>0:
            self.download_button_event()
       
    def search_url_button_event(self, download_next=False):
        url=self.url_entry.get()
        self.waiting_for_result=False
        if not self.is_url(url):
            return 
        self.change_widget_state("disabled")
        
        self.new_thread=threading.Thread(target=self.search_url_and_decide_names)
        self.new_thread.start()
        if download_next:
            self.waiting_for_result=True
            self.result_thread=threading.Thread(target=self.check_result, args=(url,))
            self.result_thread.start()
            

    def search_url_and_decide_names(self):
        self.url = self.url_entry.get()
        try:
            self.output_text.insert(customtkinter.END, "Searching URL...\n")
            self.output_text.see("end")            
            response=requests.get(self.url)
        except requests.exceptions.MissingSchema:
            self.output_text.insert(customtkinter.END, "ERROR: Invalid URL: {}\n".format(self.url))
            self.output_text.see("end")
            self.change_widget_state("normal")
            return
       
        except requests.exceptions.InvalidSchema:
            self.output_text.insert(customtkinter.END, "ERROR: Invalid URL: {}\n".format(self.url))
            self.output_text.see("end")
            self.change_widget_state("normal")
            return
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("PDF Scraper", "Could not connect to URL")
            self.change_widget_state("normal")
            return
    
    
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')
        self.pdf_links=[]
        choice=None
        duplicate_count=0
        pdf_index=-1
        for link in links:
            if ('.pdf' in link.get('href', [])) and not(link.get('href', []) in [l[0]['href'] for l in self.pdf_links]):
                pdf_index+=1
                filename_one=re.sub('<[^>]+>', '', str(link)) if not re.sub('<[^>]+>', '', str(link)) == "" else "PDF {}".format(pdf_index+1)
                filename_two=link['href'].split('/')[-1].split('.pdf')[-2] if not link['href'].split('/')[-1].split('.pdf')[-2] == "" else "PDF {}".format(pdf_index+1)
                if filename_one in [l[1] for l in self.pdf_links]:
                    # filename already exists in pdf_links list
                    
                    duplicate_count+=1
                    if choice is None:
                        custom_string=""
                        choice=messagebox.askyesno("PDF Downloader","Duplicate filenames have been detected for Option 1. Would you like to use the previous files' name and add a string. (This is only useful for specific scenarios such as if the duplicate names are 'Answers'. If you say No the files will be incrementally numbered each time a duplicate filename is discovered)")
                        index = [ind for ind, l in enumerate(self.pdf_links) if filename_one == l[1]][0]
                        if choice: custom_string=customtkinter.CTkInputDialog(text="Enter a custom string to be added to the end of duplicate filenames", title="CTkInputDialog").get_input()
    
                        if choice and (custom_string == "" or (" " in custom_string and len(custom_string)<4)):
                            choice=False
                    if choice:
                        filename_one=(str(self.pdf_links[pdf_index-1][1])+" - "+custom_string)
                        
                    else:
                        filename_one=filename_one+" - "+str(duplicate_count+1)
            
                if filename_two in [l[2] for l in self.pdf_links]:
                    filename_two = filename_two+"_- "+str(duplicate_count+1)
             
                self.pdf_links.append([link, filename_one, filename_two])
        if duplicate_count>0 and choice:
            self.pdf_links[index][1]=(str(self.pdf_links[index-1][1])+" - "+custom_string)
        elif duplicate_count > 0 and not choice:
            self.pdf_links[index][1]=(str(self.pdf_links[index][1])+" - 1")
        if len(self.pdf_links)>0:
            self.display_links()     
        else: 
            self.output_text.insert(customtkinter.END,("\nNo PDFs were found on this URL\n"))
            self.output_text.see("end")
            self.change_widget_state("normal")

    def display_links(self):
        
     
        for i, link in enumerate(self.pdf_links, start=1):
           
            pdf_link=link[0] if "http" in link[0] else urljoin(self.url,link[0]['href'])
            self.output_text.insert(customtkinter.END, ("\nFile {}: {}\n".format(i, pdf_link)))

            
            if link[1]==link[2]:
                self.output_text.insert(customtkinter.END,("Filename: {} \n".format(link[1])))
                self.filename_equal = True
            else:
                self.output_text.insert(customtkinter.END,("Filename Option 1: {} \n".format(link[1])))
                self.output_text.insert(customtkinter.END,("Filename Option 2: {} \n".format(link[2])))
                self.filename_equal = False
            self.output_text.see("end")
            
       
       
            
            
            
        if not self.waiting_for_result:
            self.change_widget_state("normal")
             
        
            
            
        
        self.output_text.insert(customtkinter.END,("\nTotal of {} PDF(s) found on this URL\n".format(len(self.pdf_links))))
        self.output_text.see("end")
        self.waiting_for_result = False
    def download_button_event(self):
      
        if len(self.pdf_links) < 1:
            self.search_url_button_event(True)
            return
        if self.url != self.url_entry.get():
            self.search_url_button_event(True)
            return
        if not self.range_is_valid():
            self.change_widget_state("normal")
            messagebox.showerror("PDF Scraper","Please enter a valid range")
            
            return

        if not self.valid_directory(self.folder_entry.get()):
            self.change_widget_state("normal")
            return
        if not self.filename_equal:
            self.naming_choice = tkinter.messagebox.askyesnocancel("PDF Scraper", "The files will be named according to option 1. Press No for option 2.")
        else:
            self.naming_choice=True
        if self.naming_choice is None:
            self.output_text.insert(customtkinter.END, "Operation cancelled by user\n")
            self.output_text.see("end")
            self.change_widget_state("normal")
            return
        self.change_widget_state("disabled")
        if self.range_is_valid():
            self.lower_range = int(self.lower_range_entry.get()) if self.lower_range_entry.get() else 1
            self.upper_range = int(self.upper_range_entry.get()) if self.upper_range_entry.get() else len(self.pdf_links)
        else:
            self.change_widget_state("normal")
            messagebox.showerror("PDF Scraper", "Please enter a valid range")
            return
        self.download_thread=threading.Thread(target=self.download_pdf)
        self.download_thread.start()
    
    
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
                self.change_widget_state("normal")
                return
            if self.naming_choice: 
                filename = pdf_link[1]
            else:
                filename = pdf_link[2]
            
                
          
            if not os.path.exists(folder_location):Path(folder_location).mkdir(parents=True, exist_ok=True)
            file_location = os.path.join(folder_location, filename+".pdf") 
            self.output_text.insert(customtkinter.END,("\nFile {}: {}\n".format(i, filename)))
            if os.path.exists(file_location):
                self.output_text.insert(customtkinter.END,("File skipped as already downloaded\n"))
                self.output_text.see("end")
                continue
            delete_file=False
            self.output_text.insert(customtkinter.END,("Downloading...\n"))
            self.output_text.see("end")
            with open(file_location, "wb") as pdf:
                try:
                    self.output_text.see("end")
                    pdf.write((requests.get(pdf_link[0]['href'])).content)
                    self.output_text.insert(customtkinter.END,("Successfully Downloaded\n"))
                    self.output_text.see("end")
                    success_count+=1
                except:
                    
                    try:
                        pdf.write(requests.get(urljoin(self.url_entry.get(),pdf_link[0]['href'])).content)
                        self.output_text.insert(customtkinter.END,("Sucessfully Downloaded\n"))
                        self.output_text.see("end")
                        success_count+=1
                    except:
                        self.output_text.insert(customtkinter.END,("Download Failed\n"))
                        self.output_text.see("end")
                        delete_file=True
            if delete_file:
                try:
                    os.unlink(file_location)
                except:
                    self.output_text.insert(customtkinter.END,("Failed to delete file {}\n".format(filename)))
                    self.output_text.see("end")
        
        if success_count==len(self.pdf_links):
            self.output_text.insert(customtkinter.END,("\nAll {} PDF files successfully downloaded to {}\n".format(success_count, folder_location)))  
        elif success_count == (self.upper_range - self.lower_range)+1:
            self.output_text.insert(customtkinter.END,("\nAll {} PDF files within the range {} - {} downloaded to {}\n".format(success_count, self.lower_range, self.upper_range, folder_location)))
        else:
            self.output_text.insert(customtkinter.END, "\n{} / {} PDF files downloaded\n".format(success_count, len(self.pdf_links)))
       
        self.output_text.see("end")
        self.change_widget_state("normal")
        self.cancel_button.configure(state="disabled")

    def cancel_download(self):
        self.download_cancel_raised = True
    def change_widget_state(self, state):
        self.download_button.configure(state=state)
        self.search_button.configure(state=state) 
        self.lower_range_entry.configure(state=state)
        self.upper_range_entry.configure(state=state)
        self.url_entry.configure(state=state)
        self.folder_button.configure(state=state)
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
        
        elif not self.is_path_exists_or_creatable(directory):
            self.output_text.insert(customtkinter.END, "Invalid Directory provided by user\n")
            self.output_text.see("end")
            return False
        
        return True 

    def is_pathname_valid(self, pathname: str) -> bool:
        '''
        `True` if the passed pathname is a valid pathname for the current OS;
        `False` otherwise.
        '''
        # If this pathname is either not a string or is but is empty, this pathname
        # is invalid.
        try:
            if not isinstance(pathname, str) or not pathname:
                return False

            # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
            # if any. Since Windows prohibits path components from containing `:`
            # characters, failing to strip this `:`-suffixed prefix would
            # erroneously invalidate all valid absolute Windows pathnames.
            _, pathname = os.path.splitdrive(pathname)

            # Directory guaranteed to exist. If the current OS is Windows, this is
            # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
            # environment variable); else, the typical root directory.
            root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
                if sys.platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

            # Append a path separator to this directory if needed.
            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

            # Test whether each path component split from this pathname is valid or
            # not, ignoring non-existent and non-readable path components.
            for pathname_part in pathname.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)
                # If an OS-specific exception is raised, its error code
                # indicates whether this pathname is valid or not. Unless this
                # is the case, this exception implies an ignorable kernel or
                # filesystem complaint (e.g., path not found or inaccessible).
                #
                # Only the following exceptions indicate invalid pathnames:
                #
                # * Instances of the Windows-specific "WindowsError" class
                #   defining the "winerror" attribute whose value is
                #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
                #   fine-grained and hence useful than the generic "errno"
                #   attribute. When a too-long pathname is passed, for example,
                #   "errno" is "ENOENT" (i.e., no such file or directory) rather
                #   than "ENAMETOOLONG" (i.e., file name too long).
                # * Instances of the cross-platform "OSError" class defining the
                #   generic "errno" attribute whose value is either:
                #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
                #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == ERROR_INVALID_NAME:
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        return False
        # If a "TypeError" exception was raised, it almost certainly has the
        # error message "embedded NUL character" indicating an invalid pathname.
        except TypeError as exc:
            return False
        # If no exception was raised, all path components and hence this
        # pathname itself are valid. (Praise be to the curmudgeonly python.)
        else:
            return True
        # If any other exception was raised, this is an unrelated fatal issue
        # (e.g., a bug). Permit this exception to unwind the call stack.
        #
        # Did we mention this should be shipped with Python already?
    def is_path_creatable(self, pathname: str) -> bool:
        '''
        `True` if the current user has sufficient permissions to create the passed
        pathname; `False` otherwise.
        '''
        # Parent directory of the passed path. If empty, we substitute the current
        # working directory (CWD) instead.
        dirname = os.path.dirname(pathname) or os.getcwd()
        return os.access(dirname, os.W_OK)
    def is_path_exists_or_creatable(self, pathname: str) -> bool:
        
        '''
        `True` if the passed pathname is a valid pathname for the current OS _and_
        either currently exists or is hypothetically creatable; `False` otherwise.

        This function is guaranteed to _never_ raise exceptions.
        '''
        
        try:
            # To prevent "os" module calls from raising undesirable exceptions on
            # invalid pathnames, is_pathname_valid() is explicitly called first.
            return self.is_pathname_valid(pathname)
            return is_pathname_valid(pathname) and (
                os.path.exists(pathname) or is_path_creatable(pathname))
        # Report failure on non-fatal filesystem complaints (e.g., connection
        # timeouts, permissions issues) implying this path to be inaccessible. All
        # other exceptions are unrelated fatal issues and should not be caught here.
        except OSError:
            return False
        

#-------------------------------------------------------------


if __name__ == "__main__":
    PDFScraper = App()




