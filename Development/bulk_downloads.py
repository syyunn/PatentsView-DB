 coding: utf-8
from bs4 import BeautifulSoup
import urllib
from urllib.request  import urlretrieve
import requests
from zipfile import ZipFile
import os

def get_zip_url_year(page_url):

    ### a helper function
    ###  parse through each URL (for one year) to get the download links

    # open the link and parse through html tags
    page_open = requests.get(page_url)
    html_content = BeautifulSoup(page_open.content)

    # extract html elements with href tag
    href_tag = []
    for tag in html_content.find_all('a', href=True):
        if tag.text:
            href_tag.append(tag['href'])

    # keep only the links with .zip that are downloadable
    download_tag = [x for x in href_tag if '.zip' in x]
    download_url = []
    for tag in download_tag:
        download_url.append(page_url + '/' + tag)

    return download_url

def get_zip_url_all(page_url_lst):
    # get the downloadable zip file link for all the years
    zip_url_lst = []
    for url in page_url_lst:
        zip_url_lst += get_zip_url_year(url)

    return zip_url_lst


def get_date_url(zip_url_lst, date):

    # create a dictionary with date as key, download url as value
    time_url_dict = {}
    for url in zip_url_lst:
        # extract the time from url
        time = int('20' + url.split('/')[-1].split('.')[0][3:])
        # write in to the dictionary
        time_url_dict[time] = url

    # compare the date given by the user to get a list of url that needs to be downloaded
    url_list = []
    for d in time_url_dict.keys():
        if d >= date:
            url_list.append(time_url_dict[d])

    return sorted(url_list)

def extract_file(download_url):
    ### download the .zip file from a url, unzip it, and delete the .zip file(keep unzip files)

    # get the url to download to thew orking directory get the name of the file
    name = download_url.split('/')[-1]
    hdrs = urlretrieve(download_url, name)

    # unzip the file just downloaded
    zip_file = ZipFile(name)
    zip_file.extractall()
    zip_file.close()
    os.remove(name)


# In[12]:

def bulk_download(date):

    if len(date) != 8:
        raise ValueError('Please input a date in the form of "YYYYMMDD"')
    # get the year and date (converted to int) of the date a user input
    year = int(date[0:4])
    date = int(date)
    if date < 20050101:
        raise ValueError('Please input a date that is later than 2005/01/01')

    print("Starting downloading data...")

    # create a list of page URL's to parse through
    main_url = 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/'
    page_url_lst = []

    # get a list of url that is after the specified year
    for i in range(year, 2019):
        page_url_lst.append(main_url + str(i))

    # get all downloadable zip file link
    zip_url_lst =  get_zip_url_all(page_url_lst)
    # get the urls that need to be downloaded
    urls_to_download = get_date_url(zip_url_lst, date)

    for url in urls_to_download:
        extract_file(url)

    print("Download Finished")

if __name__== '__main__':
    folder = '/usr/local/airflow/raw_data'
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    bulk_download('20180801')