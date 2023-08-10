from gui.url_selector import URLSelector
import os
if __name__ == "__main__":
    url_selector = URLSelector(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images"))

#pyinstaller --noconfirm --onefile --windowed --name "PDF Downloader" --distpath ./dist/%version --workpath ./build --add-data "C:/Users/viren/AppData/Local/Programs/Python/Python311/Lib/site-packages/customtkinter;customtkinter/" --add-data "C:\Users\viren\Documents\School\Computer Science\PDF Downloader\PDF-Downloader\images;images" "C:\Users\viren\Documents\School\Computer Science\PDF Downloader\PDF-Downloader\main.py"