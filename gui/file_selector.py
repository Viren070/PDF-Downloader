import os
import webbrowser
from functools import partial
from threading import Thread
from tkinter import ttk, filedialog
import customtkinter
from gui.progress_bar import ProgressBar
from downloader.downloader import download_pdf, download_pdf_alt
from time import perf_counter
from PIL import Image
class FileSelector(customtkinter.CTkToplevel):
    def __init__(self, master, url, pdfs, image_path):
        super().__init__()
        #self.withdraw()
        self.master = master
        self.url = url
        self.pdfs = pdfs
        self.selected_pdfs = [] 
        self.shift_clicks = []
        self.image_path = image_path
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
        self.final_info = {}
        self.create_widgets()
        
        self.grab_set()
        

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.widget_dict = {}
        self.table_frame_wrapper = customtkinter.CTkFrame(self, width=1000, height=700, corner_radius=20)
        self.table_frame_wrapper.grid(padx=10, pady=10)
        
        #self.table_frame_wrapper.grid_propagate(False)
        
        
        
        
        
        self.search_frame = customtkinter.CTkFrame(self.table_frame_wrapper, corner_radius=20)
        self.search_frame.grid(row=0, column=0, padx=20, sticky="w")
        self.search_image =  customtkinter.CTkImage(light_image=Image.open(os.path.join(self.image_path, "search_light.png")),
                                                     dark_image=Image.open(os.path.join(self.image_path, "search_dark.png")), size=(20, 20))
        self.search_entry = customtkinter.CTkEntry(self.search_frame, placeholder_text="Search URL/Filename")
        self.search_button = customtkinter.CTkButton(self.search_frame, width=100, image=self.search_image, text="", state="disabled", command=self.search_button_event)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)
        self.search_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.actions_frame = customtkinter.CTkFrame(self.table_frame_wrapper, corner_radius=20)
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.actions_frame.grid_rowconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        
        center_frame = customtkinter.CTkFrame(self.actions_frame)
        center_frame.grid(row=0, column=0, padx=10, pady=10)

        self.download_button = customtkinter.CTkButton(center_frame, width=300, text="Download", state="disabled", command=self.download_button_event)
        self.reset_button = customtkinter.CTkButton(center_frame, width=300, text="Reset", state="disabled", command=self.reset_window)
        self.download_button.grid(row=0, column=1, padx=10, pady=10)
        self.reset_button.grid(row=0, column=0, padx=10, pady=10)
        
        
        self.search_progress_bar = customtkinter.CTkProgressBar(self.table_frame_wrapper, width=400)
        self.search_progress_bar.grid(row=0, column=0, sticky="ew", padx=(320, 10))
        self.table_frame = customtkinter.CTkScrollableFrame(self.table_frame_wrapper,width=720, height=400, corner_radius=20)
        self.table_frame.grid(row=1, column=0, padx=20, pady=20)
        self.create_table()
        
    def create_table(self, filename_or_url_contains=None, id_to_add=None):
        self.widget_dict = {}
        self.table_frame = customtkinter.CTkScrollableFrame(self.table_frame_wrapper,width=720, height=400, corner_radius=20)
        headers = ["ID", "Filename", "Download Location"]
        separator_column = 1
        data_column=0
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
        
        self.all_checkbox = customtkinter.CTkCheckBox(self.table_frame, text="", width=25, height=25, onvalue=1, offvalue=0, command=self.select_all)
        self.all_checkbox.grid(row=0, padx=10, column=data_column)
        
        # Add data rows
        separator_row = 1
        data_row=2
        for index, pdf in enumerate(self.pdfs):
            pdf_id = index
            if filename_or_url_contains:
                if not (filename_or_url_contains in pdf[1] or filename_or_url_contains in pdf[2] or filename_or_url_contains in pdf[0]):
                    self.search_progress_bar.set((index+1)/len(self.pdfs))
                    continue
           
            customtkinter.CTkLabel(self.table_frame, text=str(pdf_id)).grid(row=data_row, column=0, padx=10, pady=10)
            # Filename Column
            filename_var = customtkinter.StringVar()
            filename_var.set(pdf[1])
            filename_var.trace_add('write', self.update_final_info)
            filename_entry = customtkinter.CTkEntry(self.table_frame, textvariable=filename_var, width=200)
            filename_entry.grid(row=data_row, column=2,padx=10,pady=10)
            filename_entry.bind('<Double-1>', command=lambda event, link=pdf[0]: webbrowser.open_new_tab(link))
            # File Destination Column
            file_dest_var = customtkinter.StringVar()
            file_dest_var.set(str(os.path.join(os.getcwd(), "Downloads")))
            file_dest_frame = customtkinter.CTkFrame(self.table_frame)
            file_dest_frame.grid(row=data_row, column=4,padx=10,pady=10)
            file_dest_entry=customtkinter.CTkEntry(file_dest_frame, textvariable=file_dest_var, width=200)
            file_dest_entry.grid(row=0, column=0, padx=10, sticky="ew")
            
            customtkinter.CTkButton(file_dest_frame, width=100, text="Browse", command=lambda pdf_id=pdf_id: self.update_file_dest(pdf_id)).grid(row=0, column=1, padx=2, pady=10, sticky="ew")
           
            # Checkbox 
            
            checkbox_var = customtkinter.BooleanVar()
            checkbox_widget = customtkinter.CTkCheckBox(self.table_frame, text="", command=self.update_all_checkbox, variable=checkbox_var,width=25, height=25)
            checkbox_widget.grid(row=data_row, column=6, padx=10)
            checkbox_widget.bind("<Button-1>", partial(self.shift_click_multi_select, pdf_id=pdf_id)) # use partial to send event and correct pdf_id
            ttk.Separator(self.table_frame, orient='horizontal').grid(row=separator_row, sticky="ew", columnspan= 1000)
            
            
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
    def shift_click_multi_select(self, event, pdf_id):
        if event.state & 1: # check if shift was held during click
            if len(self.shift_clicks) == 2:
                self.shift_clicks = []
                self.shift_clicks.append(pdf_id)
            elif len(self.shift_clicks) == 1:
                self.shift_clicks.append(pdf_id)
                self.select_pdfs((self.shift_clicks[0], self.shift_clicks[1]))
            elif len(self.shift_clicks) == 0:
                self.shift_clicks.append(pdf_id)
            else:
                self.shift_clicks = []
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
            
    def select_pdfs(self, ids, value=None):
        
        if ids is None:
            return 
        if isinstance(ids, int):
            if value == None:
                value = not self.widget_dict[ids]["checkbox"].get()
            # Handles passing start_id and end_id
            self.widget_dict[ids]["checkbox"].set(value)
            if value and ids not in self.selected_pdfs:
                print(f"Adding pdf with id {ids} to array")
                self.selected_pdfs.append(ids)
            elif value==False and ids in self.selected_pdfs:
                print(f"Removing pdf with id {ids} from array")
                self.selected_pdfs.remove(ids)

        elif isinstance(ids, list): 
            print(f"Received id list of \n\n{ids}\n\nwith value of {value}")
            for pdf_id in ids:
                if value == None:
                    value = not self.widget_dict[pdf_id]["checkbox"].get()
                try:
                    self.widget_dict[pdf_id]["checkbox"].set(value)
                except KeyError:
                    pass
                if value and pdf_id not in self.selected_pdfs:
                    print(f"Adding pdf with id {pdf_id} to array")
                    self.selected_pdfs.append(pdf_id)
                elif value==False and pdf_id in self.selected_pdfs:
                    print(f"Removing pdf with id {pdf_id} from array")
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
            raise TypeError
            
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
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
                print(f"Adding pdf with id  {pdf_id} to self.selected_pdfs")
                self.selected_pdfs.append(pdf_id)
            elif value==False and pdf_id in self.selected_pdfs:
                self.selected_pdfs.remove(pdf_id)  
                print(f"Removing pdf with id  {pdf_id} from self.selected_pdfs")
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
    def search_button_event(self):
        string_to_search = self.search_entry.get()
        self.search_button.configure(state="disabled", text="Searching...")
        Thread(target=self.show_updated_table, args=(string_to_search, 1)).start()

    
    def update_all_checkbox(self):
        if self.all_checkbox.get() == 1 and len(self.get_selected_pdfs())!=len(self.pdfs):
            self.all_checkbox.deselect()
        elif self.all_checkbox.get() == 0 and len(self.get_selected_pdfs())==len(self.pdfs):
            self.all_checkbox.select()
        for pdf_id, entry in self.widget_dict.items():
            if entry["checkbox"].get() and pdf_id not in self.selected_pdfs:
                print(f"Adding pdf with id  {pdf_id} to self.selected_pdfs")
                self.selected_pdfs.append(pdf_id)    
            elif entry["checkbox"].get() == False and pdf_id in self.selected_pdfs:
                print(f"Removing pdf with id  {pdf_id} from self.selected_pdfs")
                self.selected_pdfs.remove(pdf_id) 
        self.title(f"File Selector {len(self.selected_pdfs)}/{len(self.pdfs)} Selected")
    
    def show_updated_table(self, *args):  
        self.create_table(*args)
        self.select_pdfs(self.selected_pdfs, True)
        self.update_current_widgets()
        self.show_table()
    def show_table(self):
        self.deiconify()
        self.update()
        self.table_frame.grid(row=1, column=0, padx=20, pady=20)
        self.update_final_info()
        self.search_button.configure(state="normal", text="Search")
        self.reset_button.configure(state="normal")
        self.download_button.configure(state="normal")
    
    def update_file_dest(self, pdf_id, value=None):
        if value is None:
            new_dest = filedialog.askdirectory(parent=self)
            if pdf_id == "All":
                for pdf_id, entry in self.widget_dict.items():
                    self.update_file_dest(pdf_id, new_dest)
            else:
                self.update_file_dest(pdf_id, new_dest)
        else:
            self.widget_dict[pdf_id]["download_folder"].set(value)

        self.update_final_info()
    def change_filename(self, value, pdf_id):
        if pdf_id == "All":
            selected = self.get_selected_pdfs() if True else False
                
            for index, pdf in enumerate(self.pdfs):
                for pdf_id, entry in self.widget_dict.items():
                    if index != pdf_id:
                        continue
                    index = int(value.replace("Option ", ""))
                    if (selected and pdf_id in selected) or not selected:
                        entry["filename"].set(pdf[index])
        self.update_final_info()
                    
    def get_selected_pdfs(self):
        result = []
        for pdf_id, entry in self.widget_dict.items():
            if entry["checkbox"].get():
                result.append(pdf_id)
        return result
    def update_final_info(self, *args):
        info = self.final_info
        for pdf_id, entry in self.widget_dict.items():
            pdf_info = {
                "id": pdf_id,
                "filename": entry["filename"].get(),
                "download_folder": entry["download_folder"].get(),
                "link": entry["link"]
            }
            info.update({pdf_id:pdf_info})
        self.final_info = info
    def update_current_widgets(self):
        if self.final_info is None or not self.final_info:
            return
        for pdf_id, entry in self.widget_dict.items():
            old_pdf_info = self.final_info[pdf_id]
            entry["filename"].set(old_pdf_info["filename"])
            entry["download_folder"].set(old_pdf_info["download_folder"])
    def reset_window(self):
        self.reset_button.configure(state="disabled")
        self.download_button.configure(state="disabled")
        self.final_info = None 
        self.selected_pdfs = None 
        Thread(target=self.show_updated_table, args=("", 1)).start()
        self.select_pdfs((0, len(self.pdfs)), False)
    
    
    def download_button_event(self):
        Thread(target=self.download_selected_pdfs).start()
    
    
    
    
    def download_selected_pdfs(self):
        download_progress = ProgressBar(self.table_frame_wrapper, "Downloading Selected PDFs", len(self.selected_pdfs))
        download_progress.grid(row=4, column=0, sticky="ew")
        count=0
        for pdf in self.selected_pdfs:
            print(f"will download pdf with id - {pdf} and with info of {self.final_info[pdf]}")
            link = self.final_info[pdf]["link"]
            filename = self.final_info[pdf]["filename"]
            download_folder = self.final_info[pdf]["download_folder"]
            start = perf_counter()
            download_pdf(link, filename, download_folder)
            print(f"Took {perf_counter() - start}s with M1")
            
            start = perf_counter()
            download_pdf_alt(link, filename, download_folder)
            print(f"Took {perf_counter() - start}s with M2")
            count+=1
            download_progress.update_progress(count/download_progress.total)
            
            