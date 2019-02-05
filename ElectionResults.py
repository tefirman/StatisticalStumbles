#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 09:56:30 2019

@author: firman.taylor
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

byDistrict = pd.DataFrame(columns=['State','District','Year','Name',\
'Votes_House_R','Votes_House_D','Votes_House_O',\
'Wins_House_R','Wins_House_D','Wins_House_O',\
'Votes_Senate_R','Votes_Senate_D','Votes_Senate_O',\
'Wins_Senate_R','Wins_Senate_D','Wins_Senate_O',\
'Votes_Senate_R_Cumulative','Votes_Senate_D_Cumulative','Votes_Senate_O_Cumulative',\
'Wins_Senate_R_Cumulative','Wins_Senate_D_Cumulative','Wins_Senate_O_Cumulative'])

states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL',\
'IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',\
'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX',\
'UT','VT','VA','WA','WV','WI','WY']
redParties = ['R','REP','R/TRP','R/IP','R/CRV/IDP/TRPCombinedParties',\
'R/CRVCombinedParties','R/CRV/IDPCombinedParties','R/IDPCombinedParties',\
'REP*','R/C/IDP/RTL','R/IDP/C','R/C','R/C/RTL','RandR/D','RE','REP/W***','REP ','REPE','N']
blueParties = ['D','DEM','DFL','D/IP','D/PRO/WF/IP','D/WF*','D/PRO/WF*',\
'D/L','D*','D/IND','D/WFCombinedParties','D/WF/IDPCombinedParties','DEM ',\
'D/IDP/WFCombinedParties','D/WF','D/PRO/WF','DEM/PRO/WF','DNL','W(DEM)/DEM',\
'W(DEM)/DEM*','D/IDP/WF','D/IDP/L/WF','D/L/WF','D/IDP/C/WF','WF','DEM/IP/PRO/WF']

