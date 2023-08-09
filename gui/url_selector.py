import customtkinter
from urllib.parse import urlparse
import webbrowser
from parser.pdf_parser import get_pdfs
from gui.file_selector import FileSelector
from tkinter import messagebox
from threading import Thread
import os
class URLSelector(customtkinter.CTk):
    def __init__(self, image_path):
        super().__init__()
        self.title("PDF Downloader")
        self._url_input = None
        self.create_widgets()
        self.image_path = image_path
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
        

        self.title_label = customtkinter.CTkLabel(title_frame, text="PDF Downloader v2.0", font=customtkinter.CTkFont(size=24, family="Helvetica", weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10)

        self.author_label = customtkinter.CTkLabel(title_frame, text="Viren070 on GitHub", cursor="hand2", text_color="blue", font=customtkinter.CTkFont(family="Helvetica", size=15, underline=True))
        self.author_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Viren070"))
        self.author_label.grid(row=1, column=0, padx=10, pady=10)

        url_entry_frame = customtkinter.CTkFrame(self.main_frame)
        url_entry_frame.grid(row=1, column=0, pady=20)

        url_entry_frame.grid_columnconfigure(0, weight=1)
        url_entry_frame.grid_columnconfigure(0, weight=0)

        self.url_entry = customtkinter.CTkEntry(url_entry_frame, width=400, placeholder_text="Enter URL")
        self.search_button = customtkinter.CTkButton(url_entry_frame, width=100, text="Search", command=self.search_url_wrapper)

        self.url_entry.grid(padx=10, pady=10, row=0, column=0, sticky="ew")
        self.search_button.grid(padx=10, pady=10, row=0, column=1, sticky="e")
        
        
        
        

    def search_url_wrapper(self):
        self.search_button.configure(text="Searching...", state="disabled")
        self.url_entry.configure(state="disabled")
        if self.url_is_valid(self.url_entry.get()):
            Thread(target=self.search_url, args=(self.url_entry.get(),)).start()
        else:
            messagebox.showerror("PDF Downloader", "The URL you have entered appears to be invalid")
            self.search_button.configure(text="Search", state="normal")
            self.url_entry.configure(state="normal")
    def search_url(self, url):
   
        pdfs = get_pdfs(url)
        
        
        if pdfs is None:
            self.search_button.configure(text="Search", state="normal")
            self.url_entry.configure(state="normal")
            return
        if not pdfs:
            self.search_button.configure(text="Search", state="normal")
            self.url_entry.configure(state="normal")
            messagebox.showinfo("PDF Downloader", "No PDFs were found on that URL")
            
        self.search_button.configure(text="Creating Table...")
        
        file_selector=FileSelector(self, url, pdfs, self.image_path)
        file_selector.show_table()
        self.url_entry.configure(state="normal")
        self.search_button.configure(text="Search", state="normal")
        
    def url_is_valid(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    
if __name__ == "__main__":
    app = URLSelector()