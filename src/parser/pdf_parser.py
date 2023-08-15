import re
from tkinter import messagebox
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def get_pdfs(url):     
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    } 
    try:        
        response=requests.get(url, headers=headers)   
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        messagebox.showerror("PDF Downloader", "Could not connect to URL, check your connection and try again.")
        return None   
    except requests.exceptions.RequestException as error:
        messagebox.showerror("PDF Downloader", f"Could not connect to URL\n\n{error}")
        return None  
    pdf_links = []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if (href and href.endswith('.pdf')) and not(link.get('href', []) in [link[0] for link in pdf_links]):
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

def get_more_pdfs(base_url, progress_bar):     
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    headers = {'User-Agent': user_agent}
    
    try:        
        response = requests.get(base_url, headers=headers, allow_redirects=True)   
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Error: Could not connect to URL. Check your connection and try again.")
        return None   
    except requests.exceptions.RequestException as error:
        messagebox.showerror("Error", f"Could not connect to URL\n\n{error}")
        return None  
    
    pdf_links = []
    soup = BeautifulSoup(response.content, 'html.parser')
    anchor_tags = soup.find_all('a')
    count=0
    for anchor_tag in anchor_tags:
        print(f"{count}/{len(anchor_tags)}")
        progress_bar.set(count/len(anchor_tags))
        href = anchor_tag.get('href')
        if not href:
            count+=1
            continue
        
        # Clean the href to handle relative URLs
        clean_href = href.replace("\\", "").replace('"', '')
        href_parse_result = urlparse(clean_href)
        if not all([href_parse_result.scheme, href_parse_result.netloc]):
            clean_href = urljoin(base_url, clean_href)
        try:
            if (clean_href in [link[0] for link in pdf_links]):
                count+=1
                continue
            link_response = requests.head(clean_href, headers=headers, allow_redirects=True)
            if link_response.status_code == 200 and link_response.headers.get('content-type', '').endswith('pdf'):
                filename_description = re.sub('<[^>]+>', '', str(anchor_tag))
                filename = link_response.url.split('/')[-1].split('.pdf')[-2]
                
                pdf_links.append([link_response.url, filename, filename_description])
        except requests.exceptions.RequestException:
            pass
        count+=1
        progress_bar.set(count/len(anchor_tags))
    return pdf_links