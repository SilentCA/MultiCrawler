import requests
from bs4 import BeautifulSoup
from csv import writer
import sys
from requests.adapters import HTTPAdapter

USERS_URL = 'https://setiathome.berkeley.edu/show_user.php?userid='
HOSTS_URL = 'https://setiathome.berkeley.edu/hosts_user.php?sort=rpc_time&rev=0&show_all=1&userid='
COLUMNS = ['User ID', 'SETI@home member since', 'Country', 'Total credit', 'Recent average credit', 'SETI@home classic workunits', 'SETI@home classic CPU time', '	Operating System', 'Last contact']
N_user_info = 6
N_host_info = 2

def GetSoup(url):
    proxies = {
      "http": None,
      "https": None,
    }
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=5))
    session.mount('https://', HTTPAdapter(max_retries=5))
    
    try:
        strhtml = session.get(url, proxies=proxies, timeout=10)
        soup = BeautifulSoup(strhtml.text, 'lxml')
        return(soup)
    except:
        print('Error! URL='+url)
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
        return None
    user_info = GetUserInfo(user_soup)

    if user_info[0]==None:
        return(user_info+[None]*N_host_info)
    else:    
        host_soup = GetSoup(host_url)
        host_info = GetHostInfo(host_soup)
        return(user_info+host_info)

def CollectData(file_name, start, end):
    for uid in range(start, end+1):
        print('current uid: '+str(uid))
        info = [uid] + GetInfo(uid)
        if info[1] == None:
            continue
        print('writing......')
        with open(file_name, 'a+', newline='', encoding="utf-8") as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(info)

def CreateFile(file_name):
    columns = COLUMNS
    with open(file_name, 'w', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(columns)

if __name__ == '__main__':
    file_name = 'SETI_User_Stat.csv'
    is_new_file = 0
    start_id = 1
    end_id = 12000000

    input_str = input("start_id end_id is_new_file(0 or 1) file_name(ignore if use default)\nPlease input--> ")
    input_list = input_str.split()
    if len(input_list) != 3 & len(input_list) != 4:
        print("Input error! Expect 3 or 4 parameters")
        quit()
    
    start_id = int(input_list[0])
    end_id = int(input_list[1])
    is_new_file = int(input_list[2])
    if len(input_list) == 4:
        file_name = input_list[3]
    
    if(is_new_file==1):
        CreateFile(file_name)
    
    CollectData(file_name, start_id, end_id)
    
    """ file_name = sys.argv[2]
    if sys.argv[1] != '0':
        CreateFile(file_name)
    CollectData(file_name, int(sys.argv[3]), int(sys.argv[4])) """


    


    


