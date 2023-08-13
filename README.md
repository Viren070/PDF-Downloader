
# PDF Downloader
A Python program to download PDFs off websites using a GUI made with customtkinter

## How it works
You enter a URL and click search. You can then open the File Selector (or just click download all and be prompted for a download folder [not added yet though]). 

The File Selector allows you to select which files you want to edit and you can use the search bar at the top to search through the PDFs that were found on that URL. e.g. if you searched as-pure, only the PDFs that had that in either their original filenames or link will be showm. These can be selected and edited in batch. 

When you are done selecting which files you want to download and have changed the download folder and filenames, you can click download. A progress bar will show up and it will tell you the download speeds and percentage complete. It will also tell you how much time is left until the download finishes (not added yet)

### How to use the File Selector
- You can use the File selector to select specific PDF files and edit the file name and download folder for the files you have selected.
- You can double click the file name entry box and this will open the PDF file on a new tab on your default browser 
- You can shift click on the checkboxes to quickly select within a certain range
- You can use the select/deselect all checkbox at the top (This only applies to currently shown rows, any rows you selected before and are not currently showing due to a search, for example, will not be selected/deselected
- You can use the browse button at the top or the option menu next to filename to quickly edit the filenames and download folders for the PDF files you have selected (or all if none were selected)
- If you have files with the same names and are to be downloaded to the same folder, one will overwrite the others.
- Option 1 gets the file name from what the website has named the pdf on their website whereas option 2 gets the filename from the text of the button that links to the pdf file.
- For example on the [Maths Genie A-Level Resources](https://www.mathsgenie.co.uk/newalevel.html) wesbite.  The first file is titled `Algebraic Expressions` (option 2) but when you click that link it takes you to `as-pure-algebraic-expressions.pdf` (option 1)

## Videos 


### Basic Usage
- This will download all the files to a folder called Downloads which will be located wherever the app was run from.
- Any duplicate filenames will be adjusted so they are not overwritten

https://github.com/Viren070/PDF-Downloader/assets/71220264/863f2084-cccc-4d14-b376-e4df8257b8bb


### Using the File Selector


- In this video, I take advantage of the URL for each PDF File. The worksheets made for the newer spec and for Year 1 content have `Integration-1/Set-B` in their URL and those made for the older spec and year 2 content  have `Integration-2/Set-A`.
- I change the download folders of the files according to their specification and whether it was made for year 1 content or year 2 content. When I click download, the files are downloaded to the folders I set beforehand 
  
https://github.com/Viren070/PDF-Downloader/assets/71220264/30eb1a4b-c70d-41b6-8e2c-6ddb62d8149f


