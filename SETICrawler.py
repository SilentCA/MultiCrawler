import requests
from bs4 import BeautifulSoup
from csv import writer
import sys
from requests.adapters import HTTPAdapter
#from fake_useragent import UserAgent
from multiprocessing import Pool

UIDs = range(10000, 20000)
N_PROCESS = 50
OUT_FILE_NAME = 'SETI_MUL_10000_20000.csv'

USERS_URL = 'https://setiathome.berkeley.edu/show_user.php?userid='
HOSTS_URL = 'https://setiathome.berkeley.edu/hosts_user.php?sort=rpc_time&rev=0&show_all=1&userid='
COLUMNS = ['User ID', 'SETI@home member since', 'Country', 'Total credit', 'Recent average credit', 'SETI@home classic workunits', 'SETI@home classic CPU time', '	Operating System', 'Last contact']
N_user_info = 6
N_host_info = 2

def GetSoup(url):
    #ua = UserAgent()
    #headers = { 'User-Agent':ua.random }
    proxies = {
      "http": None,
      "https": None,
    }
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=5))
    session.mount('https://', HTTPAdapter(max_retries=5))
    
    try:
        #strhtml = session.get(url, headers=headers, proxies=proxies, timeout=10)
        strhtml = session.get(url, proxies=proxies, timeout=10)
        soup = BeautifulSoup(strhtml.text, 'lxml')
        return(soup)
    except requests.exceptions.RequestException as e:
        print('Error! URL='+url)
        print(e)
        return(None)


def GetUserInfo(soup):
    data = []
    table = soup.find('table', attrs={'class':'table table-condensed table-striped'})
    if table == None:
        return([None]*N_user_info)
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    
    findindex = lambda self,i,value:sorted(self,key=lambda x:x[i]!=value)[0]
    row = []
    for column in COLUMNS[1:-N_host_info]:
        item = findindex(data, 0, column)
        if item[0] != COLUMNS[0]:
            row.append(item[1])
        else:
            row.append(None)

    return(row)

def CheckOS(host_soup):
    host_soup = host_soup.get_text()
    if 'Microsoft' in host_soup:
        if 'Linux' in host_soup:
            return('Both')
        else:
            return('MS Windows')
    else:
        if 'Linux' in host_soup:
            return('Linux')
        else:
            return('Other')

def GetHostInfo(soup):
    last_date = soup.select('body > div > div > table > tr:nth-child(2) > td:nth-child(9)')
    if len(last_date) == 0:
        return([None, None]) 
    else:
        return([CheckOS(soup), last_date[0].get_text()])

def GetInfo(uid):
    user_url = USERS_URL+str(uid)
    host_url = HOSTS_URL+str(uid)
    user_soup = GetSoup(user_url)
    if user_soup == None:
        return [None]
    user_info = GetUserInfo(user_soup)

    if user_info[0]==None or user_info[2]=='0':#no record or total credit = 0
        return(user_info+[None]*N_host_info)
    else:    
        host_soup = GetSoup(host_url)
        host_info = GetHostInfo(host_soup)
        return(user_info+host_info)

def CollectData_it(uid):    
    #print('current uid: '+str(uid))
    info = [uid] + GetInfo(uid)
    return(info)

def CreateFile(file_name):
    columns = COLUMNS
    with open(file_name, 'w', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(columns)

def setcallback(x):
    if x[1] == None: #no record
        print(x[0])
    else:
        with open(OUT_FILE_NAME, 'a+', newline='', encoding="utf-8") as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(x)
        print(x[0])

if __name__ == '__main__':

    pool = Pool(processes=N_PROCESS)
    for i in UIDs:
        pool.apply_async(CollectData_it, args=(i,), callback=setcallback)
    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()  # 主进程阻塞等待子进程的退出


    


    


