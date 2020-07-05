#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 07:56:59 2020

@author: tefirman
"""

import numpy as np
import plotly.express as px
from plotly.offline import init_notebook_mode, plot
init_notebook_mode()
from sportsreference.mlb.roster import Roster
from sportsreference.mlb.boxscore import Boxscores, Boxscore
import pandas as pd
import datetime
import time
import os
import optparse

def logFactorial(value):
    """ Returns the logarithm of the factorial of the value provided using Sterling's approximation """
    if all([value > 0,abs(round(value) - value) < 0.000001,value <= 34]):
        return float(sum(np.log(range(1,int(value) + 1))))
    elif all([value > 0,abs(round(value) - value) < 0.000001,value > 34]):
        return float(value)*np.log(float(value)) - float(value) + \
        0.5*np.log(2.0*np.pi*float(value)) - 1.0/(12.0*float(value))
    elif value == 0:
        return float(0)
    else:
        return float('nan')

nchoosek = [np.array([logFactorial(ab) - logFactorial(ab - hit) - \
logFactorial(hit) for hit in range(ab + 1)]) for ab in range(1300)]

def fourHundredProb(career,games,abPerGame):
    global nchoosek
    abProbs = abPerGame
    for game in range(games - 1):
        abProbs = np.convolve(abProbs,abPerGame)
    fourHundred = 0.0
    for ab in range(1,len(abProbs)):
        hits = np.arange(ab + 1)
        avgs = hits/ab
        if ab == len(nchoosek):
            nchoosek.append(np.array([logFactorial(ab) - logFactorial(ab - hit) - \
            logFactorial(hit) for hit in range(ab + 1)]))
        probs = nchoosek[ab] + hits*np.log(career) + (ab - hits)*np.log(1 - career)
        probs = np.exp(probs - np.max(probs))
        probs = probs/sum(probs)
        fourHundred += sum(probs[avgs >= 0.4])*abProbs[ab]
    return fourHundred

def getAtBatStats(season,path=None):
    actualABs = pd.DataFrame()
    season = Boxscores(datetime.datetime(season,4,1),end_date=datetime.datetime(season,10,1) - datetime.timedelta(days=1))
    for day in sorted(season.games.keys()):
        print(day + ', ' + str(datetime.datetime.now()))
        for game in season.games[day]:
            try:
                game_data = Boxscore(game['boxscore'])
                actualABs = actualABs.append(pd.DataFrame({'date':day,'team':game['home_abbr'],\
                'name':[player.name for player in game_data.home_players if player.at_bats][:9],\
                'ABs':[player.at_bats for player in game_data.home_players if player.at_bats][:9]}),ignore_index=True)
            except:
                print("Can't find " + game['boxscore'] + '... Skipping...')
                time.sleep(5)
    if path:
        actualABs.to_csv(path,index=False)
    return actualABs

def getPlayerStats(season,path=None):
    player_stats = pd.DataFrame()
    teams = ['COL','DET','TBR','WSN','CHW','SFG','CLE','TOR','BAL',\
    'STL','LAA','BOS','HOU','KCR','SDP','NYM','LAD','MIN','MIA','PIT','PHI',\
    'OAK','ARI','ATL','MIL','SEA','CIN','CHC','TEX','NYY']
    for team in teams:
        print(team + ', ' + str(datetime.datetime.now()))
        try:
            roster = Roster(team,year=season)
            for player in roster.players:
                if player.position != 'P':
                    player_stats = player_stats.append(player.dataframe.loc[[str(season),'Career']].reset_index(),ignore_index=True)
        except:
            print("Can't find " + team + ' for ' + str(season) + '... Skipping...')
            time.sleep(5)
    player_stats = player_stats.rename(columns={'level_0':'context'}).drop_duplicates()
    player_stats = pd.merge(left=player_stats.loc[player_stats.context == 'Career'],\
    right=player_stats.loc[player_stats.context == str(season),['player_id','name','games_started']]\
    .rename(columns={'games_started':'season_starts'}),how='inner',on=['player_id','name'])
    if path:
        player_stats.to_csv(path,index=False)
    return player_stats