for year in range(2000,2017,2):
    print(year)
    
    results_S = pd.read_csv('ElectionResults/SenateResults_' + str(year) + '.csv',encoding='latin2',engine='python')
    for state in states:
        results_S['STATE ABBREVIATION'] = results_S['STATE ABBREVIATION'].str.replace(state + ' ',state).str.replace(' ' + state,state)
    del state
    results_S = results_S.loc[results_S['STATE ABBREVIATION'].isin(states)]
    results_S = results_S.loc[~results_S['CANDIDATE NAME'].isnull() & ~results_S['CANDIDATE NAME'].isin([' ','  ','   '])]
    results_S.D = results_S.D.astype('str')
    results_S = results_S.loc[results_S.D.str.contains('S')]
    results_S.PARTY = results_S.PARTY.str.replace('Ę','E')
    results_S.loc[results_S['GENERAL VOTES '].isin(['#','##',' ']),'GENERAL VOTES '] = '0'
    results_S['GENERAL VOTES '] = results_S['GENERAL VOTES '].str.replace(',','').str.replace('[','').str.replace(']','').str.replace(' ','').astype(float)
    results_S.loc[results_S['GENERAL VOTES '].isnull(),'GENERAL VOTES '] = 0.0
    if year in [2000,2010]:
        results_S['GE RUNOFF'] = None
    else:
        results_S['GE RUNOFF'] = results_S['GE RUNOFF'].str.replace(',','').str.replace('[','').str.replace(']','').str.replace(' ','').astype(float)
    if year in [2000,2002,2004]:
        results_S['COMBINED % (CT, NY, SC)'] = '0.0%'
    for state in results_S['STATE ABBREVIATION'].unique():
        stateVals = results_S.loc[results_S['STATE ABBREVIATION'] == state]
        for candidate in stateVals['CANDIDATE NAME'].unique():
            if stateVals.loc[stateVals['CANDIDATE NAME'] == candidate].shape[0] > 1:
                candidateVals = stateVals.loc[stateVals['CANDIDATE NAME'] == candidate]
                if np.any([party in blueParties for party in candidateVals.PARTY.unique()]):
                    results_S.loc[candidateVals.index[0],'PARTY'] = 'DEM'
                elif np.any([party in redParties for party in candidateVals.PARTY.unique()]):
                    results_S.loc[candidateVals.index[0],'PARTY'] = 'REP'
                else:
                    results_S.loc[candidateVals.index[0],'PARTY'] = 'IDP'
                results_S.loc[candidateVals.index[0],'GENERAL VOTES '] = candidateVals['GENERAL VOTES '].sum()
                results_S = results_S.drop(candidateVals.index[1:])
                del candidateVals
                stateVals = results_S.loc[results_S['STATE ABBREVIATION'] == state]
        if year in [2000,2002,2004,2006,2008,2010]:
            if year == 2008 and state in ['MS','WY']:
                for race in stateVals.D.unique():
                    raceVals = stateVals.loc[stateVals.D == race]
                    results_S.loc[results_S['GENERAL VOTES '] == raceVals['GENERAL VOTES '].max(),'GE WINNER INDICATOR'] = 'W'
                    del raceVals
                del race
            elif np.any(~stateVals['GE RUNOFF'].isnull()):
                results_S.loc[np.all([results_S['STATE ABBREVIATION'] == state,results_S.D.str.contains('S'),\
                results_S['GE RUNOFF'] == stateVals['GE RUNOFF'].max()],axis=0),'GE WINNER INDICATOR'] = 'W'
            elif stateVals.loc[stateVals['COMBINED % (CT, NY, SC)'].str[:-1].astype(float) > 50].shape[0] > 1:
                results_S.loc[stateVals.loc[stateVals['COMBINED % (CT, NY, SC)'].str[:-1].astype(float) > 50].index,'GE WINNER INDICATOR'] = 'W'
            else:
                results_S.loc[np.all([results_S['STATE ABBREVIATION'] == state,results_S.D.str.contains('S'),\
                results_S['GENERAL VOTES '] == stateVals['GENERAL VOTES '].max()],axis=0),'GE WINNER INDICATOR'] = 'W'
        del stateVals
    del state
    del candidate
    
    results_S['GE WINNER INDICATOR'] = results_S['GE WINNER INDICATOR'].astype(str)
    results_S.loc[results_S['GE WINNER INDICATOR'] == 'W (Runoff)','GE WINNER INDICATOR'] = 'W'
    
    results_H = pd.read_csv('ElectionResults/HouseResults_' + str(year) + '.csv',encoding='latin2',engine='python')
    for state in states:
        results_H['STATE ABBREVIATION'] = results_H['STATE ABBREVIATION'].str.replace(state + ' ',state).str.replace(' ' + state,state)
    del state
    results_H = results_H.loc[results_H['STATE ABBREVIATION'].isin(states)]
    results_H = results_H.loc[~results_H['CANDIDATE NAME'].isnull()]
    results_H.D = results_H.D.astype('str')
    results_H = results_H.loc[~results_H.D.str.contains('UNEXPIRED TERM')]
    results_H = results_H.loc[~results_H.D.isin(['03*','13*','18*','22*'])]
    results_H = results_H.loc[results_H.D != 'H']
    results_H = results_H.loc[~results_H.D.str.contains('S')]
    if year >= 2002:
        results_H = results_H.loc[~results_H['TOTAL VOTES'].isin(['Total Party Votes:','Total District Votes:'])]
    results_H.D = results_H.D.str.replace(' - FULL TERM','')
    results_H.D = results_H.D.str.replace(' ','')
    results_H = results_H.loc[~results_H.PARTY.isnull()]
    results_H.PARTY = results_H.PARTY.str.replace(' ','').str.replace('Ę','').str.replace('ć','').str.replace('ž','')
    results_H.loc[np.all([results_H.PARTY == 'D/R',results_H['CANDIDATE NAME'] == 'Shuster, Bud'],axis=0),'PARTY'] = 'R'
    results_H.loc[np.all([results_H.PARTY == 'D/R',results_H['CANDIDATE NAME'] == 'Welch, Peter'],axis=0),'PARTY'] = 'D'
    results_H.loc[results_H['GENERAL VOTES '].isin(['Unopposed','#','??','Withdrew -- after primary?','Unopposed   ',' ']),'GENERAL VOTES '] = '0'
    results_H['GENERAL VOTES '] = results_H['GENERAL VOTES '].str.replace(',','').str.replace('[','').str.replace(']','').str.replace(' ','').astype(float)
    
    if year in [2000,2002,2004,2006,2008,2010]:
        if year in [2000,2010]:
            results_H['GE RUNOFF'] = 'NaN'
        results_H['GE RUNOFF'] = results_H['GE RUNOFF'].str.replace(',','').str.replace(' ','')
        results_H.loc[results_H['GE RUNOFF'] == '','GE RUNOFF'] = float('NaN')
        results_H['GE RUNOFF'] = results_H['GE RUNOFF'].astype(float)
        results_H['GE WINNER INDICATOR'] = ''
        for state in results_H['STATE ABBREVIATION'].unique():
            for district in results_H.loc[results_H['STATE ABBREVIATION'] == state,'D'].unique():
                districtVals = results_H.loc[np.all([results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0)]
                if state in ['CT','NY','SC'] and districtVals['CANDIDATE NAME'].unique().shape[0] < districtVals['CANDIDATE NAME'].shape[0]:
                    for candidate in districtVals['CANDIDATE NAME'].unique():
                        if districtVals.loc[districtVals['CANDIDATE NAME'] == candidate].shape[0] > 1:
                            candidateVals = districtVals.loc[districtVals['CANDIDATE NAME'] == candidate]
                            if 'DEM' in candidateVals.PARTY.unique() or 'D' in candidateVals.PARTY.unique():
                                results_H.loc[candidateVals.index[0],'PARTY'] = 'DEM'
                            elif 'REP' in candidateVals.PARTY.unique() or 'R' in candidateVals.PARTY.unique():
                                results_H.loc[candidateVals.index[0],'PARTY'] = 'REP'
                            else:
                                results_H.loc[candidateVals.index[0],'PARTY'] = 'IDP'
                            results_H.loc[candidateVals.index[0],'GENERAL VOTES '] = candidateVals['GENERAL VOTES '].sum()
                            results_H = results_H.drop(candidateVals.index[1:])
                            del candidateVals
                    del candidate
                    districtVals = results_H.loc[np.all([results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0)]
                if np.any(~districtVals['GE RUNOFF'].isnull()):
                    results_H.loc[np.all([results_H['STATE ABBREVIATION'] == state,results_H.D == district,\
                    results_H['GE RUNOFF'] == districtVals['GE RUNOFF'].max()],axis=0),'GE WINNER INDICATOR'] = 'W'
                else:
                    results_H.loc[np.all([results_H['STATE ABBREVIATION'] == state,results_H.D == district,\
                    results_H['GENERAL VOTES '] == districtVals['GENERAL VOTES '].max()],axis=0),'GE WINNER INDICATOR'] = 'W'
                del districtVals
            del district
        del state
    results_H['GE WINNER INDICATOR'] = results_H['GE WINNER INDICATOR'].astype(str)
    
    for state in states:
        for district in results_H.loc[results_H['STATE ABBREVIATION'] == state,'D'].unique():
            byDistrict = byDistrict.append({'State':state,'District':district,'Year':year,\
            'Name':results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),'CANDIDATE NAME'].unique()[0].replace('','a'),\
            'Votes_House_R':results_H.loc[np.all([results_H['PARTY'].isin(redParties),\
            results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),'GENERAL VOTES '].sum(),\
            'Votes_House_D':results_H.loc[np.all([results_H['PARTY'].isin(blueParties),\
            results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),'GENERAL VOTES '].sum(),\
            'Votes_House_O':results_H.loc[np.all([~results_H['PARTY'].isin(np.append(redParties,blueParties)),\
            results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),'GENERAL VOTES '].sum(),\
            'Wins_House_R':float(results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H.PARTY.isin(redParties),results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0]),\
            'Wins_House_D':float(results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H.PARTY.isin(blueParties),results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0]),\
            'Wins_House_O':float(results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0] - \
            results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H.PARTY.isin(redParties),results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0] - \
            results_H.loc[np.all([results_H['GE WINNER INDICATOR'].str.contains('W'),\
            results_H.PARTY.isin(blueParties),results_H['STATE ABBREVIATION'] == state,results_H.D == district],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0]),\
            'Votes_Senate_R':results_S.loc[np.all([results_S['PARTY'].isin(redParties),\
            results_S['STATE ABBREVIATION'] == state],axis=0),'GENERAL VOTES '].sum(),\
            'Votes_Senate_D':results_S.loc[np.all([results_S['PARTY'].isin(blueParties),\
            results_S['STATE ABBREVIATION'] == state],axis=0),'GENERAL VOTES '].sum(),\
            'Votes_Senate_O':results_S.loc[np.all([~results_S['PARTY'].isin(np.append(redParties,blueParties)),\
            results_S['STATE ABBREVIATION'] == state],axis=0),'GENERAL VOTES '].sum(),\
            'Wins_Senate_R':float(results_S.loc[np.all([results_S['GE WINNER INDICATOR'].str.contains('W'),\
            results_S.PARTY.isin(redParties),results_S['STATE ABBREVIATION'] == state],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0]),\
            'Wins_Senate_D':float(results_S.loc[np.all([results_S['GE WINNER INDICATOR'].str.contains('W'),\
            results_S.PARTY.isin(blueParties),results_S['STATE ABBREVIATION'] == state],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0]),\
            'Wins_Senate_O':float(results_S.loc[np.all([results_S['GE WINNER INDICATOR'].str.contains('W'),\
            results_S['STATE ABBREVIATION'] == state],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0] - \
            results_S.loc[np.all([results_S['GE WINNER INDICATOR'].str.contains('W'),\
            results_S.PARTY.isin(redParties),results_S['STATE ABBREVIATION'] == state],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0] - \
            results_S.loc[np.all([results_S['GE WINNER INDICATOR'].str.contains('W'),\
            results_S.PARTY.isin(blueParties),results_S['STATE ABBREVIATION'] == state],axis=0),\
            ['CANDIDATE NAME','STATE ABBREVIATION','D']].drop_duplicates().shape[0])},ignore_index=True)
        del district
        
        if year >= 2004:
            if byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_R.mean() + \
            byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_D.mean() + \
            byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_O.mean() == 2:
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_R_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_R.mean()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_D_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_D.mean()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_O_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Wins_Senate_O.mean()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_R_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Votes_Senate_R.mean()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_D_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Votes_Senate_D.mean()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_O_Cumulative'] = \
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year)].Votes_Senate_O.mean()
            elif byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_R.mean().sum() + \
            byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_D.mean().sum() + \
            byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_O.mean().sum() == 2:
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_R_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_R.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_D_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_D.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_O_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_O.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_R_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_R.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_D_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_D.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_O_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 2,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_O.mean().sum()
            elif byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_R.mean().sum() + \
            byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_D.mean().sum() + \
            byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_O.mean().sum() == 2:
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_R_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_R.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_D_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_D.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_O_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Wins_Senate_O.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_R_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_R.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_D_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_D.mean().sum()
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_O_Cumulative'] = \
                byDistrict.loc[np.all([byDistrict.State == state,byDistrict.Year >= year - 4,byDistrict.Year <= year],axis=0)].groupby('Year').Votes_Senate_O.mean().sum()
            else:
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_R_Cumulative'] = 0
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_D_Cumulative'] = 0
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_O_Cumulative'] = 0
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_R_Cumulative'] = 0
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_D_Cumulative'] = 0
                byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_O_Cumulative'] = 0
                for temp in range(year - 4,year + 1):
                    totWins = byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_R.mean() + \
                    byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_D.mean() + \
                    byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_O.mean()
                    if totWins > 0:
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_R_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_R.mean()/totWins
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_D_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_D.mean()/totWins
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Wins_Senate_O_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Wins_Senate_O.mean()/totWins
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_R_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Votes_Senate_R.mean()/totWins
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_D_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Votes_Senate_D.mean()/totWins
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == year),'Votes_Senate_O_Cumulative'] += \
                        byDistrict.loc[(byDistrict.State == state) & (byDistrict.Year == temp)].Votes_Senate_O.mean()/totWins
                    del totWins
                del temp
    del state
    
    if year == 2004:
        """ Jim Jeffords (VT) switched parties in 2001... """
        byDistrict.loc[(byDistrict.Year == 2004) & (byDistrict.State == 'VT'),'Wins_Senate_R_Cumulative'] -= 1
        byDistrict.loc[(byDistrict.Year == 2004) & (byDistrict.State == 'VT'),'Wins_Senate_O_Cumulative'] += 1
    elif year == 2010:
        """ Ted Kennedy (MA) died and Republican Scott Brown won a special election """
        """ Other special elections occurred, but this is the only one that didn't occur on election day and switched parties """
        byDistrict.loc[(byDistrict.Year == 2010) & (byDistrict.State == 'MA'),'Wins_Senate_D_Cumulative'] -= 1
        byDistrict.loc[(byDistrict.Year == 2010) & (byDistrict.State == 'MA'),'Wins_Senate_R_Cumulative'] += 1
        byDistrict.loc[(byDistrict.Year == 2010) & (byDistrict.State == 'MA'),'Votes_Senate_D_Cumulative'] += 1060861 - 1500738
        byDistrict.loc[(byDistrict.Year == 2010) & (byDistrict.State == 'MA'),'Votes_Senate_R_Cumulative'] += 1168178 - 661532
        byDistrict.loc[(byDistrict.Year == 2010) & (byDistrict.State == 'MA'),'Votes_Senate_O_Cumulative'] += 24688 - 3220
    
    actual_S = pd.read_csv('ElectionResults/NetResults_Senate.csv')
    actual_H = pd.read_csv('ElectionResults/NetResults_House.csv')
    print('Wiki Senate Republican Wins: ' + str(actual_S.loc[actual_S.Year == year,'Republicans_Elected'].tolist()[0]))
    print('FEC Senate Republican Wins: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_R.mean().sum())))
    print('Wiki Senate Democrat Wins: ' + str(actual_S.loc[actual_S.Year == year,'Democrats_Elected'].tolist()[0]))
    print('FEC Senate Democrat Wins: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_D.mean().sum())))
    print('Wiki Senate Independent Wins: ' + str(actual_S.loc[actual_S.Year == year,'Other_Elected'].tolist()[0]))
    print('FEC Senate Independent Wins: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_O.mean().sum())))
    print('Wiki Senate Republicans: ' + str(actual_S.loc[actual_S.Year == year,'Republicans_Total'].tolist()[0]))
    print('FEC Senate Republicans: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_R_Cumulative.mean().sum())))
    print('Wiki Senate Democrats: ' + str(actual_S.loc[actual_S.Year == year,'Democrats_Total'].tolist()[0]))
    print('FEC Senate Democrats: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_D_Cumulative.mean().sum())))
    print('Wiki Senate Independents: ' + str(actual_S.loc[actual_S.Year == year,'Other_Total'].tolist()[0]))
    print('FEC Senate Independents: ' + str(int(byDistrict.loc[byDistrict.Year == year].groupby('State').Wins_Senate_O_Cumulative.mean().sum())))
    print('Wiki House Republicans: ' + str(actual_H.loc[actual_H.Year == year,'Republicans'].tolist()[0]))
    print('FEC House Republicans: ' + str(int(byDistrict.loc[byDistrict.Year == year,'Wins_House_R'].sum())))
    print('Wiki House Democrats: ' + str(actual_H.loc[actual_H.Year == year,'Democrats'].tolist()[0]))
    print('FEC House Democrats: ' + str(int(byDistrict.loc[byDistrict.Year == year,'Wins_House_D'].sum())))
    print('Wiki House Independents: ' + str(actual_H.loc[actual_H.Year == year,'Other'].tolist()[0]))
    print('FEC House Independents: ' + str(int(byDistrict.loc[byDistrict.Year == year,'Wins_House_O'].sum())))
    del actual_S
    del actual_H
    
    del results_S
    del results_H
del year

byDistrict.District = byDistrict.District.astype(float)
citylab = pd.read_csv('ElectionResults/citylab_cdi.csv')
citylab['State'],citylab['District'] = citylab.CD.str.split('-').str
citylab.loc[citylab.District == 'AL','District'] = '00'
citylab.District = citylab.District.astype(float)
byDistrict = pd.merge(left=byDistrict,right=citylab[['State','District','Cluster']],\
how='left',left_on=['State','District'],right_on=['State','District'])
byDistrict.loc[byDistrict.Cluster.isnull(),'Cluster'] = ''
byDistrict.loc[byDistrict.Cluster.isin(['Pure rural','Rural-suburban mix']),'Cluster'] = 'Rural'
byDistrict.loc[byDistrict.Cluster.isin(['Sparse suburban','Dense suburban']),'Cluster'] = 'Suburban'
byDistrict.loc[byDistrict.Cluster.isin(['Urban-suburban mix','Pure urban']),'Cluster'] = 'Urban'
del citylab

byDistrict['Votes_House_Total'] = byDistrict['Votes_House_R'] + byDistrict['Votes_House_D'] + byDistrict['Votes_House_O']
byDistrict['VotePct_House_R'] = byDistrict['Votes_House_R']/byDistrict['Votes_House_Total']
byDistrict['VotePct_House_D'] = byDistrict['Votes_House_D']/byDistrict['Votes_House_Total']
byDistrict['VotePct_House_O'] = byDistrict['Votes_House_O']/byDistrict['Votes_House_Total']
byDistrict['Power_House'] = 1000000/byDistrict['Votes_House_Total']
byDistrict.loc[byDistrict.Votes_House_Total == 0,'Power_House'] = float('NaN')

byDistrict['Votes_Senate_Total'] = byDistrict['Votes_Senate_R'] + byDistrict['Votes_Senate_D'] + byDistrict['Votes_Senate_O']
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'VotePct_Senate_R'] = \
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_R']/\
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_Total']
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'VotePct_Senate_D'] = \
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_D']/\
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_Total']
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'VotePct_Senate_O'] = \
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_O']/\
byDistrict.loc[byDistrict['Votes_Senate_Total'] > 0,'Votes_Senate_Total']
byDistrict['Wins_Senate_Total'] = byDistrict['Wins_Senate_R'] + byDistrict['Wins_Senate_D'] + byDistrict['Wins_Senate_O']
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'WinPct_Senate_R'] = \
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_R']/\
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_Total']
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'WinPct_Senate_D'] = \
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_D']/\
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_Total']
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'WinPct_Senate_O'] = \
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_O']/\
byDistrict.loc[byDistrict['Wins_Senate_Total'] > 0,'Wins_Senate_Total']
byDistrict['Votes_Senate_Total_Cumulative'] = byDistrict['Votes_Senate_R_Cumulative'] + \
byDistrict['Votes_Senate_D_Cumulative'] + byDistrict['Votes_Senate_O_Cumulative']
byDistrict['Power_Senate'] = 2*1000000/(byDistrict.Votes_Senate_Total_Cumulative/2)

