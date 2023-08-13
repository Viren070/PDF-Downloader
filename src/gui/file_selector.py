import os
import re
import webbrowser
from functools import partial
from threading import Thread
from time import perf_counter
from tkinter import filedialog, messagebox, ttk

import customtkinter
from PIL import Image
from requests.exceptions import RequestException

from downloader.downloader import PDF, AbortDownload, FileDownloadError
from gui.progress_bar import ProgressBar
from utils.paths import is_path_exists_or_creatable


class FileSelector(customtkinter.CTkToplevel):
    def __init__(self, master, url, pdfs, image_path):
        super().__init__()
        self.withdraw()
        self.master = master
        self.resizable(False, False)
        self.url = url
        self.pdfs = pdfs
        self.selected_pdfs = [] 
        self.shift_clicks = []
        self.image_path = image_path
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
        self.final_info = {}
        pdf_objects = []
        self.updating_current_widgets = False
        self.batch_update_in_progress = False
        self.initialising_table = True
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.create_widgets()
    
        
        

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.widget_dict = {}
        self.table_frame_wrapper = customtkinter.CTkFrame(self, width=1000, height=700, corner_radius=20)
        self.table_frame_wrapper.grid(padx=10, pady=10)
        
        #self.table_frame_wrapper.grid_propagate(False)
        
        
        
        
        
        self.search_frame = customtkinter.CTkFrame(self.table_frame_wrapper, corner_radius=20)
        self.search_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="w")
        self.search_image =  customtkinter.CTkImage(light_image=Image.open(os.path.join(self.image_path, "search_light.png")),
                                                     dark_image=Image.open(os.path.join(self.image_path, "search_dark.png")), size=(20, 20))
        self.search_entry = customtkinter.CTkEntry(self.search_frame, placeholder_text="Search URL/Filename")
        self.search_button = customtkinter.CTkButton(self.search_frame, width=50, image=self.search_image, text="", state="disabled", command=self.search_button_event)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)
        self.search_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.actions_frame = customtkinter.CTkFrame(self.table_frame_wrapper, corner_radius=20)
        self.actions_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.actions_frame.grid_rowconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        
        center_frame = customtkinter.CTkFrame(self.actions_frame)
        center_frame.grid(row=0, column=0, padx=10, pady=10)

        self.download_button = customtkinter.CTkButton(center_frame, width=300, text="Download", state="disabled", command=self.download_button_event)
        self.reset_button = customtkinter.CTkButton(center_frame, width=300, text="Reset", state="disabled", command=self.reset_window)
        self.download_button.grid(row=0, column=1, padx=10, pady=10)
        self.reset_button.grid(row=0, column=0, padx=10, pady=10)
        
        
        self.search_progress_bar = customtkinter.CTkProgressBar(self.master.button_frame, width=400)
        self.table_frame = customtkinter.CTkScrollableFrame(self.table_frame_wrapper,width=720, height=400, corner_radius=20)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20)
        self.create_table()
        
    def create_table(self, filename_or_url_contains=None, id_to_add=None):
        self.initialising_table = True
        self.widget_dict = {}
        self.search_progress_bar.set(0)
        self.search_progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=10, columnspan=2)
        self.table_frame = customtkinter.CTkScrollableFrame(self.table_frame_wrapper,width=720, height=400, corner_radius=20)
        headers = ["ID", "Filename", "Download Location"]
        separator_column = 1
        data_column=0
        header_start = perf_counter()
        for header in (headers):
            frame=customtkinter.CTkFrame(self.table_frame)
            frame.grid(row=0, column=data_column,padx=10,pady=10)
            customtkinter.CTkLabel(frame, text=header, width=20, font=customtkinter.CTkFont(size=15, weight="bold")).grid(row=0, column=0,padx=10,pady=10)
            if header=="Filename":
                customtkinter.CTkOptionMenu(frame, width=100, values=["Option 1", "Option 2"], command=lambda value: self.change_filename(value, "All")).grid(row=0, column=1, padx=10, pady=10)
            elif header=="Download Location":
                customtkinter.CTkButton(frame, width=100, text="Browse", command=lambda: self.update_file_dest("All")).grid(row=0, column=1, padx=10, pady=10)
            ttk.Separator(self.table_frame, orient="vertical").grid(row=0, column=separator_column, sticky="sn", rowspan=1000)
            separator_column+=2
            data_column+=2
        print(f"Took {(perf_counter() - header_start):.2f} To create headers")
        self.all_checkbox = customtkinter.CTkCheckBox(self.table_frame, text="", width=25, height=25, onvalue=1, offvalue=0, command=self.select_all_event)
        self.all_checkbox.grid(row=0, padx=10, column=data_column)
        
        # Add data rows
        separator_row = 1
        data_row=2
        for index, pdf in enumerate(self.pdfs):
            row_start = perf_counter()
            pdf_id = index
            search_start = perf_counter()
            if filename_or_url_contains:
                if not (filename_or_url_contains in pdf[1] or filename_or_url_contains in pdf[2] or filename_or_url_contains in pdf[0]):
                    self.search_progress_bar.set((index+1)/len(self.pdfs))
                    continue
            #print(f"Took {(perf_counter()-search_start):.2f} to search")
            widget_start = perf_counter()
            
            varstart=perf_counter()
            filename_var = customtkinter.StringVar()
            file_dest_var = customtkinter.StringVar()
            checkbox_var = customtkinter.BooleanVar()
            filename_var.set(pdf[1])
            filename_var.trace_add('write', callback=self.update_final_info)
            file_dest_var.set(str(os.path.join(os.getcwd(), "Downloads")))
            file_dest_var.trace_add('write', callback=self.update_final_info)
            #print(f"Took {(perf_counter() - varstart):.2f}s to create variables")
            # Widgets
            
            #  ID Column
            idstart=perf_counter()
            customtkinter.CTkLabel(self.table_frame, text=str(pdf_id)).grid(row=data_row, column=0, padx=10, pady=10)
            #print(f"Took {(perf_counter() - idstart):.2f}s to create id column")
            
            #  Filename Column
            fstart = perf_counter()
            filename_entry = customtkinter.CTkEntry(self.table_frame, textvariable=filename_var, width=200)
            filename_entry.grid(row=data_row, column=2,padx=10,pady=10)
            filename_entry.bind('<Double-1>', command=lambda event, link=pdf[0]: webbrowser.open_new_tab(link))
            #print(f"Took {(perf_counter() - fstart):.2f}s to create filename column")
            
            #  Download Folder Column
            dstart = perf_counter()
            file_dest_frame = customtkinter.CTkFrame(self.table_frame)
            file_dest_frame.grid(row=data_row, column=4,padx=10,pady=10)
            file_dest_entry=customtkinter.CTkEntry(file_dest_frame, textvariable=file_dest_var, width=200)
            file_dest_entry.grid(row=0, column=0, padx=10, sticky="ew")
            customtkinter.CTkButton(file_dest_frame, width=100, text="Browse", command=lambda pdf_id=pdf_id: self.update_file_dest(pdf_id)).grid(row=0, column=1, padx=2, pady=10, sticky="ew")
            #print(f"Took {(perf_counter() - dstart):.2f}s to create download folder column")
       
            
            #  Checkbox Column
            checkbox_start = perf_counter()
            checkbox_widget = customtkinter.CTkCheckBox(self.table_frame, text="", command=self.update_all_checkbox, variable=checkbox_var,width=25, height=25)
            checkbox_widget.grid(row=data_row, column=6, padx=10)
            #checkbox_widget.bind("<Button-1>", partial(self.shift_click_multi_select, pdf_id=pdf_id)) # use partial to send event and correct pdf_id
            checkbox_widget.bind("<Button-1>", command=lambda event, pdf_id=pdf_id: self.shift_click_multi_select(event, pdf_id))
            #print(f"Took {(perf_counter() - checkbox_start):.2f}s to create checkbox column")
            
            #  Row Separator
            sep_start = perf_counter()
            ttk.Separator(self.table_frame, orient='horizontal').grid(row=separator_row, sticky="ew", columnspan= 1000)
            #print(f"Took {(perf_counter() - sep_start):.2f}s to create separator")
            
            #print(f"Took {(perf_counter() - widget_start):.2f} to create widgets")
            
            row_dict = {
                "id": pdf_id,
                "filename": filename_var,
                "download_folder": file_dest_var,
                "checkbox": checkbox_var,
                "link": pdf[0]
            }
            self.widget_dict.update({pdf_id: row_dict})
            separator_row,data_row = separator_row+2, data_row+2
            self.search_progress_bar.set((index+1)/len(self.pdfs))
            #print(f"Took {(perf_counter()-row_start):.2f} to create row")
        self.initialising_table = False
        self.search_progress_bar.grid_forget()
    def shift_click_multi_select(self, event, pdf_id):
        if event.state & 1: # check if shift was held during click
            if len(self.shift_clicks) == 2:
                self.shift_clicks = []
                self.shift_clicks.append(pdf_id)
            elif len(self.shift_clicks) == 1:
                self.shift_clicks.append(pdf_id)
                Thread(target=self.select_pdfs, args=((self.shift_clicks[0], self.shift_clicks[1]),)).start()
                #self.select_pdfs((self.shift_clicks[0], self.shift_clicks[1]))
            elif len(self.shift_clicks) == 0:
                self.shift_clicks.append(pdf_id)
            else:
                self.shift_clicks = []
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
            
    def select_pdfs(self, ids, value=None):
        if ids is None or not self.selected_pdfs:
            return 
        if isinstance(ids, int):
            if value == None:
                value = not self.widget_dict[ids]["checkbox"].get()
            # Handles passing start_id and end_id
            self.widget_dict[ids]["checkbox"].set(value)
            if value and ids not in self.selected_pdfs:
                self.selected_pdfs.append(ids)
            elif value==False and ids in self.selected_pdfs:
   
                self.selected_pdfs.remove(ids)

        elif isinstance(ids, list): 
            for pdf_id in ids:
                if value == None:
                    value = not self.widget_dict[pdf_id]["checkbox"].get()
                try:
                    self.widget_dict[pdf_id]["checkbox"].set(value)
                except KeyError:
                    pass
                if value and pdf_id not in self.selected_pdfs:
                    self.selected_pdfs.append(pdf_id)
                elif value==False and pdf_id in self.selected_pdfs:
                    self.selected_pdfs.remove(pdf_id)
               
                
               
        elif isinstance(ids, tuple):
            if not len(ids) == 2:
                raise ValueError
            start_id = ids[0]
            end_id = ids[1]
            if start_id > end_id:
                start_id, end_id = end_id, start_id
            ids = list(range(start_id, end_id+1))
            for pdf_id in ids:
                if pdf_id==start_id or pdf_id==end_id:
                    value=self.widget_dict[pdf_id]["checkbox"].get()
                else:
                    value=None
                self.select_pdfs(pdf_id, value)
        else:
            # Invalid input type, just return
            raise TypeError(f"Expected int, list or tuple, instead got {type(ids)}")
            
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
    def select_all_event(self):
        Thread(target=self.select_all).start()
        
    def select_all(self):
        value = self.all_checkbox.get()
        if value == 0:
            value = False
        elif value == 1:
            value = True
        else:
            return
        for pdf_id, pdf_entry in self.widget_dict.items():
            pdf_entry["checkbox"].set(value)
            
            if value and pdf_id not in self.selected_pdfs:
                self.selected_pdfs.append(pdf_id)
            elif value==False and pdf_id in self.selected_pdfs:
                self.selected_pdfs.remove(pdf_id)  
            self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
    def search_button_event(self):
        string_to_search = self.search_entry.get()
        self.search_button.configure(state="disabled")
        Thread(target=self.show_updated_table, args=(string_to_search, 1)).start()

    
    def update_all_checkbox(self):
        if self.all_checkbox.get() == 1 and len(self.get_selected_pdfs())!=len(self.pdfs):
            self.all_checkbox.deselect()
        elif self.all_checkbox.get() == 0 and len(self.get_selected_pdfs())==len(self.pdfs):
            self.all_checkbox.select()
        for pdf_id, entry in self.widget_dict.items():
            if entry["checkbox"].get() and pdf_id not in self.selected_pdfs:
                self.selected_pdfs.append(pdf_id)    
            elif entry["checkbox"].get() == False and pdf_id in self.selected_pdfs:
                self.selected_pdfs.remove(pdf_id) 
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
    
    def show_updated_table(self, *args):  
        self.iconify()
        self.withdraw()
        self.grab_release()
        self.master.deiconify()
        self.master.update()
        self.create_table(*args)
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
        self.select_pdfs(self.selected_pdfs, True)
        self.update_current_widgets()
        self.show_table()
    def show_table(self):
        
        
        self.table_frame.grid(row=1, column=0, padx=20, pady=20)
        self.search_button.configure(state="normal")
        self.reset_button.configure(state="normal")
        self.download_button.configure(state="normal")
        if not self.final_info:
            self.update_final_info()
        self.update()
        self.deiconify()
        self.grab_set()
    def update_file_dest(self, pdf_id, value=None):
        if value is None:
            new_dest = filedialog.askdirectory(parent=self)
            if new_dest is None or new_dest == "":
                return
            if pdf_id == "All":
                self.batch_update_in_progress = True
                for pdf_id, entry in self.widget_dict.items():
                    if self.selected_pdfs and pdf_id in self.selected_pdfs:
                        self.update_file_dest(pdf_id, new_dest)
                    elif not self.selected_pdfs:
                        self.update_file_dest(pdf_id, new_dest)
                self.batch_update_in_progress = False
            else:
                self.update_file_dest(pdf_id, new_dest)
        else:
            self.widget_dict[pdf_id]["download_folder"].set(value)
        self.update_final_info()
        
    def change_filename(self, value, pdf_id):
        if pdf_id == "All":
            self.batch_update_in_progress = True
            selected = self.get_selected_pdfs() if True else False
                
            for index, pdf in enumerate(self.pdfs):
                for pdf_id, entry in self.widget_dict.items():
                    if index != pdf_id:
                        continue
                    index = int(value.replace("Option ", ""))
                    if (selected and pdf_id in selected) or not selected:
                        entry["filename"].set(pdf[index])
            self.batch_update_in_progress = False
        self.update_final_info()
                    
    def get_selected_pdfs(self):
        result = []
        for pdf_id, entry in self.widget_dict.items():
            if entry["checkbox"].get():
                result.append(pdf_id)
        return result
    def update_final_info(self, *args):
        if self.updating_current_widgets:
            return
        if self.batch_update_in_progress:
            return
        if self.initialising_table:
            return
        info = self.final_info
        incorrect_paths = []
        incorrect_filenames = []
        
        for pdf_id, entry in self.widget_dict.items():
            suggested_filename = entry["filename"].get()
            suggested_folder = entry["download_folder"].get()
            if not is_path_exists_or_creatable(suggested_folder):
                incorrect_paths.append(pdf_id)
                continue
            if  re.search(r'[\\/:*?"<>|]', suggested_filename) or suggested_filename == "":
                incorrect_filenames.append(pdf_id)
                continue
            pdf_info = {
                "id": pdf_id,
                "filename": entry["filename"].get(),
                "download_folder": entry["download_folder"].get(),
                "link": entry["link"]
            }
            info.update({pdf_id:pdf_info})
            
            

        if (incorrect_paths or incorrect_filenames) and not self.initialising_table:
            error_message = ""
            if incorrect_paths:
                error_message += f"Invalid Paths for PDFs with ID: {', '.join(map(str, incorrect_paths))}\n"
            
            if incorrect_filenames:
                error_message += f"Invalid Filenames for PDFs with ID: {', '.join(map(str, incorrect_filenames))}"
            
            messagebox.showerror("Invalid Entries", error_message)
            self.update_current_widgets()
        self.final_info = info
    def update_current_widgets(self):
        self.updating_current_widgets = True
        if self.final_info is None or not self.final_info:
            self.updating_current_widgets = False
            return
        for pdf_id, entry in self.widget_dict.items():
            old_pdf_info = self.final_info[pdf_id]
            entry["filename"].set(old_pdf_info["filename"])
            entry["download_folder"].set(old_pdf_info["download_folder"])
        self.updating_current_widgets = False
    def reset_window(self):
        self.reset_button.configure(state="disabled")
        self.download_button.configure(state="disabled")
        self.final_info = {}
        self.selected_pdfs = []
        
        Thread(target=self.show_updated_table, args=("", 1)).start()

    
    def download_button_event(self):
        self.download_button.configure(state="disabled")
        if self.master.download_in_progress:
            messagebox.showerror("Error", "There is currently a download in progress, please cancel that or wait for it to finish")
            self.download_button.configure(state="normal")
            return
        if len(self.selected_pdfs) == 0:
            messagebox.showerror("Error", "You have not selected any PDFs to download. Please use the checkboxes.\nNote: There is a select/deselect all checkbox at the top and you can shift click the checkboxes to select within a range", master=self)
            self.download_button.configure(state="normal")
            return
        Thread(target=self.download_selected_pdfs).start()

    
    
    
    def download_selected_pdfs(self, pdfs_to_download=None, download_all=False, frame=None):
        if download_all:
            self.download_in_progress = True
        else:
            self.master.download_in_progress = True
        if not download_all and not self.final_info:
            self.update_final_info()
        failed_downloads = []
        selected_pdfs = self.selected_pdfs if pdfs_to_download is None else pdfs_to_download
        pdf_objects = []
        if not messagebox.askyesno("Confirmation", f"This will download {len(selected_pdfs)} PDF Files, are you sure you wish to continue"):
            if download_all:
                self.download_all_button.configure(state="normal")
            else:
                self.download_button.configure(state="normal")
            return
        if frame is None:
            frame = self.master.main_frame
        if download_all:
            self.download_in_progress = True
        else:
            self.master.download_in_progress = True
            self.grab_release()
            self.withdraw()
            self.master.grab_set()
        download_progress = ProgressBar(frame, "Getting PDF details", len(selected_pdfs))
        download_progress.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        download_progress.grid_propagate(False)
        count=0
        total_size_of_pdfs = 0
        download_progress.update_status("Status: Fetching File Details...")
        session_errors = []
        
        for num, pdf in enumerate(selected_pdfs, start=1):
            if download_progress.cancel_raised:
                break
            if not download_all:
                link = self.final_info[pdf]["link"]
                filename = self.final_info[pdf]["filename"]
                download_folder = self.final_info[pdf]["download_folder"]
            else:
                link=selected_pdfs[num-1][0]
                filename = selected_pdfs[num-1][1]
                download_folder = os.path.join(os.getcwd(), "Downloads")
            pdf_id = pdf
            pdf_obj = PDF(pdf_id, filename, link, download_folder)
            try:
                pdf_obj.create_session()
                if pdf_obj.filesize is not None:
                    total_size_of_pdfs += pdf_obj.filesize
                pdf_objects.append(pdf_obj)
                
            except RequestException as error:
                session_errors.append(filename)
                if not pdf_id in failed_downloads:
                    failed_downloads.append(pdf_id)
                download_progress.total -= 1
                messagebox.showerror("Error", error)
                
            if download_progress.total == 0:
                messagebox.showerror("Error", "Unable to connect to any PDF url, aborting download.", master=self)
                download_progress.destroy()
                pdf_objects = []
                
                if download_all:
                    self.download_in_progress = False
                    self.download_all_button.configure(state="normal")
                else:
                    self.master.download_in_progress = False
                    self.download_button.configure(state="normal")
                return
            download_progress.update_progress_label(f"{num} PDFs / {len(selected_pdfs)} PDFs")
            download_progress.update_progress(num/len(selected_pdfs))
        if session_errors:
            messagebox.showerror("Requests Error", f"Failed to establish connection to URL and create stream for {len(session_errors)} PDF Files.", master=self)
        download_progress.total_bytes = total_size_of_pdfs
        download_progress.update_progress(0)
        download_progress.update_status("Status: Downloading Files")
        download_progress.update_total_progress_label("0")
        download_progress.show_second_bar()
        download_progress.start_time = perf_counter()
        for pdf in pdf_objects:
            download_progress.update_title(f"{pdf.filename} - {count+1}/{download_progress.total}")
            try:
                pdf.download_pdf(download_progress)
                count+=1
            except PermissionError:
                messagebox.showerror("PermissionError", f"PDF with filename {pdf.filename} failed to download due to a permission error. Please ensure you have permission to write in {pdf.download_folder}", master=self)
                if not pdf.pdf_id in failed_downloads:
                    failed_downloads.append(pdf.pdf_id)
            except FileDownloadError as Error:
                messagebox.showerror("Download Error", f"Could not download {pdf.filename}: {Error}", master=self)
                if not pdf.pdf_id in failed_downloads:
                    failed_downloads.append(pdf.pdf_id)
            except AbortDownload as error:
                messagebox.showinfo("Cancel", error)
                break
            except Exception as error:
                messagebox.showerror("Error", f"An unknown error has occured while attempting to download {pdf.filename}\nFull Error: {error}", master=self)
                if not pdf.pdf_id in failed_downloads:
                    failed_downloads.append(pdf.pdf_id)
                
        
        messagebox.showinfo("Downloads", f"{count}/{download_progress.total} PDF Files with total file size of {(download_progress.downloaded_bytes/1024/1024):.1f} MB were downloaded successfully.", master=self)
        download_progress.complete_downloads()
        pdf_objects = []
        if failed_downloads and messagebox.askyesno("Retry?", f"You have {len(failed_downloads)} PDF Files that failed to download, would you like to try downloading these files again?"):
            if download_all:
                self.download_all(self, failed_downloads, True, self.main_frame)
            else:
                self.download_selected_pdfs(failed_downloads)
        if download_all:
            self.download_all_button.configure(state="normal")
            self.download_in_progress = False
        else:
            self.download_button.configure(state="normal")
            self.master.download_in_progress = False
            self.update()
            self.deiconify()
            self.grab_set()
        
            

    def quit(self):
        self.master.file_selector = None 
        self.master.file_selector_button.configure(state="normal")
        self.withdraw()
        self.iconify()
        self.master.deiconify()
        self.destroy()
