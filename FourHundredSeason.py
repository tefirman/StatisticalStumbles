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
import unidecode
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

def hitProb(ab,career):
    global nchoosek
    hits = np.arange(ab + 1)
    while ab >= len(nchoosek):
        nchoosek.append(np.array([logFactorial(len(nchoosek)) - \
        logFactorial(len(nchoosek) - hit) - logFactorial(hit) \
        for hit in range(len(nchoosek) + 1)]))
    probs = nchoosek[ab] + hits*np.log(career) + (ab - hits)*np.log(1 - career)
    probs = np.exp(probs - np.max(probs))
    probs = probs/sum(probs)
    return probs

def fourHundredProb(career,games,abPerGame):
    global nchoosek
    abProbs = abPerGame
    for game in range(games - 1):
        abProbs = np.convolve(abProbs,abPerGame)
    fourHundred = 0.0
    for ab in range(1,len(abProbs)):
        avgs = np.arange(ab + 1)/ab
        probs = hitProb(ab,career)
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
                actualABs = actualABs.append(pd.DataFrame({'date':day,'team':game['away_abbr'],\
                'name':[player.name for player in game_data.away_players if player.at_bats][:9],\
                'ABs':[player.at_bats for player in game_data.away_players if player.at_bats][:9]}),ignore_index=True)
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
    p = writer.book.add_format({'num_format':'0.000%'})
    p.set_align('center')
    p.set_align('vcenter')
    df.to_excel(writer,sheet_name=name,index=False)
    for idx, col in enumerate(df):
        series = df[col]
        max_len = min(max((series.astype(str).map(len).max(),len(str(series.name)))) + 1,50)
        if 'Hitting .400' in col:
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
    parser.add_option('--min',action="store",dest="min_games",help="minimum number of games started for a player to be included")
    parser.add_option('--ab',action="store",dest="ab",help="path of at bat statistics per player per game")
    parser.add_option('--avg',action="store",dest="avg",help="path of career batting average statistics")
    parser.add_option('--excel',action="store_true",dest="excel",help="whether to save results in an excel spreadsheet")
    parser.add_option('--graph',action="store_true",dest="graph",help="whether to graph results as interactive html files")
    options,args = parser.parse_args()
    options.games = [int(val) for val in options.games.split(',') if val.isnumeric()]
    if len(options.games) == 0:
        options.games = [60,162]
    options.season = int(options.season) if str(options.season).isnumeric() else 2019
    options.min_games = int(options.min_games) if str(options.min_games).isnumeric() else 81
    if not options.excel and not options.graph:
        print("Output type wasn't specified... Assuming both...")
        options.excel = True
        options.graph = True
    
    """ Downloading career batting average distribution """
    if os.path.exists(str(options.avg)):
        player_stats = pd.read_csv(options.avg)
    else:
        player_stats = getPlayerStats(options.season,path='PlayerStats.csv')
    player_stats.name = player_stats.name.apply(unidecode.unidecode).str.replace('Kike Hernandez','Enrique Hernandez')
    player_stats = player_stats.loc[player_stats.season_starts > options.min_games]
    counts,careers = np.histogram(player_stats.batting_average,\
    bins=np.arange(min(0.2,round(player_stats.batting_average.min(),3)),\
    max(0.4,player_stats.batting_average.max()) + 0.002,0.001) - 0.0005)
    careers = careers[:-1] + 0.0005
    
    """ Downloading at-bats per game distribution """
    if os.path.exists(str(options.ab)):
        actualABs = pd.read_csv(options.ab)
    else:
        actualABs = getAtBatStats(options.season,path='AtBatStats.csv')
    actualABs.name = actualABs.name.str.replace(' Jr.','')
    actualABs = actualABs.loc[actualABs.name.isin(player_stats.name)].reset_index(drop=True)
    player_stats = player_stats.loc[player_stats.name.isin(actualABs.name)].reset_index(drop=True)
    abPerGame = np.histogram(actualABs.ABs,bins=np.arange(actualABs.ABs.max() + 2) - 0.5)[0]
    abPerGame = abPerGame/sum(abPerGame)
    
    """ Calculating probabilities of hitting .400 """
    by_avg = pd.DataFrame()
    avg_hist = pd.DataFrame()
    by_player = pd.DataFrame()
    any_player = pd.DataFrame()
    for games in options.games:
        for career in careers:
            by_avg = by_avg.append({'Games':games,'Career':career,'Type':'Fixed AB',\
            'Probability of Hitting .400':fourHundredProb(career,games,[0.0,0.0,0.0,0.0,1.0])},ignore_index=True)
            by_avg = by_avg.append({'Games':games,'Career':career,'Type':'Random AB',\
            'Probability of Hitting .400':fourHundredProb(career,games,abPerGame)},ignore_index=True)
            if str(int(1000*career))[-2:] in ['00','50']:
                avg_hist = avg_hist.append(pd.DataFrame({'Games':games,\
                'Career':career,'Season':np.arange(games*4 + 1)/(games*4),\
                'Probability':hitProb(games*4,career)}),ignore_index=True)
        for ind in range(player_stats.shape[0]):
            name = player_stats.loc[ind,'name']
            career = player_stats.loc[ind,'batting_average']
            playerABs = np.histogram(actualABs.loc[actualABs.name == name,'ABs'],bins=np.arange(12) - 0.5)[0]
            playerABs = playerABs/sum(playerABs)
            by_player = by_player.append({'Games':games,'Player':name,'Career':career,\
            'Probability of Hitting .400':fourHundredProb(career,games,playerABs)},ignore_index=True)
        any_player = any_player.append({'# of Games':games,\
        'Anyone Hitting .400 (Fixed AB)':1 - ((1 - by_avg.loc[(by_avg.Type == 'Fixed AB') & \
        (by_avg.Games == games),'Probability of Hitting .400'])**counts).product(),\
        'Anyone Hitting .400 (Random AB)':1 - ((1 - by_avg.loc[(by_avg.Type == 'Random AB') & \
        (by_avg.Games == games),'Probability of Hitting .400'])**counts).product(),\
        'Anyone Hitting .400 (Player AB)':1 - (1 - by_player.loc[by_player.Games == games,\
        'Probability of Hitting .400']).product()},ignore_index=True)
    
    """ Sorting and saving results to Excel spreadsheet """
    if options.excel:
        writer = pd.ExcelWriter('FourHundredProbByCareerAvg.xlsx',engine='xlsxwriter')
        writer = excelAutofit(any_player.sort_values(by='# of Games',ascending=True),'Any Player',writer)
        writer = excelAutofit(by_avg.sort_values(by=['Type','Games','Career'],ascending=True),'By Career Avg',writer)
        writer = excelAutofit(by_player.sort_values(by=['Games','Probability of Hitting .400'],ascending=[True,False]),'By Player',writer)
        writer = excelAutofit(avg_hist.sort_values(by=['Games','Career','Season'],ascending=True),'Season Avg Prob',writer)
        writer.sheets['Any Player'].conditional_format('B2:D' + str(any_player.shape[0] + 1),\
        {'type':'3_color_scale','min_color':'#FF6347','mid_color':'#FFD700','max_color':'#3CB371'})
        writer.save()
    
    """ Plotting interactive html graphs of results """
    if options.graph:
        by_avg["Probability of Hitting .400"] *= 100
        by_avg["Career"] *= 1000
        by_avg = by_avg.rename(columns={"Career":"Career Batting Average",\
        "Probability of Hitting .400":"Percent Probability of Hitting .400"})
        fig = px.scatter(by_avg,x="Career Batting Average",y="Percent Probability of Hitting .400",\
        color="Type",hover_name="Type",animation_frame='Games',range_x=[200,400],range_y=[0,50])
        plot(fig,filename='FourHundredProbByCareerAvg.html')
        avg_hist['Probability'] *= 100
        avg_hist['Career'] = '.' + (1000*avg_hist['Career']).astype(int).astype(str)
        avg_hist['Season'] *= 1000
        avg_hist = avg_hist.rename(columns={"Career":"Career Batting Average",\
        "Season":"Season Batting Average","Probability":"Percent Probability"})
        fig = px.scatter(avg_hist,x="Season Batting Average",y="Percent Probability",\
        color='Career Batting Average',animation_frame='Games',range_x=[100,500],range_y=[0,10])
        plot(fig,filename='SeasonAvgDistributions.html')

if __name__ == "__main__":
    main()