byDistrict['Power_Total'] = byDistrict.Power_Senate*4.35 + byDistrict.Power_House

byDistrict = byDistrict.sort_values(by=['State','District','Year'])
byDistrict[['State','District','Year','Cluster','Power_House','Power_Senate','Power_Total']]\
.to_csv('ElectionResults/OverallResults_ByYearAndDistrict.csv',index=False)

""" SCATTER PLOT WITH POWER BY DISTRICT!!! """
""" Color code by urban/suburban/rural or representative party??? """
""" Check both and see which one is cooler... """
""" Histogram might be more illustrative... Not really... """

#plt.figure()
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Rural'),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Rural'),'Power_Senate'],'.')
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Suburban'),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Suburban'),'Power_Senate'],'.')
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Urban'),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Cluster == 'Urban'),'Power_Senate'],'.')
#plt.grid(True)
#plt.xlabel('House Power')
#plt.ylabel('Senate Power')

#ruralProb,inds = np.histogram(byDistrict.loc[(byDistrict.Year == 2016) & \
#(byDistrict.Cluster == 'Rural') & (~byDistrict.Power_Total.isnull()),'Power_Total'],np.arange(41))
#suburbanProb,inds = np.histogram(byDistrict.loc[(byDistrict.Year == 2016) & \
#(byDistrict.Cluster == 'Suburban') & (~byDistrict.Power_Total.isnull()),'Power_Total'],np.arange(41))
#urbanProb,inds = np.histogram(byDistrict.loc[(byDistrict.Year == 2016) & \
#(byDistrict.Cluster == 'Urban') & (~byDistrict.Power_Total.isnull()),'Power_Total'],np.arange(41))
#ruralProb = ruralProb/np.sum(ruralProb)
#suburbanProb = suburbanProb/np.sum(suburbanProb)
#urbanProb = urbanProb/np.sum(urbanProb)
#plt.figure()
#plt.plot(inds[:-1],100*ruralProb,inds[:-1],100*suburbanProb,inds[:-1],100*urbanProb)
#plt.grid(True)
#plt.xlabel('Total Power')
#plt.ylabel('Percentage')
#plt.legend(['Rural','Suburban','Urban'])

