import requests
import re
import difflib
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
import numpy as np

def get_active_drivers_rr(url):
    page = requests.get(url)
    #get active drivers from table
    df = pd.read_html(page.text)[2]
    #filter to only cup drivers'
    df = df[df['Series'].str.contains("Cup")]
    #return list of drivers
    return df['Driver'].values.tolist()

def get_active_drivers_espn(url):
    page = requests.get(url)
    #get active drivers from table
    df = pd.read_html(page.text)[0]
    new_header = df.iloc[1] #grab the first row for the header
    df = df[2:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    #return list of drivers
    return df['NAME'].values.tolist()
    
def get_driver_page_rr(driver_name):
    #format name for internet page
    #A_J_Allmendinger = A.J. Allmendinger --> need to remove space and .
    #Kyle_Busch = Kyle Busch --> need to remove space
    #Martin_Truex_Jr = Martin Truex, Jr. --> need to remove space and , and .
    jr_string = ", Jr."
    initial_string = ". "
    if jr_string in driver_name:
        new_name = driver_name.replace(jr_string,"_Jr").replace(" ","_")
    elif initial_string in driver_name:
        new_name = driver_name.replace(initial_string,"_").replace(".","_") 
    else:
        new_name = driver_name.replace(" ","_")
    #return driver page url
    return f"https://www.racing-reference.info/driver/{new_name}/"

def get_driver_page_espn(driver_name):
    page = requests.get('https://www.espn.com/racing/drivers')
    soup = BeautifulSoup(page.content, 'html.parser')
    #match driver name from rr to espn and get that name
    driver_match = difflib.get_close_matches(driver_name,get_active_drivers_espn('https://www.espn.com/racing/drivers'))
    anchor_field = soup.find("a",text=driver_match[0])['href']
    return f"https://www.espn.com{anchor_field}"
  
def get_driver_age(driver_url): 
    page = requests.get(driver_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    date_field = soup.find("b",text="Born:")
    birthdate = datetime.strptime(date_field.next_sibling.strip(), '%b %d, %Y').date()
    today = date.today()
    #return age
    return today.year  - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
def get_driver_cup_table_rr(driver_url):
    page = requests.get(driver_url)
    #return driver table
    return pd.read_html(page.text)[5]
     
def get_driver_years_cup (df_driver):
    #return last row first col
    return df_driver.iloc[-1,0]
    
def get_driver_champs (df_driver):
    #return count of no1 = champs
    if 1 in df_driver['Rank'].values:
        return df_driver['Rank'].value_counts()[1]
    else:
        return 0

def get_driver_pole_count (df_driver):
    #return table value of poles
    return df_driver.iloc[-1,6]

def get_driver_win_count (df_driver):
    #return table value of poles
    return df_driver.iloc[-1,3]

def get_driver_tfive_count (df_driver):
    #return table value of poles
    return df_driver.iloc[-1,4]

def get_driver_tten_count (df_driver):
    #return table value of poles
    return df_driver.iloc[-1,5]

def get_driver_total_race_count (df_driver):
    #return table value of poles
    return df_driver.iloc[-1,2]

def get_espn_url_code (espn_url):
    match=re.search(r'_/id/\d+',espn_url)
    return match.group(0)

def get_espn_driver_year_df (espn_url,year):
    full_url = f'https://www.espn.com/racing/driver/raceresults/{espn_url}/year/{year}'
    page = requests.get(full_url)
    df = pd.read_html(page.text)[1]
    new_header = df.iloc[1] #grab the first row for the header
    df = df[2:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    return df

def get_driver_team (espn_url):
    page = requests.get(espn_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find("li",class_="last").text.strip().replace("Team: ","")

def clean_and_combine_df (df_list,year_list):
    j=0
    for i in df_list:
        df_list[i] = df_list[i].dropna(axis=1,how='all').copy()
        df_list[i].loc[:,'DATE'] = year_list[j] #how to get correct year
        #Make all Caps
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].str.upper().copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("NASCAR CUP SERIES AT ","",regex=True).copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("NASCAR CUP SERIES ","",regex=True).copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("MONSTER ENERGY ","",regex=True).copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("NASCAR SPRINT CUP SERIES AT ","",regex=True).copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("NASCAR NEXTEL CUP SERIES AT ","",regex=True).copy()
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace(" #","",regex=True).copy()
        #remove numbers from track
        df_list[i].loc[:,'RACE']=df_list[i]['RACE'].replace("\d+","",regex=True).copy()
        #convert cols to numeric
        df_list[i].loc[:,'PLACE'] = pd.to_numeric(df_list[i]["PLACE"],errors='coerce').copy()
        df_list[i].loc[:,'START'] = pd.to_numeric(df_list[i]["START"],errors='coerce').copy()
        df_list[i].loc[:,'LEAD'] = pd.to_numeric(df_list[i]["LEAD"],errors='coerce').copy()
        df_list[i].loc[:,'COMP'] = pd.to_numeric(df_list[i]["COMP"],errors='coerce').copy()
        df_list[i].loc[:,'PTS'] = pd.to_numeric(df_list[i]["PTS"],errors='coerce').copy()
        df_list[i].loc[:,'BONUS'] = pd.to_numeric(df_list[i]["BONUS"],errors='coerce').copy()
        df_list[i].loc[:,'PEN'] = pd.to_numeric(df_list[i]["PEN"],errors='coerce').copy()
        j+=1
    big_df=pd.concat(df_list)
    return big_df

def get_years_in_list(driver_years):
    if driver_years > 7:
        return np.arange(2022,2015,-1).tolist()
    else:
        return np.arange(2022,2022-driver_years,-1).tolist()
    
def get_list_of_df_espn (year_list,espn_url):
    d={}
    for year in year_list:
        d[year] = get_espn_driver_year_df(espn_url,year)
    return d
    
def get_perct_led(df_rr):
    df_rr['per']=(df_rr.loc[:,'Led']/df_rr.loc[:,'Laps'])*100
    return df_rr
        