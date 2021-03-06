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
cgitb.enable(display=0, logdir="/var/www/expugnator/log/")

craft_datei = open('craft.json','r')
craft = json.loads(craft_datei.read())

#print(craft)

tier = ["T4","T5","T6","T7","T8"]
res = ["CLOTH", "FIBER", "HIDE", "LEATHER", "METALBAR"]
ent_res = ["", "_LEVEL1@1", "_LEVEL2@2", "_LEVEL3@3"]
ent_craft = ["", "@1", "@2", "@3"]

Nodestr = "Thetford"

#url = "https://www.albion-online-data.com/api/v2/stats/prices/"+Itemstr+"?locations="+Nodestr+"&qualities=1"

Itemstr = ""

for gear in craft[0]:
    for t in tier:
        for e in ent_craft:
            Itemstr += t + "_" + gear + e + ","

Itemstr = Itemstr[:-1]


url = "https://www.albion-online-data.com/api/v2/stats/prices/"+Itemstr+"?locations="+Nodestr+"&qualities=1"

response = urllib.request.urlopen(url)
data = json.loads(response.read())


Itemstr = ""

for t in tier:
    for r in res:
        for e in ent_res:
            Itemstr += t + "_" + r + e + ","

        
        
Itemstr = Itemstr[:-1]

url = "https://www.albion-online-data.com/api/v2/stats/prices/"+Itemstr+"?locations="+Nodestr+"&qualities=1"

response = urllib.request.urlopen(url)
basemats = json.loads(response.read())


art = []
for g in craft[0]:
    for i in craft[0][g]["Mat"]:
        if i["Anz"] == 1:
            if i["Res"] not in art:
                art += [i["Res"]]


    
Itemstr = ""
for t in tier:
    for a in art:
        if a == "QUESTITEM_TOKEN_ROYAL":
            Itemstr += a + "_" + t + ","
        else:
            Itemstr += t + "_" + a + ","


Itemstr = Itemstr[:-1]

url = "https://www.albion-online-data.com/api/v2/stats/prices/"+Itemstr+"?locations="+Nodestr+"&qualities=1"

response = urllib.request.urlopen(url)
artmats = json.loads(response.read())




#art_mats =


def suche_preis(mat, liste):
    for i in liste:
        if i["item_id"] == mat:
            return([int(i["sell_price_min"]), i["sell_price_min_date"]])
    return([0,""])

prod = []            
for i in data:
    item = i["item_id"][3:]
    tier = i["item_id"][:2]

    if item[-2] == "@":
        ent = item[-2:]
        item = item[:-2]
    else:
        ent = ""
    
    mat = (craft[0][item]["Mat"])
    mat_kosten = 0
    art_kosten = 0
    time = "9999-00-00T00:00:00"
    valid = 1
    # Kosten Ress
    for j in mat:

        if ent == "":
            ent_mat = ""
        else:
            ent_mat = ent_res[int(ent[1])]
        
        erg = suche_preis(tier + "_" + j["Res"] + ent_mat, basemats)
        mat_kosten += (erg[0]*int(j["Anz"]))
        
        if time > erg[1] and j["Anz"] != 1:
            time = erg[1]

        if erg[0] == 0:
            valid = 0
            
    # Kosten Artefakt und Siegel
    for j in mat:
        erg = suche_preis(j["Res"] + "_" + tier, artmats)

        if j["Anz"] == 1 and erg[0] == 0:
            valid = 0

        if time > erg[1] and j["Anz"] == 1:
            time = erg[1]
        
        art_kosten += erg[0]
        

    
    prod += [[tier + "_" + item + ent, mat_kosten, art_kosten, i["sell_price_min"], time, valid]]

#print(prod)
"""
0: Item
1: Material Kosten
2: artefakt Kosten
3: Sell Price min
4: timestamp
5: valid
"""
local_datei = open('localisation.json',mode='r', encoding='utf-8')
local = json.loads(local_datei.read())


    
#https://wiki.albiononline.com/wiki/Journal



html = ""
print("Content-type:text/html\r\n\r\n")
html += "<html>"
html += "<head><title>Craft Program</title></head><table>"

for i in prod:
    if i[5] == 1:
        html += "<tr>"
        html += "<td>" + i[0][:2] + "</td>"
        for j in local:
            if j["UniqueName"] == i[0]:
                html += "<td>" + j["LocalizedNames"]["DE-DE"] + "</td>"


        html += "<td>" + str(i[1] + i[2]) + "</td>"
        html += "<td>" + str(i[3]) + "</td>"
        html += "<td>" + str(i[4]) + "</td>"
        html += "</tr>"

html += "</body></html>"

print(html)