#plt.figure()
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_D == 1),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_D == 1),'Power_Senate'],'.b')
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_R == 1),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_R == 1),'Power_Senate'],'.r')
#plt.plot(byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_O == 1),'Power_House'],\
#byDistrict.loc[(byDistrict.Year == 2016) & (byDistrict.Wins_House_O == 1),'Power_Senate'],'.g')
#plt.grid(True)
#plt.xlabel('House Power')
#plt.ylabel('Senate Power')



byState = byDistrict.groupby(by=['State','Year']).agg({'Votes_House_R':'sum',\
'Votes_House_D':'sum','Votes_House_O':'sum','Votes_House_Total':'sum',\
'Wins_House_R':'sum','Wins_House_D':'sum','Wins_House_O':'sum',\
'Votes_Senate_R':'mean','Votes_Senate_D':'mean','Votes_Senate_O':'mean',\
'Votes_Senate_Total':'mean','Wins_Senate_R':'mean','Wins_Senate_D':'mean',\
'Wins_Senate_O':'mean','Wins_Senate_Total':'mean','VotePct_Senate_R':'mean',\
'VotePct_Senate_D':'mean','VotePct_Senate_O':'mean','WinPct_Senate_R':'mean',\
'WinPct_Senate_D':'mean','WinPct_Senate_O':'mean','Votes_Senate_R_Cumulative':'mean',\
'Votes_Senate_D_Cumulative':'mean','Votes_Senate_O_Cumulative':'mean',\
'Votes_Senate_Total_Cumulative':'mean','Wins_Senate_R_Cumulative':'mean',\
'Wins_Senate_D_Cumulative':'mean','Wins_Senate_O_Cumulative':'mean'}).reset_index()
byState['Wins_House_Total'] = byState['Wins_House_R'] + byState['Wins_House_D'] + byState['Wins_House_O']
byState['VotePct_House_R'] = byState['Votes_House_R']/byState['Votes_House_Total']
byState['VotePct_House_D'] = byState['Votes_House_D']/byState['Votes_House_Total']
byState['VotePct_House_O'] = byState['Votes_House_O']/byState['Votes_House_Total']
byState['WinPct_House_R'] = byState['Wins_House_R']/byState['Wins_House_Total']
byState['WinPct_House_D'] = byState['Wins_House_D']/byState['Wins_House_Total']
byState['WinPct_House_O'] = byState['Wins_House_O']/byState['Wins_House_Total']
byState['Diff_House_R'] = byState['VotePct_House_R'] - byState['WinPct_House_R']
byState['Diff_House_D'] = byState['VotePct_House_D'] - byState['WinPct_House_D']
byState['Diff_House_O'] = byState['VotePct_House_O'] - byState['WinPct_House_O']
byState['Err_House'] = byState['Diff_House_R']**2 + byState['Diff_House_D']**2 + byState['Diff_House_O']**2
byState['Power_House'] = 1000000*byState['Wins_House_Total']/byState['Votes_House_Total']
byState.loc[byState.Votes_House_Total == 0,'Power_House'] = float('NaN')
byState['Power_Senate'] = 1000000*2/(byState.Votes_Senate_Total_Cumulative/2)
byState['Power_Total'] = byState.Power_Senate*4.35 + byState.Power_House

