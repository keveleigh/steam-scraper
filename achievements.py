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
        
    achievements = soup.find('div', attrs={'id':'personalAchieve'})
    achievements = str(achievements).split('<br/><br/><br/>')
    achievements = achievements[0]
    achievements = bs(achievements, 'html.parser')
    achievements = achievements.find_all('h3')

    print len(achievements)

    allNames[steamName] = {}
    allNames[steamName][gameName] = []

    for ach in achievements:
        allNames[steamName][gameName].append(str(ach.contents[0]))

    print allNames

def main(argv):
    if len(argv) < 2:
        gameName = 'KillingFloor'
    else:
        gameName = argv[1]

    if os.path.isfile('nameList.txt'):
        f = open('nameList.txt', 'r')
        names = [line.strip() for line in f.readlines()]
    else:
        names = ['supertrombone']

    for steamName in names:
        scrape_links(steamName, gameName)

if __name__ == '__main__':
    import time
    start = time.time()
    main(sys.argv[1:])
    print time.time() - start, 'seconds'
