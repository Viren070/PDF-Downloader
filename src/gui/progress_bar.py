import customtkinter
from time import perf_counter
from tkinter import messagebox
class ProgressBar(customtkinter.CTkFrame):
    def __init__(self, master, title, total, units=""):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.cancel_raised = False
        self.title = title
        self.start_time = perf_counter()
        self.units = units
        self.master = master
        self.total = total
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.time_during_cancel = 0
        self.downloaded_files = 0
        self._create_widgets()
    def _create_widgets(self):
        self.download_name = customtkinter.CTkLabel(self, text=self.title)
        self.download_name.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.progress_label = customtkinter.CTkLabel(self, text=f"0 MB / 0 MB")
        self.progress_label.grid(row=1, column=0, sticky="W", padx=10)

        self._progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate")
        self._progress_bar.grid(row=2, column=0, columnspan=6,
                               padx=(10, 45), pady=5, sticky="EW")
        self._progress_bar.set(0)

        self.percentage_complete = customtkinter.CTkLabel(self, text="0%")
        self.percentage_complete.grid(row=2, column=5, sticky="E", padx=10)

        self.download_speed_label = customtkinter.CTkLabel(self, text="0 MB/s")
        self.download_speed_label.grid(row=1, column=5, sticky="E", padx=10)

        
        self._total_progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate")
        
        self._total_progress_bar.set(0)
        
        self._total_percentage_complete = customtkinter.CTkLabel(self, text="0%")
       
        
        self._total_progress_label = customtkinter.CTkLabel(self, text=f"0 MB / {self.total_bytes} MB")
        
        
        self.install_status_label = customtkinter.CTkLabel(
            self, text="Status: Downloading")
        self.install_status_label.grid(
            row=5, column=0, sticky="W", padx=10, pady=5)
        
        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.raise_cancel)
        self.cancel_button.grid(row=5, column=5, padx=10, pady=5, sticky="E")
        
    def show_second_bar(self):
        self._total_progress_bar.grid(row=4, column=0, columnspan=6,
                               padx=(10, 45), pady=5, sticky="EW")
        self._total_progress_label.grid(row=3, column=0, sticky="W", padx=10)
        self._total_percentage_complete.grid(row=4, column=5, sticky="E", padx=10)
    def update_progress(self, value):
        self._progress_bar.set(value)
        self.percentage_complete.configure(text=f"{str(value*100).split('.')[0]}%")
        
    def update_total_progress(self, value):
        self._total_progress_bar.set(value)
        self._total_percentage_complete.configure(text=f"{str(value*100).split('.')[0]}%")
        
    def update_status(self, text):
        self.install_status_label.configure(text=text)
    def update_title(self, title):
        self.download_name.configure(text=title)
    def update_progress_label(self, text):

        self.progress_label.configure(text=text)
    def update_total_progress_label(self, bytes):
        self._total_progress_label.configure(text=f"{bytes} MB / {(self.total_bytes/1024/1024):.1f} MB")
    def get(self):
        return self._progress_bar.get()
    
    def complete_downloads(self):
        self.destroy()

    def update_speed(self, speed):
        self.download_speed_label.configure(text=f"{speed} MB/s")
        
    def raise_cancel(self):
        self.cancel_raised = True