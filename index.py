#!/usr/bin/python3.7
import urllib.request
import json
import threading
import time
import sys
from datetime import datetime, timedelta
import cgitb
import http.client
http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
cgitb.enable(display=0, logdir="/var/www/expugnator")


config_datei = open('trade.config','r')
config = json.loads(config_datei.read())

Node = config['Node']
Tier = config['Tier']
Ress = config['Ress']

Nodestr= ""
for n in Node:
    Nodestr += n+","
Nodestr = Nodestr[:-1]

Itemstr = ""

for r in Ress:
    for t in Tier:
        Itemstr += t+"_"+r+","
Itemstr = Itemstr[:-1]


url = "https://www.albion-online-data.com/api/v2/stats/prices/"+Itemstr+"?locations="+Nodestr+"&qualities=1"

response = urllib.request.urlopen(url)
data = json.loads(response.read())
if data == []:
    exit

spek = []
direkt = []



for start in range(len(data)):
    for ziel in range(len(data)):
        if start != ziel:
            if data[start]['item_id'] == data[ziel]['item_id']:

                if(data[start]['sell_price_min'] < (data[ziel]['sell_price_min']-1)*0.8):
                    spek += [[data[start],data[ziel],((data[ziel]['sell_price_min']-1)*0.9)/data[start]['sell_price_min']]]
                
                if(data[start]['sell_price_min'] < (data[ziel]['buy_price_max'])*0.8):
                    direkt += [[data[start],data[ziel],(data[ziel]['buy_price_max']*0.9)/data[start]['sell_price_min']]]
                
def help(ls):
    return(ls[2])

spek.sort(key=help)
spek.reverse()

direkt.sort(key=help)
direkt.reverse()

spekdirekt = []
for item in spek:
    time = item[0]['sell_price_min_date']
    if time > item[1]['sell_price_min_date']: time = item[1]['sell_price_min_date']
    
    spekdirekt += [[item[0]['item_id'],item[0]['city'],item[1]['city'],int((item[2]-1)*100),time,item[0]['sell_price_min'],item[1]['sell_price_min']]]


ergdirekt = []
for item in direkt:
    time = item[0]['sell_price_min_date']
    if time > item[1]['buy_price_max_date']: time = item[1]['buy_price_max_date']
    
    ergdirekt += [[item[0]['item_id'],item[0]['city'],item[1]['city'],int((item[2]-1)*100),time,item[0]['sell_price_min'],item[1]['buy_price_max']]]


time = datetime.utcnow() - timedelta(minutes=int(config['min']))
timestamp = str(time.year)+"-"+("00"+str(time.month))[-2:]+"-"+("00"+str(time.day))[-2:]+"T"+str(time.hour)+":"+str(time.minute)+":"+str(time.second)

html = ""
print("Content-type:text/html\r\n\r\n")
html += "<html>"
html += "<head><title>Hello - Second CGI Program</title></head>"
html += "<body><table>"


html += "<tr><td>Direkt</td></tr>"
html += "<tr><td>Item</td><td>Start</td><td>Einkeufspreis</td><td>Ziel</td><td>Verkaufspreis</td><td>Gewinn</td><td>Timestamp</td>"
for item in ergdirekt:
    if item[4] > timestamp:
        html += "<tr><td>"+str(item[0])+"+</td><td>"+str(item[1])+"</td><td>"+str(item[5])+"</td><td>"+str(item[2])+"</td><td>"+str(item[6])+"</td><td>"+str(item[3])+"%</td><td>"+str(item[4])+"</td></tr>"

html += "<tr></tr>"
html += "<tr><td>Spekulation</td></tr>"
html += "<tr><td>Item</td><td>Start</td><td>Einkeufspreis</td><td>Ziel</td><td>Verkaufspreis</td><td>Gewinn</td><td>Timestamp</td>"
for item in spekdirekt:
    if item[4] > timestamp:
        html += "<tr><td>"+str(item[0])+"+</td><td>"+str(item[1])+"</td><td>"+str(item[5])+"</td><td>"+str(item[2])+"</td><td>"+str(item[6])+"</td><td>"+str(item[3])+"%</td><td>"+str(item[4])+"</td></tr>"

html += "</table></body></html>"

"""
datei = open('trade.html','w')
datei.write(html)
datei.close()
"""

print(html)
