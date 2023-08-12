import customtkinter
from urllib.parse import urlparse
import webbrowser
from parser.pdf_parser import get_pdfs
from gui.file_selector import FileSelector
from tkinter import messagebox
from threading import Thread
import os
from PIL import Image
class URLSelector(customtkinter.CTk):
    def __init__(self, image_path):
        super().__init__()
        self.title("PDF Downloader")
        self.image_path = image_path
        self.file_selector = None
        self.pdfs = None
        self.download_in_progress = False
        self.resizable(False, False)
        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
       
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(padx=50, pady=50, sticky="nsew")
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)      
       
       
        title_frame = customtkinter.CTkFrame(self.main_frame)
        title_frame.grid(row=0, column=0, sticky="nsew")

        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_rowconfigure(0, weight=1)    
        

        self.title_label = customtkinter.CTkLabel(title_frame, text="PDF Downloader v1.0.2", font=customtkinter.CTkFont(size=24, family="Helvetica", weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10)

        self.author_label = customtkinter.CTkLabel(title_frame, text="Viren070 on GitHub", cursor="hand2", text_color="blue", font=customtkinter.CTkFont(family="Helvetica", size=15, underline=True))
        self.author_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Viren070"))
        self.author_label.grid(row=1, column=0, padx=10, pady=10)

        url_entry_frame = customtkinter.CTkFrame(self.main_frame)
        url_entry_frame.grid(row=1, column=0, pady=10)

        
        
        self.search_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(self.image_path, "search_light.png")),
                                                     dark_image=Image.open(os.path.join(self.image_path, "search_dark.png")), size=(20, 20))

        self.url_entry = customtkinter.CTkEntry(url_entry_frame, width=400, placeholder_text="Enter URL")
        self.search_button = customtkinter.CTkButton(url_entry_frame, width=40, image=self.search_image, text="", command=self.search_url_wrapper)

        self.url_entry.grid(padx=10, pady=10, row=0, column=0, sticky="ew")
        self.search_button.grid(padx=10, pady=10, row=0, column=1, sticky="e")
        
        self.button_frame = customtkinter.CTkFrame(self.main_frame)
        self.button_frame.grid(row=2, column=0, padx=20, pady=10)
        
        self.file_selector_button = customtkinter.CTkButton(self.button_frame, text="Open File Selector", width=200, command=self.open_file_selector)
        self.download_all_button = customtkinter.CTkButton(self.button_frame, text="Download All", state="disabled", width=200, command=self.download_all_event)
        
        self.file_selector_button.grid(row=0, column=1, padx=10, pady=10)
        self.download_all_button.grid(row=0, column=0, padx=10, pady=10)
        

    def search_url_wrapper(self):
        if self.download_in_progress:
            messagebox.showinfo("Search", "Please wait until the download has finished or cancel it")
            return
        self.search_button.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.download_all_button.configure(state="disabled")
        if self.url_is_valid(self.url_entry.get()):
            Thread(target=self.search_url, args=(self.url_entry.get(),)).start()
        else:
            messagebox.showerror("PDF Downloader", "The URL you have entered appears to be invalid")
            self.search_button.configure(state="normal")
            self.url_entry.configure(state="normal")
    def search_url(self, url):
   
        pdfs = get_pdfs(url)
        
        
        if pdfs is None:
            self.search_button.configure(state="normal")
            self.url_entry.configure(state="normal")
            return
        if not pdfs:
            self.search_button.configure(state="normal")
            self.url_entry.configure(state="normal")
            messagebox.showinfo("PDF Downloader", "No PDFs were found on that URL")
            return
        self.pdfs = pdfs
        self.download_all_button.configure(state="normal")
        Thread(target=self.create_file_selector, args=(url, pdfs, self.image_path)).start()
        messagebox.showinfo("PDF Downloader", f"{len(pdfs)} PDF Files were found at the specified URL.")
        
    def create_file_selector(self, *args):
        self.file_selector_button.configure(state="disabled", width=200, text="Initialising File Selector...")
        self.file_selector=FileSelector(self, *args)
        self.file_selector_button.configure(state="normal", width=200, text="Open File Selector")
        self.url_entry.configure(state="normal")
        self.search_button.configure(state="normal")
    
    def open_file_selector(self):
        if self.download_in_progress:
            messagebox.showinfo("E", "Please wait until the download has completed or cancel the download")
            return
        if not self.file_selector == None:
            self.file_selector.show_table()
            self.file_selector_button.configure(state="disabled")
        else:
            messagebox.showerror("PDF Downloader", "Please enter a valid URL with PDFs and click the search button")
    
    def url_is_valid(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def download_all_event(self):
        if self.download_in_progress:
            messagebox.showerror("Error", "There is already a download in progress")
            return
        self.download_all_button.configure(state="disabled")
        Thread(target=self.download_all).start()
    def download_all(self):
        FileSelector.download_selected_pdfs(self, self.pdfs, True, self.main_frame)