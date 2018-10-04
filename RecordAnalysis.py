#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 11:22:15 2018

@author: firman.taylor
"""

import os
import pandas as pd
import numpy as np
from scipy.optimize import minimize

columnNames = ['Date','Game_Nbr','Day_Of_Week','Vis_Name','Vis_League',\
'Home_Game_Nbr','Home_Name','Home_League','Home_Game_Nbr','Vis_Score',\
'Home_Score','Num_Outs','Day_Night']
counter = 0
while len(columnNames) < 161:
    columnNames.append('Unneeded_' + str(counter))
    counter += 1
del counter

playoff_games = pd.concat([pd.read_csv('gl1871_2017/gldv.txt',names=columnNames),\
pd.read_csv('gl1871_2017/gllc.txt',names=columnNames),\
pd.read_csv('gl1871_2017/glwc.txt',names=columnNames),\
pd.read_csv('gl1871_2017/glws.txt',names=columnNames)])
playoff_games['Year'] = np.floor(playoff_games['Date']/10000)

gameFiles = os.listdir('gl1871_2017/')
team_stats = pd.DataFrame(columns=['Year','Team','League','W','L','T','R','RA','Playoffs'])
for year in range(1871,2018):
    if year%10 == 0:
        print(year)
    if 'gl' + str(year) + '.txt' not in gameFiles:
        continue
    games = pd.read_csv('gl1871_2017/gl' + str(year) + '.txt',names=columnNames)
    for team in games.Home_Name.unique():
        team_stats = team_stats.append({'Year':year,'Team':team,'League':games.loc[games.Home_Name == team,'Home_League'].unique()[0],\
        'W':games.loc[np.all([games.Home_Name == team,games.Home_Score > games.Vis_Score],axis=0)].shape[0] + \
        games.loc[np.all([games.Vis_Name == team,games.Vis_Score > games.Home_Score],axis=0)].shape[0],\
        'L':games.loc[np.all([games.Home_Name == team,games.Home_Score < games.Vis_Score],axis=0)].shape[0] + \
        games.loc[np.all([games.Vis_Name == team,games.Vis_Score < games.Home_Score],axis=0)].shape[0],\
        'T':games.loc[np.all([games.Home_Name == team,games.Home_Score == games.Vis_Score],axis=0)].shape[0] + \
        games.loc[np.all([games.Vis_Name == team,games.Vis_Score == games.Home_Score],axis=0)].shape[0],\
        'R':games.loc[games.Home_Name == team].Home_Score.sum() + games.loc[games.Vis_Name == team].Vis_Score.sum(),\
        'RA':games.loc[games.Home_Name == team].Vis_Score.sum() + games.loc[games.Vis_Name == team].Home_Score.sum(),\
        'Playoffs':playoff_games.loc[np.all([playoff_games.Year == year,np.any([playoff_games.Home_Name == team,\
        playoff_games.Vis_Name == team],axis=0)],axis=0)].shape[0] > 0},ignore_index=True)
    del team
    del games
del year
del gameFiles
del playoff_games

team_stats = team_stats.astype(dtype={'Year':'int','Team':'str','League':'str','W':'int','L':'int','T':'int','R':'int','RA':'int','Playoffs':'bool'})

translation = {'NYY':'NYA','CHC':'CHN','LAD':'LAN','TBR':'TBA','STL':'SLN',\
'WSN':'WAS','LAA':'ANA','NYM':'NYN','SFG':'SFN','SDP':'SDN','CHW':'CHA','KCR':'KCA'}
lastSeason = pd.read_csv('2018Season.csv')
for team in translation:
    lastSeason.loc[lastSeason.Tm == team,'Tm'] = translation[team]
del team
lastSeason['Playoffs'] = lastSeason['Rk'] <= 10
lastSeason['Year'] = 2018
lastSeason['Team'] = lastSeason['Tm']
lastSeason['League'] = lastSeason['Lg']
lastSeason['T'] = 0
lastSeason['R'] = lastSeason['R']*lastSeason['G']
lastSeason['RA'] = lastSeason['RA']*lastSeason['G']
lastSeason = lastSeason[['Year','Team','League','W','L','T','R','RA','Playoffs']]
lastSeason = lastSeason.astype(dtype={'Year':'int','Team':'str','League':'str','W':'int','L':'int','T':'int','R':'int','RA':'int','Playoffs':'bool'})
team_stats = team_stats.append(lastSeason)
del lastSeason
del translation

team_stats['Win_Pct'] = team_stats['W']/(team_stats['W'] + team_stats['L'] + team_stats['T'])
team_stats['Pythag_Win_Pct'] = (team_stats['R']**1.83)/(team_stats['R']**1.83 + team_stats['RA']**1.83)
team_stats['Pythag_Wins'] = round(team_stats['Pythag_Win_Pct']*162)
team_stats['Pythag_Diff'] = team_stats['Win_Pct'] - team_stats['Pythag_Win_Pct']
team_stats['Pythag_Game_Diff'] = (team_stats['Win_Pct'] - team_stats['Pythag_Win_Pct'])*(team_stats['W'] + team_stats['L'] + team_stats['T'])
team_stats['Rel_Pythag'] = team_stats['Win_Pct']/team_stats['Pythag_Win_Pct']

team_stats.to_csv('MLBstatsByTeam.csv')

team_stats = team_stats.loc[team_stats.Year >= 1919] ### Excluding the deadball era... ###
mariners_2018 = team_stats.loc[np.all([team_stats.Year == 2018,team_stats.Team == 'SEA'],axis=0)].to_dict('list')
for stat in mariners_2018:
    mariners_2018[stat] = mariners_2018[stat][0]
del stat

def gaussian_fit(sigma):
    global winPctInds
    global winPctHist
    fitProb = np.exp(-((winPctInds - 0.5)**2)/(2*(sigma**2)))
    return np.sum((fitProb/np.sum(fitProb) - winPctHist)**2)

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc('font',family='Arial')
mpl.rc('font',size=12)
mpl.rcParams['xtick.labelsize'] = 15
mpl.rcParams['ytick.labelsize'] = 15
plt.rc('font',weight='bold')
textSize = 18
lineSize = 3
markerSize = 20

""" Actual Win Percentage Plots """

winPctInc = 0.025
minVals = 22
winPctHist,winPctInds = np.histogram(team_stats.Win_Pct,np.arange(0.0 - winPctInc/2,1.0 + winPctInc,winPctInc))
playoffHist = np.histogram(team_stats.loc[team_stats.Playoffs,'Win_Pct'],np.arange(0.0 - winPctInc/2,1.0 + winPctInc,winPctInc))[0].astype(float)
playoffHist[winPctHist < minVals] = float('NaN')
playoffHist = playoffHist/winPctHist
winPctHist = winPctHist/team_stats.shape[0]
winPctInds = winPctInds[:-1] + winPctInc/2
fittedSig = minimize(gaussian_fit,0.1,method='Nelder-Mead',tol=1e-6)['x'][0]
fitProb = np.exp(-((winPctInds - 0.5)**2)/(2*(fittedSig**2)))
fitProb = fitProb/np.sum(fitProb)

plt.figure(figsize=(6,5))
plt.plot(100*winPctInds,100*winPctHist,linewidth=lineSize)
#plt.plot(100*winPctInds,100*fitProb,linewidth=lineSize/2)
ind2plot_Win = np.where(abs(winPctInds - mariners_2018['Win_Pct']) == min(abs(winPctInds - mariners_2018['Win_Pct'])))[0][0]
ind2plot_Pythag = np.where(abs(winPctInds - mariners_2018['Pythag_Win_Pct']) == min(abs(winPctInds - mariners_2018['Pythag_Win_Pct'])))[0][0]
plt.plot(100*winPctInds[ind2plot_Win],100*winPctHist[ind2plot_Win],'*g',markersize=markerSize)
plt.plot(100*winPctInds[ind2plot_Pythag],100*winPctHist[ind2plot_Pythag],'*r',markersize=markerSize)
plt.grid(True)
plt.axis([0,100,0,14])
plt.xticks(np.arange(0,101,25))
plt.yticks(np.arange(0,12.1,4))
plt.xlabel('Win %',fontsize=textSize,fontweight='bold')
plt.ylabel('Probability of Occurence',fontsize=textSize,fontweight='bold')
plt.legend(['1919-2017','Actual','Pythagorean'])
plt.savefig('WinPctHist.pdf')
#plt.close()

plt.figure(figsize=(6,5))
plt.plot(100*winPctInds,100*playoffHist,linewidth=lineSize)
plt.plot(100*winPctInds[ind2plot_Win],100*playoffHist[ind2plot_Win],'*g',markersize=markerSize)
plt.plot(100*winPctInds[ind2plot_Pythag],100*playoffHist[ind2plot_Pythag],'*r',markersize=markerSize)
plt.grid(True)
plt.axis([30,70,0,75])
plt.xticks(np.arange(30,71,10))
plt.yticks(np.arange(0,61,20))
plt.xlabel('Win %',fontsize=textSize,fontweight='bold')
plt.ylabel('Playoff Probability',fontsize=textSize,fontweight='bold')
plt.legend(['1919-2017','Actual','Pythagorean'])
plt.savefig('PlayoffProbHist.pdf')
#plt.close()

""" Actual vs. Pythagorean 2D Heat Maps """

pythagInc = 0.025
minVals = 22
winRunHist,winPctInds,pythagInds = np.histogram2d(team_stats.Win_Pct,team_stats.Pythag_Win_Pct,\
bins=[np.arange(0.0 - winPctInc/2,1.0 + winPctInc,winPctInc),\
np.arange(0.0 - pythagInc/2,1.0 + pythagInc,pythagInc)])
playoffHist = np.histogram2d(team_stats.loc[team_stats.Playoffs,'Win_Pct'],team_stats.loc[team_stats.Playoffs,'Pythag_Win_Pct'],\
bins=[np.arange(0.0 - winPctInc/2,1.0 + winPctInc,winPctInc),\
np.arange(0.0 - pythagInc/2,1.0 + pythagInc,pythagInc)])[0].astype(float)
playoffHist[winRunHist < minVals] = float('NaN')
playoffHist = playoffHist/winRunHist
winRunHist = winRunHist/team_stats.shape[0]
winPctInds = winPctInds[:-1] + winPctInc/2
pythagInds = pythagInds[:-1] + pythagInc/2

plt.figure(figsize=(7,5))
plt.pcolor(pythagInds*100,winPctInds*100,winRunHist*100,cmap='Blues')
plt.plot(100*mariners_2018['Pythag_Win_Pct'],100*mariners_2018['Win_Pct'],'*g',markersize=markerSize)
plt.axis([30,70,30,70])
plt.xticks(np.arange(30,71,10))
plt.yticks(np.arange(30,71,10))
plt.colorbar(ticks=np.arange(5.1))
plt.xlabel('Pythagorean Win %',fontsize=textSize,fontweight='bold')
plt.ylabel('Actual Win %',fontsize=textSize,fontweight='bold')
plt.title('Probability of Occurence')
plt.savefig('RealVsPythagHeatMap.pdf')
#plt.close()

""" Difference Between Actual and Pythagorean Plots """

diffInc = 0.01
diffVals,diffInds = np.histogram(team_stats.Pythag_Diff,np.arange(-0.1 - diffInc/2,0.1 + diffInc,diffInc))
diffVals = diffVals/team_stats.shape[0]
diffInds = diffInds[:-1] + diffInc/2

plt.figure(figsize=(6,5))
plt.plot(diffInds*100,diffVals*100,linewidth=lineSize)
ind2plot = np.where(abs(diffInds - mariners_2018['Win_Pct'] + mariners_2018['Pythag_Win_Pct']) == \
min(abs(diffInds - mariners_2018['Win_Pct'] + mariners_2018['Pythag_Win_Pct'])))[0][0]
plt.plot(100*diffInds[ind2plot],100*diffVals[ind2plot],'*g',markersize=markerSize)
plt.grid(True)
plt.axis([-10,10,0,16])
plt.xticks(np.arange(-10,10.1,5))
plt.yticks(np.arange(0,15.1,5))
plt.xlabel('Actual Win % - Pythagorean Win %',fontsize=textSize,fontweight='bold')
plt.ylabel('Probability',fontsize=textSize,fontweight='bold')
plt.legend(['1919-2017',"2018 M's"])
plt.savefig('PythagDiffHist.pdf')
#plt.close()

outliers = team_stats.loc[team_stats.Pythag_Diff >= mariners_2018['Win_Pct'] - mariners_2018['Pythag_Win_Pct']]

""" Win % Standard Deviation Over Time """

years = np.arange(1919,2019)
stDevs_AL = []
range_AL = []
stDevs_NL = []
range_NL = []
for year in years:
    if year%10 == 0:
        print(year)
    if team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'AL'],axis=0)].shape[0] > 0:
        stDevs_AL.append(team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'AL'],axis=0),'Win_Pct'].std())
        range_AL.append(team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'AL'],axis=0),'Win_Pct'].max() - \
        team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'AL'],axis=0),'Win_Pct'].min())
    else:
        stDevs_AL.append(float('NaN'))
        range_AL.append(float('NaN'))
    if team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'NL'],axis=0)].shape[0] > 0:
        stDevs_NL.append(team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'NL'],axis=0),'Win_Pct'].std())
        range_NL.append(team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'NL'],axis=0),'Win_Pct'].max() - \
        team_stats.loc[np.all([team_stats.Year == year,team_stats.League == 'NL'],axis=0),'Win_Pct'].min())
    else:
        stDevs_NL.append(float('NaN'))
        range_NL.append(float('NaN'))
del year

plt.figure(figsize=(6,5))
plt.plot(years,stDevs_AL,years,stDevs_NL)
plt.plot(years,np.ones(len(years))*stDevs_AL[-1],'r')
plt.grid(True)
plt.xlabel('Year')
plt.ylabel('Win % St. Dev.')
plt.legend(['AL','NL'])
plt.title('Highest St. Dev. Since ' + str(max(years[np.array(stDevs_AL) > stDevs_AL[-1]][-1],years[np.array(stDevs_NL) > stDevs_AL[-1]][-1])))
plt.savefig('WinPctStDevsOverTime.pdf')
#plt.close()

plt.figure(figsize=(6,5))
plt.plot(years,range_AL,years,range_NL)
plt.plot(years,np.ones(len(years))*range_AL[-1],'r')
plt.grid(True)
plt.xlabel('Year')
plt.ylabel('Win % Range')
plt.legend(['AL','NL'])
plt.title('Highest Range Since ' + str(max(years[np.array(range_AL) > range_AL[-1]][-1],years[np.array(range_NL) > range_AL[-1]][-1])))
plt.savefig('WinPctRangesOverTime.pdf')
#plt.close()

""" Playoff Expectancies """

since1998 = team_stats.loc[team_stats.Year >= 1998]
since1998.loc[since1998.Team == 'FLO','Team'] = 'MIA'
since1998.loc[since1998.Team == 'MON','Team'] = 'WAS'
oneWC = pd.read_csv('OneWC_Curve.csv')
twoWC = pd.read_csv('TwoWC_Curve.csv')
for year in range(1998,2019):
    for team in since1998.Team.unique():
        if year < 2012:
            since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Playoffs_Exp'] = \
            oneWC.loc[oneWC.Wins == since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'W'].tolist()[0],'Probability'].tolist()[0]
            since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Playoffs_Exp_Pythag'] = \
            oneWC.loc[oneWC.Wins == since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Pythag_Wins'].tolist()[0],'Probability'].tolist()[0]
        else:
            since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Playoffs_Exp'] = \
            twoWC.loc[twoWC.Wins == since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'W'].tolist()[0],'Probability'].tolist()[0]
            since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Playoffs_Exp'] = \
            twoWC.loc[twoWC.Wins == since1998.loc[np.all([since1998.Year == year,since1998.Team == team],axis=0),'Pythag_Wins'].tolist()[0],'Probability'].tolist()[0]
    del team
del year

playoffs = pd.DataFrame(columns=['Team','Expected','Expected_Pythag','Actual'])
for team in since1998.Team.unique():
    playoffs = playoffs.append({'Team':team,'Expected':since1998.loc[since1998.Team == team,'Playoffs_Exp'].sum(),\
    'Expected_Pythag':since1998.loc[since1998.Team == team,'Playoffs_Exp_Pythag'].sum(),'Actual':since1998.loc[since1998.Team == team,'Playoffs'].sum()},ignore_index=True)
del team
playoffs['Difference'] = playoffs['Expected'] - playoffs['Actual']
playoffs['Difference_Pythag'] = playoffs['Expected_Pythag'] - playoffs['Actual']
playoffs = playoffs.sort_values(by=['Difference'],ascending=False)
#playoffs = playoffs.sort_values(by=['Difference_Pythag'],ascending=False)


