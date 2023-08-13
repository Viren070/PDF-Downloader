import re
from tkinter import messagebox
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


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
            linkk = link.get('href').replace("\\","").replace('"','')
            result=urlparse(linkk)
            if all([result.scheme, result.netloc]):
                pdf_url=linkk
            else:
                pdf_url =urljoin(url,link.get('href'))
                result=urlparse(pdf_url)
                if not all([result.scheme, result.netloc]):
                    messagebox.showerror("Error", f"Received: {link.get('href')} \nwith urljoin: {pdf_url}\nResult = False")
                    continue
            pdf_links.append([pdf_url, filename_one, filename_two])
    return pdf_links