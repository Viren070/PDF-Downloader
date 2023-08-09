import customtkinter
from time import perf_counter
class ProgressBar(customtkinter.CTkFrame):
    def __init__(self, master, title, total, units=""):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.cancel_download_raised = False
        self.title = title
        self.start_time = perf_counter()
        self.units = units
        self.master = master
        self.total = total
        self.time_during_cancel = 0
        self._create_widgets()
    def _create_widgets(self):
        self.download_name = customtkinter.CTkLabel(self, text=self.title)
        self.download_name.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.progress_label = customtkinter.CTkLabel(self, text=f"0 {self.units} / 0 {self.units}")
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

        self.install_status_label = customtkinter.CTkLabel(
            self, text="Status: ")
        self.install_status_label.grid(
            row=3, column=0, sticky="W", padx=10, pady=5)

        self.eta_label = customtkinter.CTkLabel(
            self, text="Time Left: 00:00:00")
        self.eta_label.grid(row=0, column=5, sticky="E", pady=5, padx=10)
    def update_progress(self, value):
        self._progress_bar.set(value)
    def update_status(self, text):
        self.install_status_label.configure(text=text)

        