presResults = pd.read_csv('ElectionResults/PresidentialResults_2016.csv')
presResults = presResults.loc[presResults['STATE ABBREVIATION'].isin(states) & (presResults['WINNER INDICATOR'] == 'W')]
presResults['CANDIDATE NAME'] = presResults['LAST NAME,  FIRST']
del presResults['LAST NAME,  FIRST']
presResults.loc[presResults['CANDIDATE NAME'].str.contains('Trump'),'PARTY'] = 'REP'
presResults.loc[presResults['CANDIDATE NAME'].str.contains('Clinton'),'PARTY'] = 'DEM'
byState = pd.merge(left=byState,right=presResults[['STATE ABBREVIATION','PARTY']],\
how='left',left_on='State',right_on='STATE ABBREVIATION')
stateAbbrevs = presResults[['STATE','STATE ABBREVIATION']].drop_duplicates()
stateAbbrevs.STATE = stateAbbrevs.STATE.str.upper()
demographics = pd.read_csv('ElectionResults/DemographicsByState_2016.csv')
demographics['Total Population'] = demographics['Total Population'].str.replace(',','').str.replace('-','0').astype(float)
demographics['Total Citizen Population'] = demographics['Total Citizen Population'].str.replace(',','').str.replace('-','0').astype(float)
demographics['Total registered'] = demographics['Total registered'].str.replace(',','').str.replace('-','0').astype(float)
demographics['Percent registered (Total)'] = demographics['Percent registered (Total)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
demographics['Percent registered (Citizen)'] = demographics['Percent registered (Citizen)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
demographics['Total voted'] = demographics['Total voted'].str.replace(',','').str.replace('-','0').astype(float)
demographics['Percent voted (Total)'] = demographics['Percent voted (Total)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
demographics['Percent voted (Citizen)'] = demographics['Percent voted (Citizen)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
demographics = pd.merge(left=demographics,right=stateAbbrevs,how='left',left_on='STATE',right_on='STATE')
demographics = demographics.loc[demographics['STATE ABBREVIATION'].isin(states)]
age = pd.read_csv('ElectionResults/AgeByState_2016.csv')
age['Total Population'] = age['Total Population'].str.replace(',','').str.replace('-','0').astype(float)
age['Total Citizen Population'] = age['Total Citizen Population'].str.replace(',','').str.replace('-','0').astype(float)
age['Total registered'] = age['Total registered'].str.replace(',','').str.replace('-','0').astype(float)
age['Percent registered (Total)'] = age['Percent registered (Total)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
age['Percent registered (Citizen)'] = age['Percent registered (Citizen)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
age['Total voted'] = age['Total voted'].str.replace(',','').str.replace('-','0').astype(float)
age['Percent voted (Total)'] = age['Percent voted (Total)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
age['Percent voted (Citizen)'] = age['Percent voted (Citizen)'].str.replace(',','').str.replace('-','0').str.replace('B','0').astype(float)
age = pd.merge(left=age,right=stateAbbrevs,how='left',left_on='STATE',right_on='STATE')
age = age.loc[age['STATE ABBREVIATION'].isin(states)]
for state in byState.State.unique():
    for demo in ['Male','Female','White alone or in combination','Black alone or in combination','Asian alone or in combination','Hispanic (of any race)']:
        byState.loc[(byState.State == state) & (byState.Year == 2016),demo.split(' ')[0]] = \
        demographics.loc[(demographics['STATE ABBREVIATION'] == state) & (demographics['Sex, Race and Hispanic-Origin'] == demo),'Total voted'].tolist()[0]/\
        demographics.loc[(demographics['STATE ABBREVIATION'] == state) & (demographics['Sex, Race and Hispanic-Origin'] == 'Total'),'Total voted'].tolist()[0]
    del demo
    for demo in ['18 to 24','25 to 34','35 to 44','45 to 64','65+']:
        byState.loc[(byState.State == state) & (byState.Year == 2016),demo] = \
        age.loc[(age['STATE ABBREVIATION'] == state) & (age['Age'] == demo),'Total voted'].tolist()[0]/\
        age.loc[(age['STATE ABBREVIATION'] == state) & (age['Age'] == 'Total'),'Total voted'].tolist()[0]
    del demo
del state
del stateAbbrevs
del demographics
del age
del presResults

byState = byState.sort_values(by=['State','Year'])
byState[['State','Year','PARTY','Power_House','Power_Senate','Power_Total']]\
.to_csv('ElectionResults/OverallResults_ByYearAndState.csv',index=False)

""" SCATTER PLOT WITH POWER BY STATE!!! COLOR CODE BY TRUMP/CLINTON!!! """

byUrbanRural = byDistrict[['Cluster','Year','District','Votes_House_Total']]\
.groupby(by=['Cluster','Year']).agg({'District':'size','Votes_House_Total':'sum'}).reset_index()
byUrbanRural['Power_House'] = 1000000*byUrbanRural['District']/byUrbanRural['Votes_House_Total']
for cluster in ['Rural','Suburban','Urban']:
    for year in range(2004,2017,2):
        byUrbanRural.loc[(byUrbanRural.Cluster == cluster) & (byUrbanRural.Year == year),'Power_Senate'] = \
        (byDistrict.loc[(byDistrict.Cluster == cluster) & (byDistrict.Year == year),'Votes_House_Total']*\
        byDistrict.loc[(byDistrict.Cluster == cluster) & (byDistrict.Year == year),'Power_Senate']).sum()/\
        byDistrict.loc[(byDistrict.Cluster == cluster) & (byDistrict.Year == year),'Votes_House_Total'].sum()
    del year
del cluster
byUrbanRural['Power_Total'] = byUrbanRural.Power_Senate*4.35 + byUrbanRural.Power_House

byRedBlue = pd.DataFrame(columns=['Year','PARTY','Power_House','Power_Senate'])
for year in range(2004,2017,2):
    byRedBlue = byRedBlue.append({'Year':year,'PARTY':'REP',\
    'Power_House':1000000*byState.loc[byState.Year == year,'Wins_House_R'].sum()/\
    byState.loc[byState.Year == year,'Votes_House_R'].sum(),\
    'Power_Senate':1000000*byState.loc[byState.Year == year,'Wins_Senate_R_Cumulative'].sum()/\
    (byState.loc[byState.Year == year,'Votes_Senate_R_Cumulative'].sum()/2)},ignore_index=True)
    byRedBlue = byRedBlue.append({'Year':year,'PARTY':'DEM',\
    'Power_House':1000000*byState.loc[byState.Year == year,'Wins_House_D'].sum()/\
    byState.loc[byState.Year == year,'Votes_House_D'].sum(),\
    'Power_Senate':1000000*byState.loc[byState.Year == year,'Wins_Senate_D_Cumulative'].sum()/\
    (byState.loc[byState.Year == year,'Votes_Senate_D_Cumulative'].sum()/2)},ignore_index=True)
    byRedBlue = byRedBlue.append({'Year':year,'PARTY':'IND',\
    'Power_House':1000000*byState.loc[byState.Year == year,'Wins_House_O'].sum()/\
    byState.loc[byState.Year == year,'Votes_House_O'].sum(),\
    'Power_Senate':1000000*byState.loc[byState.Year == year,'Wins_Senate_O_Cumulative'].sum()/\
    (byState.loc[byState.Year == year,'Votes_Senate_O_Cumulative'].sum()/2)},ignore_index=True)
del year
byRedBlue['Power_Total'] = byRedBlue.Power_Senate*4.35 + byRedBlue.Power_House

byDemo = pd.DataFrame(columns=['Demographic','Power_House','Power_Senate'])
for demo in ['Male','Female','White','Black','Asian','Hispanic']:
    byDemo = byDemo.append({'Demographic':demo,\
    'Power_House':(byState.loc[byState.Year == 2016,demo]*byState.loc[byState.Year == 2016,'Votes_House_Total']*\
    byState.loc[byState.Year == 2016,'Power_House']).sum()/(byState.loc[byState.Year == 2016,demo]*\
    byState.loc[byState.Year == 2016,'Votes_House_Total']).sum(),\
    'Power_Senate':(byState.loc[byState.Year == 2016,demo]*byState.loc[byState.Year == 2016,'Votes_Senate_Total']*\
    byState.loc[byState.Year == 2016,'Power_Senate']).sum()/(byState.loc[byState.Year == 2016,demo]*\
    byState.loc[byState.Year == 2016,'Votes_Senate_Total']).sum()},ignore_index=True)
del demo
byDemo['Power_Total'] = byDemo['Power_House'] + 4.35*byDemo['Power_Senate']

byAge = pd.DataFrame(columns=['Age','Power_House','Power_Senate'])
for age in ['18 to 24','25 to 34','35 to 44','45 to 64','65+']:
    byAge = byAge.append({'Age':age,\
    'Power_House':(byState.loc[byState.Year == 2016,age]*byState.loc[byState.Year == 2016,'Votes_House_Total']*\
    byState.loc[byState.Year == 2016,'Power_House']).sum()/(byState.loc[byState.Year == 2016,age]*\
    byState.loc[byState.Year == 2016,'Votes_House_Total']).sum(),\
    'Power_Senate':(byState.loc[byState.Year == 2016,age]*byState.loc[byState.Year == 2016,'Votes_Senate_Total']*\
    byState.loc[byState.Year == 2016,'Power_Senate']).sum()/(byState.loc[byState.Year == 2016,age]*\
    byState.loc[byState.Year == 2016,'Votes_Senate_Total']).sum()},ignore_index=True)
del age
byAge['Power_Total'] = byAge['Power_House'] + 4.35*byAge['Power_Senate']

import matplotlib as mpl
mpl.rc('font',family='Arial')
mpl.rc('font',size=12)
mpl.rcParams['xtick.labelsize'] = 15
mpl.rcParams['ytick.labelsize'] = 15
plt.rc('font',weight='bold')
fileformat = 'png'

plt.figure(figsize=(8,5))
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_Senate_R.sum()/(byState.groupby('Year').Votes_Senate_R.sum() + \
byState.groupby('Year').Votes_Senate_D.sum() + byState.groupby('Year').Votes_Senate_O.sum()),'r',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_Senate_R.sum()/(byState.groupby('Year').Wins_Senate_R.sum() + \
byState.groupby('Year').Wins_Senate_D.sum() + byState.groupby('Year').Wins_Senate_O.sum()),'r--',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_Senate_D.sum()/(byState.groupby('Year').Votes_Senate_R.sum() + \
byState.groupby('Year').Votes_Senate_D.sum() + byState.groupby('Year').Votes_Senate_O.sum()),'b',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_Senate_D.sum()/(byState.groupby('Year').Wins_Senate_R.sum() + \
byState.groupby('Year').Wins_Senate_D.sum() + byState.groupby('Year').Wins_Senate_O.sum()),'b--',linewidth=2)
plt.axis([1999.5,2016.5,30,70])
plt.xticks(np.arange(2000,2017,2))
plt.yticks(np.arange(30,71,10))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Percentage',fontsize=18,fontweight='bold')
plt.title('Senate Results',fontsize=15,fontweight='bold')
plt.legend(['Vote % (R)','Win % (R)','Vote % (D)','Win % (D)'])
plt.tight_layout()
plt.savefig('ElectionResults/SenateResultsByYear_Overall.' + fileformat)

plt.figure(figsize=(8,5))
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_Senate_R_Cumulative.sum()/\
(byState.groupby('Year').Votes_Senate_R_Cumulative.sum() + \
byState.groupby('Year').Votes_Senate_D_Cumulative.sum() + \
byState.groupby('Year').Votes_Senate_O_Cumulative.sum()),'r',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_Senate_R_Cumulative.sum()/\
(byState.groupby('Year').Wins_Senate_R_Cumulative.sum() + \
byState.groupby('Year').Wins_Senate_D_Cumulative.sum() + \
byState.groupby('Year').Wins_Senate_O_Cumulative.sum()),'r--',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_Senate_D_Cumulative.sum()/\
(byState.groupby('Year').Votes_Senate_R_Cumulative.sum() + \
byState.groupby('Year').Votes_Senate_D_Cumulative.sum() + \
byState.groupby('Year').Votes_Senate_O_Cumulative.sum()),'b',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_Senate_D_Cumulative.sum()/\
(byState.groupby('Year').Wins_Senate_R_Cumulative.sum() + \
byState.groupby('Year').Wins_Senate_D_Cumulative.sum() + \
byState.groupby('Year').Wins_Senate_O_Cumulative.sum()),'b--',linewidth=2)
plt.axis([2003.5,2016.5,30,70])
plt.xticks(np.arange(2004,2017,2))
plt.yticks(np.arange(30,71,10))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Percentage',fontsize=18,fontweight='bold')
plt.title('Senate Results',fontsize=15,fontweight='bold')
plt.legend(['Vote % (R)','Win % (R)','Vote % (D)','Win % (D)'])
plt.tight_layout()
plt.savefig('ElectionResults/SenateResultsByYear_Cumulative.' + fileformat)

plt.figure(figsize=(8,5))
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_House_R.sum()/(byState.groupby('Year').Votes_House_R.sum() + \
byState.groupby('Year').Votes_House_D.sum() + byState.groupby('Year').Votes_House_O.sum()),'r',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_House_R.sum()/(byState.groupby('Year').Wins_House_R.sum() + \
byState.groupby('Year').Wins_House_D.sum() + byState.groupby('Year').Wins_House_O.sum()),'r--',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Votes_House_D.sum()/(byState.groupby('Year').Votes_House_R.sum() + \
byState.groupby('Year').Votes_House_D.sum() + byState.groupby('Year').Votes_House_O.sum()),'b',linewidth=2)
plt.plot(range(2000,2017,2),100*byState.groupby('Year').Wins_House_D.sum()/(byState.groupby('Year').Wins_House_R.sum() + \
byState.groupby('Year').Wins_House_D.sum() + byState.groupby('Year').Wins_House_O.sum()),'b--',linewidth=2)
plt.axis([1999.5,2016.5,30,70])
plt.xticks(np.arange(2000,2017,2))
plt.yticks(np.arange(30,71,10))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Percentage',fontsize=18,fontweight='bold')
plt.title('House Results',fontsize=15,fontweight='bold')
plt.legend(['Vote % (R)','Win % (R)','Vote % (D)','Win % (D)'])
plt.tight_layout()
plt.savefig('ElectionResults/HouseResultsByYear_Overall.' + fileformat)

statesOfInterest = byState.loc[byState['Wins_House_R'] + byState['Wins_House_D'] + \
byState['Wins_House_O'] >= 10].groupby('State').Err_House.sum().sort_values(ascending=False)

for state in statesOfInterest[:5].index:
    plt.figure(figsize=(8,5))
    plt.plot(range(2000,2017,2),100*byState.loc[byState.State == state,'VotePct_House_R'],'r',linewidth=2)
    plt.plot(range(2000,2017,2),100*byState.loc[byState.State == state,'WinPct_House_R'],'r--',linewidth=2)
    plt.plot(range(2000,2017,2),100*byState.loc[byState.State == state,'VotePct_House_D'],'b',linewidth=2)
    plt.plot(range(2000,2017,2),100*byState.loc[byState.State == state,'WinPct_House_D'],'b--',linewidth=2)
    plt.axis([1999.5,2016.5,-5,105])
    plt.xticks(np.arange(2000,2017,2))
    plt.yticks(np.arange(0,101,20))
    plt.grid(True)
    plt.xlabel('Year',fontsize=18,fontweight='bold')
    plt.ylabel('Percentage',fontsize=18,fontweight='bold')
    plt.title('House Results, ' + state,fontsize=15,fontweight='bold')
    plt.legend(['Vote % (R)','Win % (R)','Vote % (D)','Win % (D)'])
    plt.tight_layout()
    plt.savefig('ElectionResults/HouseResultsByYear_' + state + '.' + fileformat)
del state

legendVals = ['Rural','Suburban','Urban']
plt.figure(figsize=(8,5))
for cluster in legendVals:
    plt.plot(byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Year'],\
    byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Power_House'],linewidth=2)
del cluster
plt.axis([1999.5,2016.5,3.0,9.0])
plt.xticks(np.arange(2000,2017,2))
plt.yticks(np.arange(3.0,9.01,1.0))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('House of Representatives',fontsize=15,fontweight='bold')
plt.legend(legendVals)
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_House_ByCluster.' + fileformat)

plt.figure(figsize=(8,5))
for cluster in legendVals:
    plt.plot(byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Year'],\
    byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Power_Senate'],linewidth=2)
del cluster
plt.axis([2003.5,2016.5,0.4,1.5])
plt.xticks(np.arange(2004,2017,2))
plt.yticks(np.arange(0.4,1.41,0.2))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('Senate',fontsize=15,fontweight='bold')
plt.legend(legendVals)
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_Senate_ByCluster.' + fileformat)

plt.figure(figsize=(8,5))
for cluster in legendVals:
    plt.plot(byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Year'],\
    byUrbanRural.loc[byUrbanRural.Cluster == cluster,'Power_Total'],linewidth=2)
del cluster
plt.axis([2003.5,2016.5,5.75,12.25])
plt.xticks(np.arange(2004,2017,2))
plt.yticks(np.arange(6.0,12.01,2.0))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('Total',fontsize=15,fontweight='bold')
plt.legend(legendVals)
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_Total_ByCluster.' + fileformat)
del legendVals

plt.figure(figsize=(8,5))
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'REP','Year'],byRedBlue.loc[byRedBlue.PARTY == 'REP','Power_House'],'r',linewidth=2)
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'DEM','Year'],byRedBlue.loc[byRedBlue.PARTY == 'DEM','Power_House'],'b',linewidth=2)
plt.axis([1999.5,2016.5,3.25,6.25])
plt.xticks(np.arange(2000,2017,2))
plt.yticks(np.arange(3.5,6.01,0.5))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('House of Representatives',fontsize=15,fontweight='bold')
plt.legend(['Republican','Democrat'])
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_House_ByParty.' + fileformat)