def excelAutofit(df,name,writer):
    f = writer.book.add_format()
    f.set_align('center')
    f.set_align('vcenter')
    p = writer.book.add_format({'num_format':'0.0%'})
    p.set_align('center')
    p.set_align('vcenter')
    df.to_excel(writer,sheet_name=name,index=False)
    for idx, col in enumerate(df):
        series = df[col]
        max_len = min(max((series.astype(str).map(len).max(),len(str(series.name)))) + 1,50)
        if 'Probability' in col:
            writer.sheets[name].set_column(idx,idx,max_len,p)
        else:
            writer.sheets[name].set_column(idx,idx,max_len,f)
    writer.sheets[name].autofilter('A1:' + (chr(64 + (df.shape[1] - 1)//26) + \
    chr(65 + (df.shape[1] - 1)%26)).replace('@','') + str(df.shape[0] + 1))
    return writer

def main():
    """ Intializing input arguments """
    parser = optparse.OptionParser()
    parser.add_option('--games',action="store",dest="games",help="number of games in the proposed season")
    parser.add_option('--season',action="store",dest="season",help="season from which to pull stats")
    parser.add_option('--ab',action="store",dest="ab",help="path of at bat statistics per player per game")
    parser.add_option('--avg',action="store",dest="avg",help="path of career batting average statistics")
    options,args = parser.parse_args()
    options.games = [int(val) for val in options.games.split(',') if val.isnumeric()]
    if len(options.games) == 0:
        options.games = [60,162]
    options.season = int(options.season) if options.season else 2019
    
    """ Downloading at-bats per game distribution """
    if os.path.exists(options.ab):
        actualABs = pd.read_csv(options.ab)
    else:
        actualABs = getAtBatStats(options.season,path='AtBatStats.csv')
    abPerGame = np.histogram(actualABs.ABs,bins=np.arange(actualABs.ABs.max() + 2) - 0.5)[0]
    abPerGame = abPerGame/sum(abPerGame)
    
    """ Downloading career batting average distribution """
    if os.path.exists(options.avg):
        player_stats = pd.read_csv(options.avg)
    else:
        player_stats = getPlayerStats(options.season,path='PlayerStats.csv')
    inds = player_stats.season_starts > 20
    counts,careers = np.histogram(player_stats.loc[inds,'batting_average'],\
    bins=np.arange(min(0.1,round(player_stats.loc[inds,'batting_average'].min(),3)),\
    max(0.4,player_stats.loc[inds,'batting_average'].max()) + 0.002,0.001) - 0.0005)
    careers = careers[:-1] + 0.0005
    
    """ Calculating probabilities of hitting .400 and saving to Excel spreadsheet """
    anyPlayer = pd.DataFrame()
    data = pd.DataFrame()
    for games in options.games:
        prob_flat = 1.0
        prob_var = 1.0
        for career in careers:
            data = data.append({'Games':games,'Career':career,'Type':'Fixed AB',\
            'Probability of Hitting .400':fourHundredProb(career,games,[0.0,0.0,0.0,0.0,1.0])},ignore_index=True)
            prob_flat *= (1 - data['Probability of Hitting .400'].values[-1])**sum(counts[careers == career])
            data = data.append({'Games':games,'Career':career,'Type':'Random AB',\
            'Probability of Hitting .400':fourHundredProb(career,games,abPerGame)},ignore_index=True)
            prob_var *= (1 - data['Probability of Hitting .400'].values[-1])**sum(counts[careers == career])
        anyPlayer = anyPlayer.append({'# of Games':games,'Probability of Anyone Hitting .400 (Fixed AB)':1 - prob_flat,\
        'Probability of Anyone Hitting .400 (Random AB)':1 - prob_var},ignore_index=True)
    writer = pd.ExcelWriter('FourHundredProbByCareerAvg.xlsx',engine='xlsxwriter')
    writer = excelAutofit(anyPlayer,'Any Player',writer)
    writer = excelAutofit(data,'By Career Avg',writer)
    writer.sheets['Any Player'].conditional_format('B2:C' + str(anyPlayer.shape[0] + 1),\
    {'type':'3_color_scale','min_color':'#FF6347','mid_color':'#FFD700','max_color':'#3CB371'})
    writer.save()
    
    """ Plotting interactive html graph of results """
    data["Probability of Hitting .400"] *= 100
    data = data.rename(columns={"Probability of Hitting .400":"Percent Probability of Hitting .400"})
    fig = px.scatter(data,x="Career",y="Percent Probability of Hitting .400",color="Type",\
    hover_name="Type",animation_frame='Games',range_x=[0.2,0.4],range_y=[0,50])
    plot(fig,filename='FourHundredProbByCareerAvg.html')

if __name__ == "__main__":
    main()




