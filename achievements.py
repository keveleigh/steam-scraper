#!/usr/bin/env python

"""
This scrapes achievement info from Steam.
It uses BeautifulSoup 4 and xlwt.

In order to use this, you will need to download bs4 and xlwt.

Dictionary format: {Steam Name: [{GameName1: [Achievement1, Achievement2, Achievement3, ... , AchievementN]}, ... , {GameNameN: [Achievement1, Achievement2, Achievement3, ... AchievementN]}]}

Command format: python achievements.py [SteamID [GameName]]
"""

import urllib2
import xlwt
import sys
import os
from bs4 import BeautifulSoup as bs

allNames = {}

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

    if len(argv) > 0:
        names = [argv[0]]
    elif os.path.isfile('nameList.txt'):
        f = open('nameList.txt', 'r')
        names = [line.strip() for line in f.readlines()]
    else:
        names = ['supertrombone']

    for steamName in names:
        scrape_links(steamName, gameName)

    wb = xlwt.Workbook()
    items = allNames.items()
    print type(items)
    items.sort(key=lambda t : tuple(t[0].lower()))
    ws = wb.add_sheet(gameName);

    i = 1
    col = len(items)+1
    ws.col(0).width = 10000
    for key in achs:
        ws.write(i, 0, key)
        ws.write(i, col, xlwt.Formula('SUM(B' + str(i+1) + ':' + str(chr(ord('B') + (col-2))) + str(i+1) + ')'))
        i+=1
    i = 1
    for key, value in items:
        ws.write(0, i, key)
        ws.col(i).width = len(key)*300;
        for v in value[gameName]:
            vIndex = achs.index(v)
            ws.write(vIndex+1, i, int(1))
        i+=1

    wb.save('Achievements.xls');

if __name__ == '__main__':
    import time
    start = time.time()
    main(sys.argv[1:])
    print time.time() - start, 'seconds'