plt.figure(figsize=(8,5))
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'REP','Year'],byRedBlue.loc[byRedBlue.PARTY == 'REP','Power_Senate'],'r',linewidth=2)
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'DEM','Year'],byRedBlue.loc[byRedBlue.PARTY == 'DEM','Power_Senate'],'b',linewidth=2)
plt.axis([2003.5,2016.5,0.7,1.12])
plt.xticks(np.arange(2004,2017,2))
plt.yticks(np.arange(0.7,1.11,0.1))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('Senate',fontsize=15,fontweight='bold')
plt.legend(['Republican','Democrat'])
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_Senate_ByParty.' + fileformat)

plt.figure(figsize=(8,5))
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'REP','Year'],byRedBlue.loc[byRedBlue.PARTY == 'REP','Power_Total'],'r',linewidth=2)
plt.plot(byRedBlue.loc[byRedBlue.PARTY == 'DEM','Year'],byRedBlue.loc[byRedBlue.PARTY == 'DEM','Power_Total'],'b',linewidth=2)
plt.axis([2003.5,2016.5,6.5,10.5])
plt.xticks(np.arange(2004,2017,2))
plt.yticks(np.arange(7.0,10.01,1.0))
plt.grid(True)
plt.xlabel('Year',fontsize=18,fontweight='bold')
plt.ylabel('Representative Power',fontsize=18,fontweight='bold')
plt.title('Total',fontsize=15,fontweight='bold')
plt.legend(['Republican','Democrat'])
plt.tight_layout()
plt.savefig('ElectionResults/RepresentativePower_Total_ByParty.' + fileformat)

