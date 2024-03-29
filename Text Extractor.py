#!/usr/bin/env python
# coding: utf-8

# # INSERT CREDITS TO BRIAN #

# In[ ]:


# Web scraping imports
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from joblib import delayed, Parallel
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk

# This warning ignore is in place because the "requests.get" is unverified.
# TODO: Find ways to securely make a request
import warnings
warnings.filterwarnings("ignore")


# In[ ]:


# Function for all article text
def open_unknown_csv(file_in, delimination):
    encode_index = 0
    encoders = ['utf_8', 'latin1', 'utf_16',
                'ascii', 'big5', 'big5hkscs', 'cp037', 'cp424',
                'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
                'cp850', 'cp852', 'cp855', 'cp856', 'cp857',
                'cp858', 'cp860', 'cp861', 'cp862', 'cp863',
                'cp864', 'cp865', 'cp866', 'cp869', 'cp874',
                'cp875', 'cp932', 'cp949', 'cp950', 'cp1006',
                'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252',
                'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
                'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr',
                'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
                'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4',
                'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9',
                'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15',
                'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic',
                'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
                'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32',
                'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le',
                'utf_7', 'utf_8', 'utf_8_sig']

    data = open_file(file_in, encoders[encode_index], delimination)
    encoder = encoders[encode_index]
    while type(data) == str:
        print("Encoder error: " + encoders[encode_index])
        if encode_index < len(encoders) - 1:
            encode_index = encode_index + 1
            try:
                print("Trying encoder: " + encoders[encode_index])
                data = open_file(file_in, encoders[encode_index], delimination)
            except:
                continue
            print("")
            encoder = encoders[encode_index]
        else:
            print("Can't find appropriate encoder")
            input("Program Terminated. Press Enter to continue...")
            exit()

    return data

def scrape_urls_text(url):
    text = ''

    # Handling non-URLs
    if url == None or type(url) == float:
        print("No URL provided")
        return 'Invalid URL or Non-existant URL'

    # Retrieving text from HTML tags
    try:
        # Handling incorrectly formatted URLs
        if 'http' not in url[:5] and 'www.' in url:
            url = 'https://' + url

        html = requests.get(url, verify=False, timeout=(5, 5))

        if html.status_code != 200:
            if 'https' in url:
                html = requests.get('http' + url[5:], verify=False, timeout=(5,5))
                if html.status_code != 200:
                    raise
            else:
                raise

        soup = BeautifulSoup(html.content, 'html.parser')
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.body.get_text(separator=' ')
        tex = re.sub('[^a-zA-Z0-9 \n\.]', '', text) # removing additional characters
        text = ' '.join([s for s in str(tex).split() if len(s)<15]) # only accept valid words

    # Catch for timeout or retry errors due to proxy
    except:
        print("Failure: ", url)
        return 'Unable to access website'

    return text

def extract_text(urls):
    # Actual web scraping!

    # First extracting samsung-specific urls
    print("Extracting text from all URLs...")
    grabbed_text = Parallel(n_jobs=-1)        (delayed(scrape_urls_text)(url)
         for url in urls)
    print("Extraction complete!")

    return grabbed_text

def open_file(file_in, encoder, delimination):
    try:
        data = pd.read_csv(file_in, low_memory=False, encoding=encoder, delimiter=delimination)
        print("Opened file using encoder: " + encoder)

    except UnicodeDecodeError:
        print("Encoder Error for: " + encoder)
        return "Encode Error"
    return data


# In[ ]:


print("Program: Text Extractor")
print("Release: 0.0.1")
print("Date: 2019-12-09")
print("Author: David Liau")
print()
print()
print("This program extracts all text from a given list of websites using Beautiful Soup.")
print("Credit to Brian Neely (github.com/neelybd) for supplying multiple help functions.")
print()
print()


# Hide Tkinter GUI
Tk().withdraw()

# Find input file
print("Select File in")
file_in = askopenfilename(initialdir="../", title="Select input file",
                          filetypes=(("Comma Separated Values", "*.csv"), ("all files", "*.*")))
if not file_in:
    input("Program Terminated. Press Enter to continue...")
    exit()

# Set output file
print("Select File out")
file_out = asksaveasfilename(initialdir=file_in, title="Select output file",
                             filetypes=(("Comma Separated Values", "*.csv"), ("all files", "*.*")))
if '.' not in file_out[-4:]:
    file_out = file_out + '.csv'

if not file_out:
    input("Program Terminated. Press Enter to continue...")
    exit()

# Identify CSV Encoding
data = open_unknown_csv(file_in, ",")

data['Text'] = extract_text(data.iloc[:,0])

# output = pd.DataFrame(text, columns=['Text'])
output = data

# Write CSV
print("Writing CSV File...")
output.to_csv(file_out, index=False)
print("Wrote CSV File!")


# In[ ]:
