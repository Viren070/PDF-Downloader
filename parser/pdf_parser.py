import customtkinter
import requests
from bs4 import BeautifulSoup
from tkinter import messagebox
import re
from urllib.parse import urljoin


def get_pdfs(url):      
    try:        
        response=requests.get(url)   
    except requests.exceptions.ConnectionError:
        messagebox.showerror("PDF Downloader", "Could not connect to URL")
        return None   
    pdf_links = []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        if ('.pdf' in link.get('href', [])) and not(link.get('href', []) in [link[0] for link in pdf_links]):
            filename_two=re.sub('<[^>]+>', '', str(link))
            filename_one=link['href'].split('/')[-1].split('.pdf')[-2] 
            pdf_links.append([urljoin(url,link.get('href')), filename_one, filename_two])
    return pdf_links