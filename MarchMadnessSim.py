#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 19:52:05 2019

@author: firman.taylor
"""

import pandas as pd
import numpy as np
import datetime
import os
import warnings
warnings.filterwarnings("ignore")
import plotly.graph_objs as graph_objs
from plotly.offline import init_notebook_mode, plot
init_notebook_mode()

numSims = 10000
winners = {'mens':{'2019':'Virginia','2018':'Villanova','2017':'North Carolina'},\
           'womens':{'2019':'Baylor','2018':'Notre Dame','2017':'South Carolina'}}
runnersUp = {'mens':{'2019':'Texas Tech','2018':'Michigan','2017':'Gonzaga'},\
             'womens':{'2019':'Notre Dame','2018':'Mississippi State','2017':'Mississippi State'}}
startDate = {'mens':{'2019':'2019-03-20','2018':'2018-03-14','2017':'2017-03-15'},\
             'womens':{'2019':'2019-03-17','2018':'2018-03-12','2017':'2017-03-12'}}
endDate = {'mens':{'2019':'2019-04-06','2018':'2018-03-31','2017':'2017-04-01'},\
           'womens':{'2019':'2019-04-05','2018':'2018-03-30','2017':'2017-03-31'}}
regionRank = {'mens':{'2019':['East','South','Midwest','West'],\
                      '2018':['South','East','Midwest','West'],\
                      '2017':['East','Midwest','South','West']},\
              'womens':{'2019':['Greensboro','Chicago','Albany','Portland'],\
                        '2018':['Albany','Kansas City','Lexington','Spokane'],\
                        '2017':['Bridgeport','Lexington','Stockton','Oklahoma City']}}
colors = ['blue','green','orange','red']
genders = ['mens','womens']
seasons = [str(year) for year in range(2017,2020)]

data = []
relData = []
for gender in genders:
    relative = []
    for season in seasons:
        tournyProbs = pd.read_csv('fivethirtyeight_ncaa_forecasts_' + season + '.csv')
        outcomes = tournyProbs.loc[(tournyProbs.gender == gender) & \
        (tournyProbs.forecast_date == endDate[gender][season]) & (tournyProbs.rd1_win == 1)]
        outcomes.loc[outcomes.team_name == winners[gender][season],'rd7_win'] = 1.0
        outcomes.loc[outcomes.team_name == runnersUp[gender][season],'rd7_win'] = 0.0
        outcomes['team_seed'] = outcomes['team_seed'].str.replace('a','').str.replace('b','')
        
        if os.path.exists('MarchMadnessSims_' + gender.title() + '_' + season + '.csv'):
            simulations = pd.read_csv('MarchMadnessSims_' + gender.title() + '_' + season + '.csv')
        else:
            simulations = pd.DataFrame(columns=['Type','FirstRound','SecondRound',\
            'SweetSixteen','EliteEight','FinalFour','Championship'])
        
        for numSim in range(simulations.loc[simulations.Type == 'FiveThirtyEight'].shape[0],numSims):
            if (numSim + 1)%10 == 0:
                print('Sim #' + str(numSim + 1) + ', ' + str(datetime.datetime.now()))
                simulations.to_csv('MarchMadnessSims_' + gender.title() + '_' + season + '.csv',index=False)
            
            """ FiveThirtyEight Simulation """
            
            initProbs = tournyProbs.loc[(tournyProbs.gender == gender) & \
            (tournyProbs.forecast_date == startDate[gender][season]) & (tournyProbs.rd1_win == 1)]
            initProbs['team_seed'] = initProbs['team_seed'].str.replace('a','').str.replace('b','')
            pointVals = {'Type':'FiveThirtyEight'}
            
            """ Round of 64 """
            for region in outcomes.team_region.unique():
                for seed in range(1,9):
                    topRating = initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(seed)),'team_rating'].sum()
                    bottomRating = initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(17 - seed)),'team_rating'].sum()
                    pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(seed)),'rd2_sim'] = int(outcome < pureProb)
                    initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(17 - seed)),'rd2_sim'] = int(outcome >= pureProb)
                    del topRating, bottomRating, pureProb, outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd2_sim']],right=outcomes[['team_id','rd2_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['FirstRound'] = (results.rd2_sim*results.rd2_win*10).sum()
            
            """ Round of 32 """
            initProbs = initProbs.loc[initProbs.rd2_sim == 1]
            for region in outcomes.team_region.unique():
                for seed in range(1,5):
                    topRating = initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed)]),'team_rating'].sum()
                    bottomRating = initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(9 - seed),str(8 + seed)]),'team_rating'].sum()
                    pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed)]),'rd3_sim'] = int(outcome < pureProb)
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(9 - seed),str(8 + seed)]),'rd3_sim'] = int(outcome >= pureProb)
                    del topRating, bottomRating, pureProb, outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd3_sim']],right=outcomes[['team_id','rd3_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['SecondRound'] = (results.rd3_sim*results.rd3_win*20).sum()
        
            """ Sweet Sixteen """
            initProbs = initProbs.loc[initProbs.rd3_sim == 1]
            for region in outcomes.team_region.unique():
                for seed in range(1,3):
                    topRating = initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed),str(9 - seed),str(8 + seed)]),'team_rating'].sum()
                    bottomRating = initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(5 - seed),str(4 + seed),str(13 - seed),str(12 + seed)]),'team_rating'].sum()
                    pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed),str(9 - seed),str(8 + seed)]),'rd4_sim'] = int(outcome < pureProb)
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(5 - seed),str(4 + seed),str(13 - seed),str(12 + seed)]),'rd4_sim'] = int(outcome >= pureProb)
                    del topRating, bottomRating, pureProb, outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd4_sim']],right=outcomes[['team_id','rd4_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['SweetSixteen'] = (results.rd4_sim*results.rd4_win*40).sum()
            
            """ Elite Eight """
            initProbs = initProbs.loc[initProbs.rd4_sim == 1]
            for region in outcomes.team_region.unique():
                topTeam = initProbs.loc[initProbs.team_region == region,'team_name'].tolist()[0]
                topRating = initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == topTeam),'team_rating'].tolist()[0]
                bottomTeam = initProbs.loc[initProbs.team_region == region,'team_name'].tolist()[1]
                bottomRating = initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == bottomTeam),'team_rating'].tolist()[0]
                pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
                outcome = np.random.rand()
                initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == topTeam),'rd5_sim'] = int(outcome < pureProb)
                initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == bottomTeam),'rd5_sim'] = int(outcome >= pureProb)
                del topTeam, topRating, bottomTeam, bottomRating, pureProb, outcome
            del region
            results = pd.merge(left=initProbs[['team_id','team_name','rd5_sim']],right=outcomes[['team_id','rd5_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['EliteEight'] = (results.rd5_sim*results.rd5_win*80).sum()
            
            """ Final Four """
            initProbs = initProbs.loc[initProbs.rd5_sim == 1]
            topRating = initProbs.loc[initProbs.team_region == regionRank[gender][season][0],'team_rating'].tolist()[0]
            bottomRating = initProbs.loc[initProbs.team_region == regionRank[gender][season][3],'team_rating'].tolist()[0]
            pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region == regionRank[gender][season][0],'rd6_sim'] = int(outcome < pureProb)
            initProbs.loc[initProbs.team_region == regionRank[gender][season][3],'rd6_sim'] = int(outcome >= pureProb)
            topRating = initProbs.loc[initProbs.team_region == regionRank[gender][season][1],'team_rating'].tolist()[0]
            bottomRating = initProbs.loc[initProbs.team_region == regionRank[gender][season][2],'team_rating'].tolist()[0]
            pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region == regionRank[gender][season][1],'rd6_sim'] = int(outcome < pureProb)
            initProbs.loc[initProbs.team_region == regionRank[gender][season][2],'rd6_sim'] = int(outcome >= pureProb)
            del topRating, bottomRating, pureProb, outcome
            results = pd.merge(left=initProbs[['team_id','team_name','rd6_sim']],right=outcomes[['team_id','rd6_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['FinalFour'] = (results.rd6_sim*results.rd6_win*160).sum()
            
            """ National Championship """
            initProbs = initProbs.loc[initProbs.rd6_sim == 1]
            topRating = initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][0],regionRank[gender][season][3]]),'team_rating'].tolist()[0]
            bottomRating = initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][1],regionRank[gender][season][2]]),'team_rating'].tolist()[0]
            pureProb = 1/(1+10**(30.464*(bottomRating - topRating)/400))
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][0],regionRank[gender][season][3]]),'rd7_sim'] = int(outcome < pureProb)
            initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][1],regionRank[gender][season][2]]),'rd7_sim'] = int(outcome >= pureProb)
            del topRating, bottomRating, pureProb, outcome
            results = pd.merge(left=initProbs[['team_id','team_name','rd7_sim']],right=outcomes[['team_id','rd7_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['Championship'] = (results.rd7_sim*results.rd7_win*320).sum()
            simulations = simulations.append(pointVals,ignore_index=True)
            del pointVals
            
            """ Coin Flip Simulation """
            
            initProbs = tournyProbs.loc[(tournyProbs.gender == gender) & \
            (tournyProbs.forecast_date == startDate[gender][season]) & (tournyProbs.rd1_win == 1)]
            initProbs['team_seed'] = initProbs['team_seed'].str.replace('a','').str.replace('b','')
            initProbs['team_rating'] = initProbs['team_rating'].mean()
            pointVals = {'Type':'CoinFlip'}
            
            """ Round of 64 """
            for region in outcomes.team_region.unique():
                for seed in range(1,9):
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(seed)),'rd2_sim'] = int(outcome < 0.5)
                    initProbs.loc[(initProbs.team_region == region) & (initProbs.team_seed == str(17 - seed)),'rd2_sim'] = int(outcome >= 0.5)
                    del outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd2_sim']],right=outcomes[['team_id','rd2_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['FirstRound'] = (results.rd2_sim*results.rd2_win*10).sum()
        
            """ Round of 32 """
            initProbs = initProbs.loc[initProbs.rd2_sim == 1]
            for region in outcomes.team_region.unique():
                for seed in range(1,5):
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed)]),'rd3_sim'] = int(outcome < 0.5)
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(9 - seed),str(8 + seed)]),'rd3_sim'] = int(outcome >= 0.5)
                    del outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd3_sim']],right=outcomes[['team_id','rd3_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['SecondRound'] = (results.rd3_sim*results.rd3_win*20).sum()
        
            """ Sweet Sixteen """
            initProbs = initProbs.loc[initProbs.rd3_sim == 1]
            for region in outcomes.team_region.unique():
                for seed in range(1,3):
                    outcome = np.random.rand()
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(seed),str(17 - seed),str(9 - seed),str(8 + seed)]),'rd4_sim'] = int(outcome < 0.5)
                    initProbs.loc[(initProbs.team_region == region) & initProbs.team_seed.isin([str(5 - seed),str(4 + seed),str(13 - seed),str(12 + seed)]),'rd4_sim'] = int(outcome >= 0.5)
                    del outcome
                del seed
            del region
            results = pd.merge(left=initProbs[['team_id','rd4_sim']],right=outcomes[['team_id','rd4_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['SweetSixteen'] = (results.rd4_sim*results.rd4_win*40).sum()
        
            """ Elite Eight """
            initProbs = initProbs.loc[initProbs.rd4_sim == 1]
            for region in outcomes.team_region.unique():
                outcome = np.random.rand()
                topTeam = initProbs.loc[initProbs.team_region == region,'team_name'].tolist()[0]
                bottomTeam = initProbs.loc[initProbs.team_region == region,'team_name'].tolist()[1]
                initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == topTeam),'rd5_sim'] = int(outcome < 0.5)
                initProbs.loc[(initProbs.team_region == region) & (initProbs.team_name == bottomTeam),'rd5_sim'] = int(outcome >= 0.5)
                del topTeam, bottomTeam, outcome
            del region
            results = pd.merge(left=initProbs[['team_id','team_name','rd5_sim']],right=outcomes[['team_id','rd5_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['EliteEight'] = (results.rd5_sim*results.rd5_win*80).sum()
            
            """ Final Four """
            initProbs = initProbs.loc[initProbs.rd5_sim == 1]
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region == regionRank[gender][season][0],'rd6_sim'] = int(outcome < 0.5)
            initProbs.loc[initProbs.team_region == regionRank[gender][season][3],'rd6_sim'] = int(outcome >= 0.5)
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region == regionRank[gender][season][1],'rd6_sim'] = int(outcome < 0.5)
            initProbs.loc[initProbs.team_region == regionRank[gender][season][2],'rd6_sim'] = int(outcome >= 0.5)
            del outcome
            results = pd.merge(left=initProbs[['team_id','team_name','rd6_sim']],right=outcomes[['team_id','rd6_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['FinalFour'] = (results.rd6_sim*results.rd6_win*160).sum()
            
            """ National Championship """
            initProbs = initProbs.loc[initProbs.rd6_sim == 1]
            outcome = np.random.rand()
            initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][0],regionRank[gender][season][3]]),'rd7_sim'] = int(outcome < 0.5)
            initProbs.loc[initProbs.team_region.isin([regionRank[gender][season][1],regionRank[gender][season][2]]),'rd7_sim'] = int(outcome >= 0.5)
            del outcome
            results = pd.merge(left=initProbs[['team_id','team_name','rd7_sim']],right=outcomes[['team_id','rd7_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals['Championship'] = (results.rd7_sim*results.rd7_win*320).sum()
            simulations = simulations.append(pointVals,ignore_index=True)
            del pointVals
        
        if 'Chalk' not in simulations.Type.unique():
            initProbs = tournyProbs.loc[(tournyProbs.gender == gender) & \
            (tournyProbs.forecast_date == startDate[gender][season]) & (tournyProbs.rd1_win == 1)]
            initProbs['team_seed'] = initProbs['team_seed'].str.replace('a','').str.replace('b','')
            initProbs.loc[initProbs.team_seed.astype(int) <= 8,'rd2_sim'] = 1
            initProbs.loc[initProbs.team_seed.astype(int) > 8,'rd2_sim'] = 0
            initProbs.loc[initProbs.team_seed.astype(int) <= 4,'rd3_sim'] = 1
            initProbs.loc[initProbs.team_seed.astype(int) > 4,'rd3_sim'] = 0
            initProbs.loc[initProbs.team_seed.astype(int) <= 2,'rd4_sim'] = 1
            initProbs.loc[initProbs.team_seed.astype(int) > 2,'rd4_sim'] = 0
            initProbs.loc[initProbs.team_seed.astype(int) == 1,'rd5_sim'] = 1
            initProbs.loc[initProbs.team_seed.astype(int) != 1,'rd5_sim'] = 0
            initProbs.loc[(initProbs.team_seed.astype(int) == 1) & (initProbs.team_region == regionRank[gender][season][0]),'rd6_sim'] = 1
            initProbs.loc[(initProbs.team_seed.astype(int) != 1) | (initProbs.team_region != regionRank[gender][season][0]),'rd6_sim'] = 0
            initProbs.loc[(initProbs.team_seed.astype(int) == 1) & (initProbs.team_region == regionRank[gender][season][1]),'rd6_sim'] = 1
            initProbs.loc[(initProbs.team_seed.astype(int) == 1) & (initProbs.team_region != regionRank[gender][season][1]),'rd6_sim'] = 0
            initProbs.loc[(initProbs.team_seed.astype(int) == 1) & (initProbs.team_region == regionRank[gender][season][0]),'rd7_sim'] = 1
            initProbs.loc[(initProbs.team_seed.astype(int) != 1) | (initProbs.team_region != regionRank[gender][season][0]),'rd7_sim'] = 0
            results = pd.merge(left=initProbs[['team_id','rd2_sim','rd3_sim','rd4_sim','rd5_sim','rd6_sim','rd7_sim']],\
            right=outcomes[['team_id','rd2_win','rd3_win','rd4_win','rd5_win','rd6_win','rd7_win']],how='inner',left_on='team_id',right_on='team_id')
            pointVals = {'Type':'Chalk'}
            pointVals['FirstRound'] = (results.rd2_sim*results.rd2_win*10).sum()
            pointVals['SecondRound'] = (results.rd3_sim*results.rd3_win*20).sum()
            pointVals['SweetSixteen'] = (results.rd4_sim*results.rd4_win*40).sum()
            pointVals['EliteEight'] = (results.rd5_sim*results.rd5_win*80).sum()
            pointVals['FinalFour'] = (results.rd6_sim*results.rd6_win*160).sum()
            pointVals['Championship'] = (results.rd7_sim*results.rd7_win*320).sum()
            simulations = simulations.append(pointVals,ignore_index=True)
            del pointVals
        
        simulations['Total'] = simulations['FirstRound'] + simulations['SecondRound'] + simulations['SweetSixteen'] + \
        simulations['EliteEight'] + simulations['FinalFour'] + simulations['Championship']
        simulations.to_csv('MarchMadnessSims_' + gender.title() + '_' + season + '.csv',index=False)
        
        points_538Hist,points_538Inds = np.histogram(simulations.loc[simulations.Type == 'FiveThirtyEight','Total'],bins=np.arange(0,320*6 + 11,10) - 5)
        points_538Hist = points_538Hist/np.sum(points_538Hist)
        points_538Inds = points_538Inds[:-1] + 5
        points_CoinHist,points_CoinInds = np.histogram(simulations.loc[simulations.Type == 'CoinFlip','Total'],bins=np.arange(0,320*6 + 11,10) - 5)
        points_CoinHist = points_CoinHist/np.sum(points_CoinHist)
        points_CoinInds = points_CoinInds[:-1] + 5
        if len(data) == 0 or len(data) == len(seasons)*2 + 1:
            data.append(graph_objs.Scatter(
                x = points_CoinInds,
                y = 100*points_CoinHist,
                name = 'Coin Flip',
                legendgroup = 'a',
                showlegend = gender == 'mens',
                line = dict(width=4,color=colors[0]),
                xaxis='x' + str(genders.index(gender) + 1),yaxis='y' + str(genders.index(gender) + 1)
            ))
        data.append(graph_objs.Scatter(
            x = points_538Inds,
            y = 100*points_538Hist,
            name = '538 Odds, ' + season,
            legendgroup = chr(98 + seasons.index(season)),
            showlegend = gender == 'mens',
            line = dict(width=4,color=colors[seasons.index(season) + 1]),
            xaxis='x' + str(genders.index(gender) + 1),yaxis='y' + str(genders.index(gender) + 1)
        ))
        data.append(graph_objs.Scatter(
            x = [simulations.loc[simulations.Type == 'Chalk','Total'].sum(),\
                 simulations.loc[simulations.Type == 'Chalk','Total'].sum()],
            y = [0,10],
            name = 'Chalk, ' + season,
            legendgroup = chr(98 + seasons.index(season)),
            showlegend = gender == 'mens',
            line = dict(width=4,color=colors[seasons.index(season) + 1],dash='dash'),
            xaxis='x' + str(genders.index(gender) + 1),yaxis='y' + str(genders.index(gender) + 1)
        ))
        relative.extend(simulations.loc[simulations.Type == 'FiveThirtyEight','Total']/\
        simulations.loc[simulations.Type == 'Chalk','Total'].sum())
        del points_538Hist, points_538Inds, points_CoinHist, points_CoinInds, simulations
    del season
    
    points_RelHist,points_RelInds = np.histogram(relative,bins=np.arange(0,2.06,0.05) - 0.025)
    points_RelHist = points_RelHist/np.sum(points_RelHist)
    points_RelInds = points_RelInds[:-1] + 0.025
    
    relData.append(graph_objs.Scatter(
        x = points_RelInds,
        y = np.round(100*points_RelHist,1),
        name = gender.title()[:-1] + "'s",
        legendgroup = chr(97 + genders.index(gender)),
        line = dict(width=4,color=colors[genders.index(gender)]),
    ))
    del relative
    
del gender

layout = dict(xaxis=dict(title='Points',range=[-100,2100],dtick=500,domain=[0,0.45]),
              yaxis=dict(title='% of Brackets',range=[-0.5,6.5],dtick=2,anchor='x1'),
              xaxis2=dict(title='Points',range=[-100,2100],dtick=500,domain=[0.55,1]),
              yaxis2=dict(title='% of Brackets',range=[-0.5,6.5],dtick=2,anchor='x2'),
              legend=dict(x=0.9,y=1),height=400,width=900,
              margin=graph_objs.layout.Margin(l=50,r=50,b=100,t=50),
              annotations=[{"x": 0.225, "y": 1.0,
                            "font": {"size": 16}, "showarrow": False, 
                            "text": "Men's Tournament", 
                            "xanchor": "center", "xref": "paper", 
                            "yanchor": "bottom", "yref": "paper"},
                           {"x": 0.775, "y": 1.0, 
                            "font": {"size": 16}, "showarrow": False, 
                            "text": "Women's Tournament", 
                            "xanchor": "center", "xref": "paper", 
                            "yanchor": "bottom", "yref": "paper"}])

fig = dict(data=data, layout=layout)
plot(fig, filename='MarchMadness_PointDistribution.html')#,auto_open=False)
del data, layout, fig

relData.append(graph_objs.Scatter(
    x = [1,1],y = [0,20],name = "Chalk",showlegend=False,
    legendgroup = 'c',line = dict(width=4,color='black'),
))

layout = dict(xaxis=dict(title='538-to-Chalk Ratio',range=[-0.1,2.1],dtick=0.5),
              yaxis=dict(title='% of Brackets',range=[-2,14],dtick=4),
              legend=dict(x=0.8,y=1),height=400,width=600,
              margin=graph_objs.layout.Margin(l=50,r=50,b=100,t=50))

fig = dict(data=relData, layout=layout)
plot(fig, filename='MarchMadness_RelativePoints.html')#,auto_open=False)
del relData, layout, fig