""" 2017 Skinny Repeal of Obamacare """

if os.path.exists('ElectionResults/AmericanHealthCareAct_VoteTally.csv'):
    acaVotes = pd.read_csv('ElectionResults/AmericanHealthCareAct_VoteTally.csv')
else:
    voteData = open('ElectionResults/AmericanHealthCareAct.xml','r')
    votes = voteData.read().split('vote-data')[1].split('\n')[1:-1]
    voteData.close()
    del voteData
    acaVotes = pd.DataFrame(columns=['Name','Party','State','Vote'])
    for vote in votes:
        acaVotes = acaVotes.append({'Name':vote.split('unaccented-name="')[1].split('"')[0],\
        'Party':vote.split('party="')[1].split('"')[0],'State':vote.split('state="')[1].split('"')[0],\
        'Vote':vote.split('<vote>')[1].split('</vote>')[0]},ignore_index=True)
    del vote
    del votes
    acaVotes.to_csv('ElectionResults/AmericanHealthCareAct_VoteTally.csv',index=False)

acaHouseVotes = {'Aye':0,'No':0,'Not Voting':0}
for ind in range(acaVotes.shape[0]):
    acaHouseVotes[acaVotes.loc[ind,'Vote']] += byDistrict.loc[np.all([byDistrict.State == acaVotes.loc[ind,'State'],\
    byDistrict.Name.str.contains(acaVotes.loc[ind,'Name'].replace('Estes (KS)','Pompeo').split(' (')[0].split(' ')[0]),\
    byDistrict.Year == 2016],axis=0),'Votes_House_Total'].tolist()[0]
