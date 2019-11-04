from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time 
import json
import urllib
import datetime
import argparse

def date2name(date):
    return '{year}-{month}-{day}'.format(year=date.year, month=str(date.month).zfill(2), day=str(date.day).zfill(2))

def date2query(date):
    ds = '{year}/{month}/{day}'.format(year=date.year, month=str(date.month).zfill(2), day=str(date.day).zfill(2))
    return urllib.parse.quote(ds, safe='') + '+00%3A00%3A00'

def login(driver):
    driver.get('https://auig2.jaxa.jp/ips/home')
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'guestsearch'))
    )

    driver.execute_script('document.getElementById("guestsearch").click();')
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, '_sl_historyFrame'))
    )


def get_scenes(driver, target_date=date2query(datetime.datetime.now() - datetime.timedelta(days=1))):
    driver.execute_script('window.queryResult = null;')

    class getResult:
        def __call__(self, driver):
            value = driver.execute_script('return window.queryResult')
            if type(value) is str:
                return value
            else:
                return False

    script_get_scenes = """
    function get(url, query) {
        var xhr = new XMLHttpRequest();
        window.ttt = xhr;
        xhr.open("GET", url+ query);
        
        xhr.onload = function() {
            window.queryResult = this.responseText
        }
        xhr.send(null);
    }
                    
    var url = "https://auig2.jaxa.jp/arcgis_general/rest/services/palsar2/ImageServer/query"

    get(url, query)
    """
    script_query = "var query =\"?returnGeometry=true&spatialRel=esriSpatialRelIntersects&where=((((opemode+%3d+'SPT')))+or+(((opemode+%3d+'SM1')))+or+(((opemode+%3d+'SM2')))+or+(((opemode+%3d+'SM3')))+or+(((opemode+%3d+'WD1')))+or+(((opemode+%3d+'WD2'))))+and+(scenecenterdate+%3e%3d+'{start_date}'+and+scenecenterdate+%3c%3d+'{end_date}')+and+(deleteflag+%3d+0+or+deleteflag+is+null)+and+(privatediscloseflag+%3d+0+or+privatediscloseflag+is+null)    +and+(l0status+%3d+'NORMAL'+or+l0status+is+null)+and+((groundstationcode+in+('HEOC'%2c'TKSC'%2c'TDRS')+and+scenecenterdate+%3e%3d+'2014%2f08%2f04+00%3a00%3a00')+or+((groundstationcode+not+in+('HEOC'%2c'TKSC'%2c'TDRS')+or+groundstationcode+is+null)+and+scenecenterdate+%3e%3d+'2014%2f08%2f04+00%3a00%3a00'))&outSR=102100&outFields=objectid%2ccatalogid%2csensorname%2copemode%2csceneid%2cobspathno%2ccenterframeno%2corbitdatatype%2cobservationstartdate%2cobservationenddate%2csatellitename%2corbitdirection%2cobservationdirection%2coffnadirangle%2cpolarization%2ctablenumber%2cbeamno%2cpositionx%2cpositiony%2cpositionz%2cvelocityx%2cvelocityy%2cvelocityz%2cscenestartdate%2cscenestarttime%2cscenecenterdate%2cscenecentertime%2cscenecenterlat%2cscenecenterlong%2csceneupperleftlat%2csceneupperleftlong%2csceneupperrightlat%2csceneupperrightlong%2cscenelowerleftlat%2cscenelowerleftlong%2cscenelowerrightlat%2cscenelowerrightlong%2ccompressionmode%2cnoofpixels%2clineno%2cbitspixel%2csetpixel%2ctotalorbitno%2cdownlinksegno%2coperationsegmentid%2cgroundstationcode%2cyawsteeringflag%2cdatatransmissionrate%2curgentflag%2cnearrealflag%2cl0processingresultfilename%2cl0status%2cimagecatalogfilename%2cimagecatalogfilesize%2cimagecatalogprocessingdate%2cl0dataprocessing%2csceneidentificationid&f=json\"".format(start_date=target_date, end_date=target_date)

    driver.execute_script(script_query  + script_get_scenes)

    return WebDriverWait(driver, 200).until(
        getResult()
    )


def save(value, filename=date2name(datetime.datetime.now() - datetime.timedelta(days=1)) + '.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(value)
    
    

parser = argparse.ArgumentParser(description='search palsar2 scene information form AUIG2.') 
parser.add_argument('start_date', help='search from this day. ex: 2019-01-01')
parser.add_argument('end_date', help='search from this day. ex: 2019-01-31')

args = parser.parse_args() 
start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")

driver = webdriver.Ie()
login(driver)

temp_date = start_date
while temp_date < end_date:
    value = get_scenes(driver, temp_date)

    print('start: {}'.format(date2name(temp_date)))
    try:
        data = json.loads(value)
        l = len(data['features'])
        if l >= 5000:
            raise Exception
        print('got: {}'.format(l))
        save(value, 'palsar2_' + date2name(temp_date) + '.json')
    except Exception as e:
        print('error!')
        save(value, 'palsar2_' + date2name(temp_date) + '_error' + '.log')
    time.sleep(3)
    temp_date = temp_date + datetime.timedelta(days=1)
print('end.')
driver.quit()