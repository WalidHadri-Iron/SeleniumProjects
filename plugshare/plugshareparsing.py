from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from tqdm import tqdm

#For installing any library just type in pip install name-library
# pip install selenium
#pip install tqdm

DRIVER_PATH = r"C:\geckodriver.exe"
#This is where you have your driver, I used Firefox, you can use Chrome if you want to, but you have to download its driver too

def get_info_row(location, index_station, DRIVER_PATH):
    """
    This function extract info for a single station
    Location: String could be an address or city or country, anything that you can type in the bar search of the website
    
    index_station: When you look for an adress, a number of stations pop off, they are in a list, give an index starting from zero, if index_station
    is out of range, a message is shown
    
    If you have a good connection, you can reduce time sleep
    """
    seen = []
    driver = webdriver.Firefox(executable_path=DRIVER_PATH)
    #Use this with the Chrome
    #     driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    df_plugs = pd.read_excel('ActivePlugs.xlsx')
    plugs = list(df_plugs[df_plugs.Status==1]['Plug'])
    driver.get("https://www.plugshare.com/")
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/md-dialog/md-dialog-content[2]/button/md-icon")))
    driver.find_element_by_xpath("/html/body/div[7]/md-dialog/md-dialog-content[2]/button/md-icon").click()
    #     time.sleep(0.8)
    #     wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div[3]/div[12]/button[2]")))
    #     driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div[3]/div[12]/button[2]").click()
    time.sleep(1)
    location = "Duluth Supercharger"
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input-0")))
    inputLocation = driver.find_element_by_id("input-0")
    inputLocation.send_keys(location)
    inputLocation.send_keys(u'\ue007')
    time.sleep(1)
    #     nbr_charging = int(driver.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[3]/div[6]/div[2]/button[1]/span[1]').text)
    driver.refresh()

    js_string = "var element = document.getElementById(\"nav\");element.remove();"
    driver.execute_script(js_string)
    #     js_string = "var element = document.getElementById(\"search\");element.remove();"
    #     driver.execute_script(js_string)
    #     js_string = "var element = document.getElementById(\"quick-filters\");element.remove();"
    #     driver.execute_script(js_string)
    #     js_string = "var element = document.getElementById(\"menu\");element.remove();"
    #     driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"markers\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"traffic\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"map-types\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"zoom-in\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"zoom-out\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"my-location\");element.remove();"
    driver.execute_script(js_string)
    js_string = "var element = document.getElementById(\"menu\");element.remove();"
    driver.execute_script(js_string)
    # driver.find_element_by_xpath('//*[@id="menu-button"]').click()
    time.sleep(4)
    choices = driver.find_elements_by_xpath("//div[contains(@style,'width: 32px; height: 44px')]")
    row = {'Station_Name':"", 'Address':"",'latitude':0,"longitude":0, 'Phone_number':"", 'Parking':"","Stations":0, 'Amenities':[], 'Payment':"", 'Open_hours':"",'location_description':"","Power Level":"",'PlugScore':"","Supercharger":0,"CSS/SAE":0,"CHAdeMO":0,"J-1772":0,"Tesla":0,
                "Tesla (Roadster)":0,"Type 2":0,"Type 3":0,"Three Phase":0, "Caravan Mains Socket":0, "Wall":0}


   
    try:
        ActionChains(driver).move_to_element(choices[index_station]).click().perform()
    except:
        print('Out of index')

    url_refresh = driver.current_url.split("/")[-1]
    start = time.time()
    end = time.time()
    while url_refresh == "" and end-start<10:
        url_refresh = driver.current_url.split("/")[-1]
        end = time.time()
    if url_refresh=="":
        print('Not clickable')
        driver.close()
    station_id = int(driver.current_url.split("/")[-1])
    if station_id in seen:
        print('Station already seen')
        driver.close()
    seen.append(station_id)
    row['Station_id'] = station_id
    station_name=""
    start = time.time()
    end = time.time()

    while station_name=="" and end-start<10:
        station_name = driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div[1]/md-content/div/div/div[6]/div[2]/div/h1").text
        end = time.time()
    if station_name=="":
        print('Not able to extract station')
        driver.close()
    row['Station_Name'] = station_name 
    a = driver.find_elements_by_class_name("information")[0]
    
    try:
        address = a.find_element_by_css_selector("[ng-show='maps.location.address || (maps.location.latitude && maps.location.longitude)']").find_element_by_class_name("content").text
        row['Address'] = address
    except:
        print("Address missing")
        pass
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div[1]/md-card[1]/div[2]/div[3]/div[2]/a[2]')))
        latlon = a.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[1]/md-card[1]/div[2]/div[3]/div[2]/a[2]').get_attribute("href")[27:].split(',')
        lat = float(latlon[0].split('/')[-1])
        lon = float(latlon[1])
        row['latitude'] = lat
        row['longitude'] = lon
    except:
        print("Longitude Latitude Missing")
    try:
        phone_number = a.find_element_by_css_selector("[ng-show='maps.location.phone']").find_element_by_class_name("content").text
        row['Phone_number'] = phone_number
    except:
        print("Phone Number missing")
        pass
    try:
        parking = a.find_element_by_css_selector("[ng-show='maps.location.parking_type_name || maps.location.parking_attributes.length']").find_element_by_class_name("content").text.split(":")[-1][1:]
        row['Parking'] = parking
    except:
        print("Parking info missing")
        pass

    try:
        amenities = a.find_element_by_css_selector("[ng-show='maps.location.amenities.length > 0']").find_element_by_class_name("content").text.split(', ')
        row['Amenities'] = amenities 
    except:
        print("Amenities info missing")
        pass
    try:
        payment = a.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div[1]/md-card[1]/div[2]/div[5]/div[2]").text.split('\n')
        row['Payment'] = payment
    except:
        print("Payment Info missing")
        pass
    try:
        open_hours = a.find_element_by_css_selector("[ng-show='maps.location.hours || maps.location.open247']").find_element_by_class_name("content").text
        row['Open_hours'] = open_hours
    except:
        print("Open Hours Info missing")
        pass
    try:
        location_description = a.find_element_by_css_selector("[ng-show='maps.location.description']").find_element_by_class_name("content").text
        row['location_description'] = location_description
    except:
        print("Location Description Missing")
        pass
    try:
        plug_score = a.find_element_by_xpath('//*[@id="plugscore"]').text
        row['PlugScore'] = plug_score
    except:
        print("Location Description Missing")
        pass
    try:
        power_level = driver.find_element_by_css_selector("div.plug-power").text
        
        row['Power Level'] = power_level
    except:
        print("Power Level Missing")
        pass

    try:
        b = driver.find_element_by_id('connectors').find_elements_by_css_selector("[ng-repeat='connector in maps.location.connectors']")
        for i in range(len(b)):
            plug_name = b[i].find_element_by_css_selector("[class='plug-name ng-binding']").text
            station_number = int(b[i].find_element_by_css_selector("[class='station-count ng-binding']").text.split(" ")[0])
            if plug_name in plugs:
                row[plug_name] = station_number
                row['Stations'] = station_number
            else:
                row["Wall"] = station_number
                row['Stations'] = station_number
    except:
        print("Plug information missing")
    driver.close()
    return row

out = []
seen = []
# out where we store all the rows parsed
# seen where we store the id of already seen stations, so we don't process them again
nbr_stations_to_visit = 200 #How many stations you want
nbr_stations_seen = 0
start_index = 0 #where to start in the list rendered
pbar = tqdm(total = nbr_stations_to_visit+1)
i=0
while nbr_stations_seen<=nbr_stations_to_visit:
    result = get_info_row("Australia", start_index + i, DRIVER_PATH)
    if (result != -1) and result:
        nbr_stations_seen+=1
        out.append(result)
        data = pd.DataFrame(out)
        data.to_csv("out.csv", index=False,sep=",")
        pbar.update(1)

    i+=1
