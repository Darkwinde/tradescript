#!/usr/bin/python3.7
import urllib.request
import json
import threading  # für später
import time
import sys
from datetime import datetime, timedelta
import cgitb
import http.client

http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
cgitb.enable(display=0, logdir="/var/www/expugnator/log/")

with open('trade.config', 'r') as config_file:
    config = json.loads(config_file.read())

NODE = config['Node']
TIER = config['Tier']
RESOURCE = config['Resource']

if RESOURCE:
    # Todo: Func if Armor or Resource
    quality_tier = 1

node_string = ""
for n in NODE:
    node_string += n + ","
node_string = node_string[:-1]

item_string = ""

for r in RESOURCE:
    for t in TIER:
        item_string += t + "_" + r + ","
item_string = item_string[:-1]


url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_string}?locations={node_string}&qualities={quality_tier} "

response = urllib.request.urlopen(url)
data = json.loads(response.read())

if not data:
    exit

spek = []  # Todo: Change Name
direct = []  # Todo: Change Name

counter = 0
for d in data:
    if data[counter]['sell_price_min'] == 0:
        del (data[counter])
    else:
        counter += 1

for start in range(len(data)):
    for destination in range(len(data)):
        if start != destination:
            if data[start]['item_id'] == data[destination]['item_id']:

                if data[start]['sell_price_min'] < (data[destination]['sell_price_min'] - 1) * 0.8:
                    spek += [{data[start], data[destination],
                              ((data[destination]['sell_price_min'] - 1) * 0.9) / data[start]['sell_price_min']}
                             ]

                if data[start]['sell_price_min'] < (data[destination]['buy_price_max']) * 0.8:
                    direct += [[data[start], data[destination],
                                (data[destination]['buy_price_max'] * 0.9) / data[start]['sell_price_min']]
                               ]


def help(ls):
    return ls[2]


spek.sort(key=help)
spek.reverse()

direct.sort(key=help)
direct.reverse()

direkt_spek = []
for item in spek:
    time = item[0]['sell_price_min_date']
    if time > item[1]['sell_price_min_date']:
        time = item[1]['sell_price_min_date']

    direkt_spek += [[item[0]['item_id'], item[0]['city'], item[1]['city'], int((item[2] - 1) * 100), time,
                     item[0]['sell_price_min'], item[1]['sell_price_min']]]

ergdirekt = []
for item in direct:
    time = item[0]['sell_price_min_date']
    if time > item[1]['buy_price_max_date']:
        time = item[1]['buy_price_max_date']

    ergdirekt += [[item[0]['item_id'], item[0]['city'], item[1]['city'], int((item[2] - 1) * 100), time,
                   item[0]['sell_price_min'], item[1]['buy_price_max']]]

time = datetime.utcnow() - timedelta(minutes=int(config['delta_t']))
# todo: Strftimes setzen https://www.programiz.com/python-programming/datetime/strftime
timestamp = str(time.year) + "-" + ("00" + str(time.month))[-2:] + "-" + ("00" + str(time.day))[-2:] + "T" + str(
        time.hour) + ":" + str(time.minute) + ":" + str(time.second)

html = ""
print("Content-type:text/html\r\n\r\n")
html += "<html>"
html += "<head><title>Hello - Second CGI Program</title></head>"
html += "<body><table>"

html += "<tr><td>Direkt</td></tr>"
html += "<tr><td>Item</td><td>Start</td><td>Einkeufspreis</td><td>Ziel</td><td>Verkaufspreis</td><td>Gewinn</td><td>Timestamp</td>"
for item in ergdirekt:
    if item[4] > timestamp:
        html += "<tr><td>" + str(item[0]) + "+</td><td>" + str(item[1]) + "</td><td>" + str(
                item[5]) + "</td><td>" + str(item[2]) + "</td><td>" + str(item[6]) + "</td><td>" + str(
                item[3]) + "%</td><td>" + str(item[4]) + "</td></tr>"

html += "<tr></tr>"
html += "<tr><td>Spekulation</td></tr>"
html += "<tr><td>Item</td><td>Start</td><td>Einkeufspreis</td><td>Ziel</td><td>Verkaufspreis</td><td>Gewinn</td><td>Timestamp</td>"
for item in direkt_spek:
    if item[4] > timestamp:
        html += "<tr><td>" + str(item[0]) + "+</td><td>" + str(item[1]) + "</td><td>" + str(
                item[5]) + "</td><td>" + str(item[2]) + "</td><td>" + str(item[6]) + "</td><td>" + str(
                item[3]) + "%</td><td>" + str(item[4]) + "</td></tr>"
                
html += "</table></body></html>"

"""
datei = open('trade.html','w')
datei.write(html)
datei.close()
"""

print(html)
