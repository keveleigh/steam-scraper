#!/usr/bin/env python

"""
This scrapes achievement info from Steam.
It uses BeautifulSoup 4 and xlwt.

In order to use this, you will need to download bs4 and xlwt.

Dictionary format: {Steam Name: [{GameName1: [Achievement1, Achievement2, Achievement3, ... , AchievementN]}, ... , {GameNameN: [Achievement1, Achievement2, Achievement3, ... AchievementN]}]}

Command format: python achievements.py [SteamID [GameName]]
"""

import urllib2
import xlsxwriter
import sys
import os
import collections
from bs4 import BeautifulSoup as bs

allNames = collections.OrderedDict()

def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    yield 'Hello from Azure Websites\n'

def _format_steam_url(steamName, gameName):
    """Format Steam link to scrape individual achievements from."""
    if steamName.isdigit():
        link = ['http://steamcommunity.com/profiles/' + steamName + '/stats/' + gameName + '/']
    else:
        link = ['http://steamcommunity.com/id/' + steamName + '/stats/' + gameName + '/']
    return link[0]

def scrape_links(steamName, gameName):
    """Scrape Steam's pages for data."""
    global allNames

    steam_page = _format_steam_url(steamName, gameName)

    page = urllib2.urlopen(steam_page)   
    print page.geturl()
    
    soup = bs(page.read(), 'html.parser')

    name = soup.find('a', attrs={'class':'whiteLink'})
    name = str(name.contents[0])
    
    achievements = soup.find('div', attrs={'id':'personalAchieve'})
    achievements = str(achievements).split('<br/><br/><br/>')
    achievements = achievements[0]
    achievements = bs(achievements, 'html.parser')
    achievements = achievements.find_all('h3')

    allNames[name] = {}
    allNames[name][gameName] = []

    for ach in achievements:
        allNames[name][gameName].append(str(ach.contents[0]).strip())

def main(argv):
    if len(argv) < 2:
        gameName = 'KillingFloor'
    else:
        gameName = argv[1]

    a = open('allAchievements.txt', 'r')
    achs = [line.strip() for line in a.readlines()]

    achNames = []
    achTypes = []
    achMaps = []
    for line in achs:
        lineSplit = line.split('|')
        achNames.append(lineSplit[0])
        achTypes.append(lineSplit[1])
        if len(lineSplit) > 2:
            achMaps.append(lineSplit[2])
        else:
            achMaps.append('')

    if len(argv) > 0:
        names = [argv[0]]
    elif os.path.isfile('nameList.txt'):
        f = open('nameList.txt', 'r')
        names = [line.strip() for line in f.readlines()]
    else:
        names = ['supertrombone']

    for steamName in names:
        scrape_links(steamName, gameName)

    wb = xlsxwriter.Workbook('KFAchievements.xlsx')
    bold = wb.add_format({'bold': True})
    items = allNames.items()
##    items.sort(key=lambda t : tuple(t[0].lower()))
    ws = wb.add_worksheet(gameName)
    ws.freeze_panes(1, 0)
    ws.set_column(0, 0, 40)

    i = 1
    col = len(items)+1
    for key in achNames:
        ws.write(i, 0, key)
        ws.write_formula(i, col, '=SUM(B' + str(i+1) + ':' + str(chr(ord('B') + (col-2))) + str(i+1) + ')')
        ws.write(i, col+1, achTypes[i-1])
        ws.write(i, col+2, achMaps[i-1])
        i+=1
        
    i = 1
    for key, value in items:
        ws.write(0, i, key, bold)
        ws.set_column(i, i, len(key)+1.5)
        for v in value[gameName]:
            vIndex = achNames.index(v)
            ws.write(vIndex+1, i, 1)
        i+=1

    t = time.strftime("%x %I:%M:%S %p %Z")
    ws.write(0, 0, t, bold)
    ws.write(0, i, 'Total', bold)
    ws.write(0, col+1, 'Type', bold)
    ws.write(0, col+2, 'Map', bold)
    
    ws.set_column(i, i, 5)
    ws.set_column(i+1, i+1, 10)
    ws.set_column(i+2, i+2, 32)
    
    wb.close()

if __name__ == '__main__':
    import time
    start = time.time()
    main(sys.argv[1:])
    print time.time() - start, 'seconds'