del ind

""" Senate: All Democrats, McCain, Collins, and Murkowski voted no, remaining Republicans voted yes """
acaSenateVotes = {'Aye':0,'No':0,'Not Voting':0}
for state in byState.State.unique():
    if state in ['AZ','AK']:
        acaSenateVotes['Aye'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
        acaSenateVotes['No'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
    elif state in ['VT','ME']:
        acaSenateVotes['No'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/2
    else:
        acaSenateVotes['Aye'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Wins_Senate_R_Cumulative'].tolist()[0]*\
        byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
        acaSenateVotes['No'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Wins_Senate_D_Cumulative'].tolist()[0]*\
        byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
del state

""" 2017 Tax Cuts and Jobs Act """

if os.path.exists('ElectionResults/TaxCutsAndJobsAct_VoteTally.csv'):
    taxVotes = pd.read_csv('ElectionResults/TaxCutsAndJobsAct_VoteTally.csv')
else:
    voteData = open('ElectionResults/TaxCutsAndJobsAct.xml','r')
    votes = voteData.read().split('vote-data')[1].split('\n')[1:-1]
    voteData.close()
    del voteData
    taxVotes = pd.DataFrame(columns=['Name','Party','State','Vote'])
    for vote in votes:
        taxVotes = taxVotes.append({'Name':vote.split('unaccented-name="')[1].split('"')[0],\
        'Party':vote.split('party="')[1].split('"')[0],'State':vote.split('state="')[1].split('"')[0],\
        'Vote':vote.split('<vote>')[1].split('</vote>')[0]},ignore_index=True)
    del vote
    del votes
    taxVotes.to_csv('ElectionResults/TaxCutsAndJobsAct_VoteTally.csv',index=False)

taxHouseVotes = {'Yea':0,'Nay':0,'Not Voting':0}
for ind in range(taxVotes.shape[0]):
    taxHouseVotes[taxVotes.loc[ind,'Vote']] += byDistrict.loc[np.all([byDistrict.State == taxVotes.loc[ind,'State'],\
    byDistrict.Name.str.contains(taxVotes.loc[ind,'Name'].replace('Curtis','Chaffetz').replace('Gomez','Becerra').replace('Norman','Mulvaney')\
    .replace('Estes (KS)','Pompeo').replace('Gianforte','Zinke').replace('Handel','Price').split(' (')[0].split(' ')[0]),\
    byDistrict.Year == 2016],axis=0),'Votes_House_Total'].tolist()[0]
del ind

""" Senate: McCain didn't vote, but party-line vote otherwise """
taxSenateVotes = {'Yea':0,'Nay':0,'Not Voting':0}
for state in byState.State.unique():
    if state == 'AZ':
        taxSenateVotes['Yea'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
        taxSenateVotes['Not Voting'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
    else:
        taxSenateVotes['Yea'] += byState.loc[(byState.State == state) & (byState.Year == 2016),'Wins_Senate_R_Cumulative'].tolist()[0]*\
        byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
        taxSenateVotes['Nay'] += (byState.loc[(byState.State == state) & (byState.Year == 2016),'Wins_Senate_D_Cumulative'].tolist()[0] + \
        byState.loc[(byState.State == state) & (byState.Year == 2016),'Wins_Senate_O_Cumulative'].tolist()[0])*\
        byState.loc[(byState.State == state) & (byState.Year == 2016),'Votes_Senate_Total_Cumulative'].tolist()[0]/4
del state

""" Gorsuch Supreme Court Nomination """

rollCall = pd.read_csv('ElectionResults/GorsuchRollCall.csv')
rollCall = pd.merge(left=rollCall,right=byState.loc[byState.Year == 2016,\
['State','Votes_Senate_Total_Cumulative']],how='inner',left_on='State',right_on='State')
gorsuchVotes = rollCall.groupby('Vote').Votes_Senate_Total_Cumulative.sum()/4
del rollCall

""" Cavanaugh Supreme Court Nomination """

rollCall = pd.read_csv('ElectionResults/KavanaughRollCall.csv')
rollCall = pd.merge(left=rollCall,right=byState.loc[byState.Year == 2016,\
['State','Votes_Senate_Total_Cumulative']],how='inner',left_on='State',right_on='State')
kavanaughVotes = rollCall.groupby('Vote').Votes_Senate_Total_Cumulative.sum()/4
del rollCall





