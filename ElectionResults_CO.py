#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 23:57:45 2019

@author: tefirman
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import json
import plotly.graph_objs as graph_objs
from plotly.offline import plot
from matplotlib.colors import Normalize

plotCounties = True
plotPrecincts = True

def heatMap(shapes,stat,minVal,maxVal,numIncs,colorMap,accuracy,center,zoomFactor,outline,filename,showPlot):
    cmap = plt.get_cmap(colorMap)
    norm = Normalize(vmin=minVal,vmax=maxVal)
    mapbox_access_token = "pk.eyJ1IjoidGVmaXJtYW4iLCJhIjoiY2p0cmU0MDZsMHAyYjQ1bnNseHBta2FuNiJ9.qo4-Zqy7JEZQDegzn-WXRQ"
    dataLayers = []
    for inc in range(numIncs):
        if inc == 0:
            inds = shapes[stat] < minVal + (maxVal - minVal)*(inc + 1)/numIncs
        elif inc == numIncs - 1:
            inds = shapes[stat] >= minVal + (maxVal - minVal)*inc/numIncs
        else:
            inds = (shapes[stat] >= minVal + (maxVal - minVal)*inc/numIncs) & (shapes[stat] < minVal + (maxVal - minVal)*(inc + 1)/numIncs)
        dataLayers.append(graph_objs.Scattermapbox(
        lat=round(shapes.loc[inds,'geometry'].centroid.y,accuracy),
        lon=round(shapes.loc[inds,'geometry'].centroid.x,accuracy), 
        text=shapes.loc[inds,'Label'], hoverinfo='text',mode='markers',
        marker=dict(size=0,color='rgba' + str(cmap(norm(minVal + (maxVal - minVal)*(inc + 0.5)/numIncs)))),name='CO_' + stat + '_' + str(inc)))
        del inds
    del inc
    mapData = graph_objs.Data(dataLayers)
    incLayers = []
    for inc in range(numIncs):
        if inc == 0:
            geoj = json.loads(shapes.loc[shapes[stat] < minVal + (maxVal - minVal)*(inc + 1)/numIncs].to_json())
        elif inc == numIncs - 1:
            geoj = json.loads(shapes.loc[shapes[stat] >= minVal + (maxVal - minVal)*inc/numIncs].to_json())
        else:
            geoj = json.loads(shapes.loc[(shapes[stat] >= minVal + (maxVal - minVal)*inc/numIncs) & (shapes[stat] < minVal + (maxVal - minVal)*(inc + 1)/numIncs)].to_json())
        if len(geoj['features']) == 0:
            del geoj
            continue
        for shapeInd in range(len(geoj['features'])):
            geoj['features'][shapeInd]['properties'][stat] = round(geoj['features'][shapeInd]['properties'][stat],accuracy)
            if len(geoj['features'][shapeInd]['geometry']['coordinates']) == 1:
                geoj['features'][shapeInd]['geometry']['coordinates'] = np.round(np.array(geoj['features'][shapeInd]['geometry']['coordinates']),accuracy)
            else:
                for coordInd in range(len(geoj['features'][shapeInd]['geometry']['coordinates'][0])):
                    if type(geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0]) == list:
                        geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0][0] = round(geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0][0],accuracy)
                        geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0][1] = round(geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0][1],accuracy)
                    else:
                        geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0] = round(geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0],accuracy)
                        geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][1] = round(geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][1],accuracy)
                del coordInd
            
            if type(geoj['features'][shapeInd]['geometry']['coordinates']) == np.ndarray:
                geoj['features'][shapeInd]['geometry']['coordinates'] = geoj['features'][shapeInd]['geometry']['coordinates'].tolist()
            coordInd = 1
            while coordInd < len(geoj['features'][shapeInd]['geometry']['coordinates'][0]) - 1:
                if geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd] == \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd - 1]:
                    # print('Popping repeat coordinate...')
                    geoj['features'][shapeInd]['geometry']['coordinates'][0].pop(coordInd)
                    coordInd -= 1
                elif geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0] == \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd - 1][0] and \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][0] == \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd + 1][0]:
                    # print('Popping linear coordinate...')
                    geoj['features'][shapeInd]['geometry']['coordinates'][0].pop(coordInd)
                    coordInd -= 1
                elif geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][1] == \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd - 1][1] and \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd][1] == \
                geoj['features'][shapeInd]['geometry']['coordinates'][0][coordInd + 1][1]:
                    # print('Popping linear coordinate...')
                    geoj['features'][shapeInd]['geometry']['coordinates'][0].pop(coordInd)
                    coordInd -= 1
                coordInd += 1
            del coordInd
        del shapeInd
        source = {'type':'FeatureCollection','features':geoj['features']}
        incLayers.append(dict(sourcetype='geojson',source=source,below="place-neighbourhood",type='fill',
        color = 'rgba' + str(cmap(norm(minVal + (maxVal - minVal)*(inc + 0.5)/numIncs))),opacity=0.8))
        if outline:
            incLayers.append(dict(sourcetype='geojson',source=source,below="place-neighbourhood",type='line',
            color = 'rgba' + str(cmap(norm(minVal + (maxVal - minVal)*(inc + 0.5)/numIncs))),opacity=0.8))
        del geoj, source
    del inc
    mapLayout = graph_objs.Layout(
        height=400,width=700,autosize=True,hovermode='closest',mapbox=dict(
        layers=incLayers,accesstoken=mapbox_access_token,bearing=0,
        center=dict(lat=center[0],lon=center[1]),pitch=0,zoom=zoomFactor,
        style='light'),showlegend=False,margin=dict(l=0,r=0,t=0,b=0)
    )
    mapFig = dict(data=mapData, layout=mapLayout)
    plot(mapFig, filename=filename,auto_open=showPlot)

""" Loading Raw Results """

results = pd.DataFrame()
turnout = pd.DataFrame()
for year in range(2012,2019,2):
    results = results.append(pd.read_csv('ElectionResults_CO/GeneralResultsPrecinctLevel_' + str(year) + '.csv',encoding='latin2'),ignore_index=True)
    results = results.loc[~results.Party.isnull()]
    results.loc[~results.Party.isin(['Democratic Party','Republican Party']),'Party'] = 'Independent'
    turnout = turnout.append(pd.read_csv('ElectionResults_CO/GeneralTurnoutPrecinctLevel_' + str(year) + '.csv',encoding='latin2'),ignore_index=True,sort=False)
    if year == 2018:
        results_73 = pd.read_csv('ElectionResults_CO/GeneralResultsPrecinctLevel_' + str(year) + '.csv',encoding='latin2')
        results_73 = results_73.loc[results_73['Office/Issue/Judgeship'].str.contains('Amendment 73')]
del year
results = results.loc[results.Precinct != 'Provisional']
results.Precinct = results.Precinct.astype(int)
turnout['County'] = turnout['County'].str.title()
turnout['Total Voters'] = turnout['Total Voters'].str.replace(',','').astype(float)
turnout['Ballots Cast'] = turnout['Ballots Cast'].str.replace(',','').astype(int)

""" Results By County """

voteTotals = pd.merge(left=results.loc[results.Party == 'Democratic Party']\
.groupby(['Year','County','Office/Issue/Judgeship'])['Candidate Votes']\
.sum().reset_index().rename(index=str,columns={'Candidate Votes':'Democratic Votes'}),\
right=results.loc[results.Party == 'Republican Party'].groupby(['Year','County','Office/Issue/Judgeship'])\
['Candidate Votes'].sum().reset_index().rename(index=str,columns={'Candidate Votes':'Republican Votes'}),\
how='inner',left_on=['Year','County','Office/Issue/Judgeship'],right_on=['Year','County','Office/Issue/Judgeship'])
voteTotals = pd.merge(left=voteTotals,right=results.groupby(['Year','County','Office/Issue/Judgeship'])\
['Candidate Votes'].sum().reset_index().rename(index=str,columns={'Candidate Votes':'Total Votes'}),\
how='inner',left_on=['Year','County','Office/Issue/Judgeship'],right_on=['Year','County','Office/Issue/Judgeship'])
voteTotals['Lean'] = (voteTotals['Democratic Votes'] - voteTotals['Republican Votes'])/voteTotals['Total Votes']
voteTotals['Elasticity'] = voteTotals['Lean']
voteTotals['Democratic Avg'] = voteTotals['Democratic Votes']/voteTotals['Total Votes']
voteTotals['Republican Avg'] = voteTotals['Republican Votes']/voteTotals['Total Votes']
voteTotals['Democratic Variance'] = voteTotals['Democratic Avg']**2
voteTotals['Republican Variance'] = voteTotals['Republican Avg']**2
voteTotals['Covariance'] = voteTotals['Democratic Avg']*voteTotals['Republican Avg']

byCounty = voteTotals.groupby('County').agg({'Lean':'mean','Elasticity':'std',\
'Democratic Avg':'mean','Republican Avg':'mean','Democratic Variance':'mean',\
'Republican Variance':'mean','Covariance':'mean'}).reset_index()
byCounty['Democratic Variance'] -= byCounty['Democratic Avg']**2
byCounty['Republican Variance'] -= byCounty['Republican Avg']**2
byCounty['Covariance'] -= byCounty['Democratic Avg']*byCounty['Republican Avg']
byCounty['Correlation'] = byCounty['Covariance']/((byCounty['Democratic Variance']**0.5)*(byCounty['Republican Variance']**0.5))
byCounty['Flippability'] = -np.log10(abs(byCounty['Lean']/byCounty['Elasticity']))

byCountyYear = voteTotals.groupby(['Year','County']).agg({'Lean':'mean','Elasticity':'std'}).reset_index()
byCountyYear = pd.merge(left=byCountyYear.loc[byCountyYear.Year == 2018,['County','Lean']].rename(index=str,columns={'Lean':'Lean 2018'}),\
right=byCountyYear.loc[byCountyYear.Year == 2014,['County','Lean']].rename(index=str,columns={'Lean':'Lean 2014'}),\
how='inner',left_on='County',right_on='County')
byCountyYear['Trump Effect'] = byCountyYear['Lean 2018'] - byCountyYear['Lean 2014']
byCounty = pd.merge(left=byCounty,right=byCountyYear,how='inner',left_on='County',right_on='County')
del byCountyYear

byCountyYear = voteTotals.groupby(['Year','County']).agg({'Lean':'mean','Elasticity':'std'}).reset_index()
for county in byCountyYear.County.unique():
    byCountyYear.loc[byCountyYear.County == county,'Trend'] = \
    np.polyfit(byCountyYear.loc[byCountyYear.County == county,'Year'],\
    byCountyYear.loc[byCountyYear.County == county,'Lean'].tolist(),1)[0]
del county
byCountyYear = byCountyYear.loc[byCountyYear.Year == 2018,['County','Trend']]
byCounty = pd.merge(left=byCounty,right=byCountyYear,how='inner',left_on='County',right_on='County')
del byCountyYear, voteTotals

""" Voter Turnout By County During Presidential Election Years """

voteTotals = turnout.loc[turnout.Year%4 == 0].groupby(['Year','County'])[['Total Voters','Ballots Cast']].sum().reset_index()
voteTotals['Presidential Turnout %'] = voteTotals['Ballots Cast']/voteTotals['Total Voters']
voteTotals = voteTotals.groupby('County')[['Presidential Turnout %']].mean().reset_index()
byCounty = pd.merge(left=byCounty,right=voteTotals[['County','Presidential Turnout %']],how='inner',left_on='County',right_on='County')
del voteTotals

""" Voter Turnout By County During Midterm Election Years """

voteTotals = turnout.loc[turnout.Year%4 == 2].groupby(['Year','County'])[['Total Voters','Ballots Cast']].sum().reset_index()
voteTotals['Midterm Turnout %'] = voteTotals['Ballots Cast']/voteTotals['Total Voters']
voteTotals = voteTotals.groupby('County')[['Midterm Turnout %']].mean().reset_index()
byCounty = pd.merge(left=byCounty,right=voteTotals[['County','Midterm Turnout %']],how='inner',left_on='County',right_on='County')
del voteTotals

""" Most Recent Voter Registration and Likely Voter Turnout """

byCounty = pd.merge(left=byCounty,right=turnout.loc[turnout.Year == 2018].groupby('County')['Total Voters'].sum().reset_index(),how='inner',left_on='County',right_on='County')
byCounty['Ballots Cast'] = byCounty['Total Voters']*byCounty['Presidential Turnout %']

""" Amendment 73 (Education) Results """

byCounty = pd.merge(left=byCounty,right=results_73.groupby('County')[['Yes Votes','No Votes']].sum()\
.reset_index().rename(index=str,columns={'Yes Votes':'Yes on 73','No Votes':'No on 73'}),\
how='inner',left_on='County',right_on='County')
byCounty = pd.merge(left=byCounty,right=turnout.loc[turnout.Year == 2018].groupby('County')['Ballots Cast'].sum()\
.reset_index().rename(index=str,columns={'Ballots Cast':'Ballots 73'}),how='inner',left_on='County',right_on='County')
byCounty['Abstain on 73'] = byCounty['Ballots 73'] - byCounty['Yes on 73'] - byCounty['No on 73']
byCounty['Yes % on 73'] = byCounty['Yes on 73']/byCounty['Ballots 73']
byCounty['No % on 73'] = byCounty['No on 73']/byCounty['Ballots 73']
byCounty['Abstain % on 73'] = byCounty['Abstain on 73']/byCounty['Ballots 73']
del byCounty['Ballots 73']

""" Democratic Primary Results By County """

primary = pd.read_csv('ElectionResults_CO/PrimaryResultsCountyLevel_2018.csv')
primary['County Name'] = primary['County Name'].str.title()
primary = primary.loc[(primary.Party == 'Democratic Party') & (primary.Office == 'Governor') & (primary['County Name'] != 'Percentage')]
primary['Votes'] = primary['Votes/Percentage'].str.replace(',','').astype(int)
primByCounty = primary.groupby('County Name')['Votes'].sum().reset_index().rename(index=str,columns={'Votes':'Total Votes'})
primary = pd.merge(left=primary,right=primByCounty,how='left',left_on='County Name',right_on='County Name')
del primary['Unnamed: 5'], primary['Votes/Percentage'], primByCounty
primary['Percentage'] = primary['Votes']/primary['Total Votes']
johnston = primary.loc[primary['Candidate Name'].str.contains('Johnston')]
johnston = johnston.rename(index=str,columns={'County Name':'County',\
'Votes':'Johnston Primary Votes','Percentage':'Johnston Primary %',\
'Total Votes':'Primary Ballots Cast'})
byCounty = pd.merge(left=byCounty,right=johnston[['County','Johnston Primary Votes',\
'Johnston Primary %','Primary Ballots Cast']],how='inner',left_on='County',right_on='County')
polis = primary.loc[primary['Candidate Name'].str.contains('Polis')]
polis = polis.rename(index=str,columns={'County Name':'County',\
'Votes':'Polis Primary Votes','Percentage':'Polis Primary %'})
byCounty = pd.merge(left=byCounty,right=polis[['County','Polis Primary Votes',\
'Polis Primary %']],how='inner',left_on='County',right_on='County')
kennedy = primary.loc[primary['Candidate Name'].str.contains('Kennedy')]
kennedy = kennedy.rename(index=str,columns={'County Name':'County',\
'Votes':'Kennedy Primary Votes','Percentage':'Kennedy Primary %'})
byCounty = pd.merge(left=byCounty,right=kennedy[['County','Kennedy Primary Votes',\
'Kennedy Primary %']],how='inner',left_on='County',right_on='County')
byCounty['Primary Turnout %'] = byCounty['Primary Ballots Cast']/(byCounty['Ballots Cast']*(byCounty['Lean'] + 0.5))
del primary, johnston, polis, kennedy

""" County Area and Voter Density """

countyShapes = gpd.read_file('PrecinctShapefiles/cb_2017_us_county_500k/cb_2017_us_county_500k.shp')
countyShapes = countyShapes.loc[countyShapes.STATEFP == '08'].rename(index=str,columns={'NAME':'County','ALAND':'Area'})
countyShapes['Area'] /= (1.60934*1.60934*1e6) # Converting to square miles
byCounty = pd.merge(left=byCounty,right=countyShapes[['County','Area']],how='inner',left_on='County',right_on='County')
byCounty['Voter Density'] = byCounty['Ballots Cast']/byCounty['Area']
byCounty['Primary Voter Density'] = byCounty['Primary Ballots Cast']/byCounty['Area']
byCounty['Flippable'] = ((byCounty['Flippability'] >= 0) & (byCounty['Voter Density'] >= 20)).astype(int)
del countyShapes['Area']

""" Saving County Results to CSV """

byCounty.sort_values('Lean',ascending=False).to_csv('ElectionResults_CO/LeanElasticityTrend_ByCounty.csv',index=False)

""" Plotting County Results """

countyShapes = pd.merge(left=countyShapes,right=byCounty,how='inner',left_on='County',right_on='County')
countyShapes.Lean *= 100
countyShapes.Elasticity *= 100
countyShapes.Trend *= 100
countyShapes['Trump Effect'] *= 100
countyShapes['Presidential Turnout %'] *= 100
countyShapes['Midterm Turnout %'] *= 100
countyShapes['Yes % on 73'] *= 100
countyShapes['Johnston Primary %'] *= 100

if plotCounties:
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Partisan Lean: '
    countyShapes.loc[countyShapes.Lean < 0,'Label'] += 'R+' + round(abs(countyShapes.loc[countyShapes.Lean < 0,'Lean']),1).astype(str)
    countyShapes.loc[countyShapes.Lean == 0,'Label'] += 'Even'
    countyShapes.loc[countyShapes.Lean > 0,'Label'] += 'D+' + round(abs(countyShapes.loc[countyShapes.Lean > 0,'Lean']),1).astype(str)
    heatMap(countyShapes,'Lean',-25,25,20,'RdBu',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PartisanLeanCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Partisan Elasticity: ' + round(countyShapes.Elasticity,1).astype(str)
    heatMap(countyShapes,'Elasticity',0,25,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PartisanElasticityCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Partisan Correlation: ' + round(countyShapes.Correlation,2).astype(str)
    heatMap(countyShapes,'Correlation',-1,0,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PartisanCorrelationCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Partisan Trend: '
    countyShapes.loc[countyShapes.Trend < 0,'Label'] += 'R+' + round(abs(countyShapes.loc[countyShapes.Trend < 0,'Trend']),1).astype(str)
    countyShapes.loc[countyShapes.Trend == 0,'Label'] += 'Even'
    countyShapes.loc[countyShapes.Trend > 0,'Label'] += 'D+' + round(abs(countyShapes.loc[countyShapes.Trend > 0,'Trend']),1).astype(str)
    heatMap(countyShapes,'Trend',-2.5,2.5,20,'RdBu',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PartisanTrendCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Trump Effect: '
    countyShapes.loc[countyShapes['Trump Effect'] < 0,'Label'] += 'R+' + round(abs(countyShapes.loc[countyShapes['Trump Effect'] < 0,'Trump Effect']),1).astype(str)
    countyShapes.loc[countyShapes['Trump Effect'] == 0,'Label'] += 'Even'
    countyShapes.loc[countyShapes['Trump Effect'] > 0,'Label'] += 'D+' + round(abs(countyShapes.loc[countyShapes['Trump Effect'] > 0,'Trump Effect']),1).astype(str)
    heatMap(countyShapes,'Trump Effect',-7.5,7.5,20,'RdBu',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/TrumpEffectCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Flippability: ' + round(countyShapes.Flippability,2).astype(str)
    heatMap(countyShapes,'Flippability',-2,2,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/FlippabilityCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Flippable: ' + (abs(countyShapes.Flippable) > 0).astype(str)
    heatMap(countyShapes,'Flippable',0,1,2,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/FlippableCountiesCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Ballots Cast: ' + round(countyShapes['Ballots Cast']).map('{:,.0f}'.format)
    heatMap(countyShapes,'Ballots Cast',0,250000,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/NumberOfVotersCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Presidential Voter Turnout: ' + round(countyShapes['Presidential Turnout %'],1).astype(str) + '%'
    heatMap(countyShapes,'Presidential Turnout %',60,85,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PresidentialVoterTurnoutCO.html',False)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Midterm Voter Turnout: ' + round(countyShapes['Midterm Turnout %'],1).astype(str) + '%'
    heatMap(countyShapes,'Midterm Turnout %',60,85,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/MidtermVoterTurnoutCO.html',False)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Amendment 73 Yes %: ' + round(countyShapes['Yes % on 73'],1).astype(str) + '%'
    heatMap(countyShapes,'Yes % on 73',30,50,20,'Purples',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/Amendment73YesPctCO.html',True)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Johnston Primary Vote %: ' + round(countyShapes['Johnston Primary %'],1).astype(str) + '%'
    heatMap(countyShapes,'Johnston Primary %',10,45,20,'Blues',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/JohnstonPrimaryPctCO.html',False)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Johnston Primary Votes: ' + countyShapes['Johnston Primary Votes'].map('{:,.0f}'.format)
    heatMap(countyShapes,'Johnston Primary Votes',0,10000,20,'Blues',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/JohnstonPrimaryVotesCO.html',False)
    
    countyShapes['Label'] = countyShapes['County'] + ' County<br>Primary Ballots Cast: ' + round(countyShapes['Primary Ballots Cast']).map('{:,.0f}'.format)
    heatMap(countyShapes,'Primary Ballots Cast',0,75000,20,'Blues',4,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/NumberOfPrimaryVotersCO.html',False)

""" Results By Precinct """

voteTotals = pd.merge(left=results.loc[results.Party == 'Democratic Party']\
.groupby(['Year','County','Precinct','Office/Issue/Judgeship'])['Candidate Votes']\
.sum().reset_index().rename(index=str,columns={'Candidate Votes':'Democratic Votes'}),\
right=results.loc[results.Party == 'Republican Party'].groupby(['Year','County','Precinct','Office/Issue/Judgeship'])\
['Candidate Votes'].sum().reset_index().rename(index=str,columns={'Candidate Votes':'Republican Votes'}),\
how='inner',left_on=['Year','County','Precinct','Office/Issue/Judgeship'],right_on=['Year','County','Precinct','Office/Issue/Judgeship'])
voteTotals = pd.merge(left=voteTotals,right=results.groupby(['Year','County','Precinct','Office/Issue/Judgeship'])\
['Candidate Votes'].sum().reset_index().rename(index=str,columns={'Candidate Votes':'Total Votes'}),\
how='inner',left_on=['Year','County','Precinct','Office/Issue/Judgeship'],right_on=['Year','County','Precinct','Office/Issue/Judgeship'])
voteTotals['Lean'] = (voteTotals['Democratic Votes'] - voteTotals['Republican Votes'])/voteTotals['Total Votes']
voteTotals['Elasticity'] = voteTotals['Lean']
voteTotals['Democratic Avg'] = voteTotals['Democratic Votes']/voteTotals['Total Votes']
voteTotals['Republican Avg'] = voteTotals['Republican Votes']/voteTotals['Total Votes']
voteTotals['Democratic Variance'] = voteTotals['Democratic Avg']**2
voteTotals['Republican Variance'] = voteTotals['Republican Avg']**2
voteTotals['Covariance'] = voteTotals['Democratic Avg']*voteTotals['Republican Avg']
voteTotals = voteTotals.loc[voteTotals['Total Votes'] > 0]

byPrecinct = voteTotals.groupby(['County','Precinct']).agg({'Lean':'mean','Elasticity':'std',\
'Democratic Avg':'mean','Republican Avg':'mean','Democratic Variance':'mean',\
'Republican Variance':'mean','Covariance':'mean'}).reset_index()
byPrecinct['Democratic Variance'] -= byPrecinct['Democratic Avg']**2
byPrecinct['Republican Variance'] -= byPrecinct['Republican Avg']**2
byPrecinct['Covariance'] -= byPrecinct['Democratic Avg']*byPrecinct['Republican Avg']
byPrecinct['Correlation'] = byPrecinct['Covariance']/((byPrecinct['Democratic Variance']**0.5)*(byPrecinct['Republican Variance']**0.5))
byPrecinct['Flippability'] = -np.log10(abs(byPrecinct['Lean']/byPrecinct['Elasticity']))

byPrecinctYear = voteTotals.groupby(['Year','County','Precinct']).agg({'Lean':'mean','Elasticity':'std'}).reset_index()
byPrecinctYear = pd.merge(left=byPrecinctYear.loc[byPrecinctYear.Year == 2018,['County','Precinct','Lean']].rename(index=str,columns={'Lean':'Lean 2018'}),\
right=byPrecinctYear.loc[byPrecinctYear.Year == 2014,['County','Precinct','Lean']].rename(index=str,columns={'Lean':'Lean 2014'}),\
how='inner',left_on=['County','Precinct'],right_on=['County','Precinct'])
byPrecinctYear['Trump Effect'] = byPrecinctYear['Lean 2018'] - byPrecinctYear['Lean 2014']
byPrecinct = pd.merge(left=byPrecinct,right=byPrecinctYear,how='left',left_on=['County','Precinct'],right_on=['County','Precinct'])
del byPrecinctYear

byPrecinctYear = voteTotals.groupby(['Year','County','Precinct']).agg({'Lean':'mean','Elasticity':'std'}).reset_index()
for precinct in byPrecinctYear.Precinct.unique():
    if byPrecinctYear.loc[byPrecinctYear.Precinct == precinct,'Year'].unique().shape[0] > 1:
        byPrecinctYear.loc[byPrecinctYear.Precinct == precinct,'Trend'] = \
        np.polyfit(byPrecinctYear.loc[byPrecinctYear.Precinct == precinct,'Year'],\
        byPrecinctYear.loc[byPrecinctYear.Precinct == precinct,'Lean'].tolist(),1)[0]
del precinct
byPrecinctYear = byPrecinctYear.loc[byPrecinctYear.Year == 2018,['County','Precinct','Trend']]
byPrecinct = pd.merge(left=byPrecinct,right=byPrecinctYear,how='left',left_on=['County','Precinct'],right_on=['County','Precinct'])
del byPrecinctYear, voteTotals

""" Voter Turnout By Precinct During Presidential Election Years """

voteTotals = turnout.loc[turnout.Year%4 == 0].groupby(['Year','County','Precinct'])[['Total Voters','Ballots Cast']].sum().reset_index()
voteTotals['Presidential Turnout %'] = voteTotals['Ballots Cast']/voteTotals['Total Voters']
voteTotals = voteTotals.groupby(['County','Precinct'])[['Presidential Turnout %']].mean().reset_index()
byPrecinct = pd.merge(left=byPrecinct,right=voteTotals[['County','Precinct','Presidential Turnout %']],how='left',left_on=['County','Precinct'],right_on=['County','Precinct'])
del voteTotals

""" Voter Turnout By Precinct During Midterm Election Years """

voteTotals = turnout.loc[turnout.Year%4 == 2].groupby(['Year','County','Precinct'])[['Total Voters','Ballots Cast']].sum().reset_index()
voteTotals['Midterm Turnout %'] = voteTotals['Ballots Cast']/voteTotals['Total Voters']
voteTotals = voteTotals.groupby(['County','Precinct'])[['Midterm Turnout %']].mean().reset_index()
byPrecinct = pd.merge(left=byPrecinct,right=voteTotals[['County','Precinct','Midterm Turnout %']],how='left',left_on=['County','Precinct'],right_on=['County','Precinct'])
del voteTotals

""" Most Recent Voter Registration and Likely Voter Turnout """

byPrecinct = pd.merge(left=byPrecinct,right=turnout.loc[turnout.Year == 2018]\
.groupby(['County','Precinct'])['Total Voters'].sum().reset_index(),how='inner',\
left_on=['County','Precinct'],right_on=['County','Precinct'])
byPrecinct['Ballots Cast'] = byPrecinct['Total Voters']*byPrecinct['Presidential Turnout %']

""" Amendment 73 (Education) Results """

byPrecinct = pd.merge(left=byPrecinct,right=results_73.groupby(['County','Precinct'])[['Yes Votes','No Votes']].sum()\
.reset_index().rename(index=str,columns={'Yes Votes':'Yes on 73','No Votes':'No on 73'}),\
how='inner',left_on=['County','Precinct'],right_on=['County','Precinct'])
byPrecinct = pd.merge(left=byPrecinct,right=turnout.loc[turnout.Year == 2018].groupby(['County','Precinct'])['Ballots Cast'].sum()\
.reset_index().rename(index=str,columns={'Ballots Cast':'Ballots 73'}),how='inner',left_on=['County','Precinct'],right_on=['County','Precinct'])
byPrecinct['Abstain on 73'] = byPrecinct['Ballots 73'] - byPrecinct['Yes on 73'] - byPrecinct['No on 73']
byPrecinct['Yes % on 73'] = byPrecinct['Yes on 73']/byPrecinct['Ballots 73']
byPrecinct['No % on 73'] = byPrecinct['No on 73']/byPrecinct['Ballots 73']
byPrecinct['Abstain % on 73'] = byPrecinct['Abstain on 73']/byPrecinct['Ballots 73']
del byPrecinct['Ballots 73']

""" Precinct Area and Voter Density """

precinctCol = {'Larimer':'PRECINCT','Weld':'PRECINCT','Boulder':'PRECINCT',\
'Jefferson':'COUNTYPREC','Denver':'PRECINCT_N','Adams':'Full_Numbe',\
'Arapahoe':'COLO_PREC','Douglas':'STATE_PREC','El Paso':'STATENUM',\
'Broomfield':'PRECINCT_N','Pueblo':'Precinct','Mesa':'CRS_CODE',\
'La Plata':'Precinct','Pitkin':'PRECINCT','Fremont':'id_full',\
'Montrose':'PRECINCT_N','Summit':'Precincts','Garfield':'PRECINCT',\
'Routt':'PRECINCTID','Montezuma':'VoterPreci','Grand':'VOTE_PRECT',\
'Clear Creek':'VOTING','San Miguel':'PRECINCT_C','Rio Blanco':'PRECINCT',\
'Gunnison':'Name','Eagle':'NEW_PRECIN','San Juan':'OBJECTID',\
'Ouray':'Precinct','Teller':'Label','Delta':'Precinct_N',\
'Conejos':'Precinct','Cheyenne':'Precinct','Park':'LABEL','Logan':'PRECINCT',\
'Jackson':'Precinct','Archuleta':'Precinct','Chaffee':'Precinct',\
'Custer':'Precinct','Gilpin':'precinctid','Lake':'Precinct',\
'Lincoln':'Precinct','Phillips':'Precinct','Prowers':'Precinct',\
'Saguache':'Precinct','Sedgwick':'Precinct','Washington':'Precinct',\
'Yuma':'Precinct','Moffat':'Precinct','Alamosa':'Precinct',\
'Elbert':'Precinct','Kit Carson':'Precinct','Morgan':'Precinct',\
'Crowley':'Precinct','Baca':'Precinct','Dolores':'Precinct',\
'Otero':'ID','Rio Grande':'Precinct','Las Animas':'Precinct',\
'Bent':'Precinct','Huerfano':'Precinct','Costilla':'Precinct',\
'Kiowa':'Precinct','Hinsdale':'Precinct','Mineral':'Precinct'}
offsets = {'La Plata':3065934000,'Pitkin':3056149000,'Montrose':3065843000,\
'Summit':2086159000,'Garfield':3085723000,'Routt':3082654000,\
'Montezuma':3065842000,'Grand':2081325000,'Clear Creek':2021310000,\
'Rio Blanco':3085752000,'Ouray':3065946000,'Teller':5023960000,\
'Conejos':3356211000,'Logan':4016538000,'San Juan':3065956001,\
'Hinsdale':3055927001,'Mineral':3356240001,'Gilpin':2161324000,\
'Alamosa':3356202000,'Otero':4354745000}
precinctShapes = gpd.GeoDataFrame()
for county in precinctCol:
    if county in ['San Juan','Hinsdale','Mineral']:
        precincts = countyShapes.loc[countyShapes.County == county]
        precincts['Precinct'] = 0
        precincts = precincts[['Precinct','geometry']]
    else:
        precincts = gpd.read_file('PrecinctShapefiles/Voter_Precincts_' + \
        county.replace(' ','_') + '_County/Voter_Precincts_' + county.replace(' ','_') + \
        '_County.shp')[[precinctCol[county],'geometry']].rename(index=str,\
        columns={precinctCol[county]:'Precinct'})
    if precincts.crs['init'] != 'epsg:4326':
        precincts['geometry'] = precincts['geometry'].to_crs(epsg=4326)
    if county == 'Grand':
        precincts['Precinct'] = precincts['Precinct'].str.replace('precinct','')
    if county == 'Gunnison':
        precincts['Precinct'] = precincts['Precinct'].str.replace('Precinct ','').astype(int)
        precincts.loc[precincts.Precinct.isin([8,9,10,12,13,14,15]),'Precinct'] += 3055926000
        precincts.loc[precincts.Precinct.isin([1,2,3,4,5,6,7,11]),'Precinct'] += 3056126000
    if county == 'Delta':
        precincts['Precinct'] = precincts['Precinct'].astype(int)
        precincts.loc[precincts.Precinct > 7,'Precinct'] += 3056115000
        precincts.loc[precincts.Precinct <= 7,'Precinct'] += 3055415000
    if county == 'Park':
        precincts['Precinct'] = precincts['Precinct'].str.replace('Precinct #','').astype(int)
        precincts.loc[precincts.Precinct.isin([8,10,11,12,13]),'Precinct'] += 2026047000
        precincts.loc[precincts.Precinct.isin([1,2,3,4,5,6,7,9]),'Precinct'] += 5026047000
    if county in offsets:
        precincts.Precinct = precincts.Precinct.astype(int) + offsets[county]
    precincts['County'] = county
    if str(precincts.Precinct.dtype) not in ['int64','float64']:
        precincts.Precinct = precincts.Precinct.astype(int)
    precinctShapes = precinctShapes.append(precincts,ignore_index=True)
    del precincts
del county
precinctShapes.Precinct = precinctShapes.Precinct.astype(int)
precinctShapes = precinctShapes.dissolve(by='Precinct').reset_index()
precinctShapes['Area'] = precinctShapes.geometry.area
conversion = pd.merge(left=precinctShapes.groupby('County').Area.sum().reset_index(),\
right=countyShapes[['County','Area']].rename(index=str,columns={'Area':'ActualArea'}),\
how='inner',left_on='County',right_on='County')
area_factor = (conversion['ActualArea']/conversion['Area']).mean()
precinctShapes['Area'] *= area_factor
del conversion, area_factor
byPrecinct = pd.merge(left=byPrecinct,right=precinctShapes[['Precinct','County','Area']],\
how='inner',left_on=['Precinct','County'],right_on=['Precinct','County'])
byPrecinct['Voter Density'] = byPrecinct['Ballots Cast']/byPrecinct['Area']
byPrecinct['Flippable'] = ((byPrecinct['Flippability'] >= 0) & (byPrecinct['Voter Density'] >= 100)).astype(int)
del precinctShapes['Area']

""" Creating Urban/Urban Suburban/Rural Suburban/Rural Classification Using Voter Density """
""" If you group flippable counties by urb/sub/rur, many more voters in "urban suburban" precincts... """

byPrecinct['UrbSubRur'] = 0
cutoff = 0
for ind in range(1,4):
    while byPrecinct.loc[(byPrecinct['Voter Density'] < cutoff) | byPrecinct['Voter Density'].isnull(),'Total Voters'].sum()/byPrecinct['Total Voters'].sum() < 0.25*ind:
        cutoff += 0.1
    byPrecinct.loc[byPrecinct['Voter Density'] >= cutoff,'UrbSubRur'] = ind
del ind, cutoff

""" Inferring Democratic Primary Results by Precinct """

byPrecinct = pd.merge(left=byPrecinct,right=byCounty[['County','Primary Turnout %',\
'Johnston Primary %','Polis Primary %','Kennedy Primary %']],how='inner',left_on='County',right_on='County')
byPrecinct['Primary Ballots Cast'] = byPrecinct['Ballots Cast']*(byPrecinct['Lean'] + 0.5)*byPrecinct['Primary Turnout %']
byPrecinct['Primary Voter Density'] = byPrecinct['Primary Ballots Cast']/byPrecinct['Area']
byPrecinct['Johnston Primary Votes'] = byPrecinct['Primary Ballots Cast']*byPrecinct['Johnston Primary %']
byPrecinct['Johnston Voter Density'] = byPrecinct['Johnston Primary Votes']/byPrecinct['Area']
byPrecinct['Polis Primary Votes'] = byPrecinct['Primary Ballots Cast']*byPrecinct['Polis Primary %']
byPrecinct['Polis Voter Density'] = byPrecinct['Polis Primary Votes']/byPrecinct['Area']
byPrecinct['Kennedy Primary Votes'] = byPrecinct['Primary Ballots Cast']*byPrecinct['Kennedy Primary %']
byPrecinct['Kennedy Voter Density'] = byPrecinct['Kennedy Primary Votes']/byPrecinct['Area']

""" Saving Results to CSV """

byPrecinct.sort_values('Lean',ascending=False).to_csv('ElectionResults_CO/LeanElasticityTrend_ByPrecinct.csv',index=False)

""" Plotting Results """

precinctShapes = pd.merge(left=precinctShapes,right=byPrecinct,how='left',left_on=['County','Precinct'],right_on=['County','Precinct'])
precinctShapes.Lean *= 100
precinctShapes.Elasticity *= 100
precinctShapes.Trend *= 100
precinctShapes['Lean 2014'] *= 100
precinctShapes['Lean 2018'] *= 100
precinctShapes['Trump Effect'] *= 100
precinctShapes['Presidential Turnout %'] *= 100
precinctShapes['Midterm Turnout %'] *= 100
precinctShapes['Yes % on 73'] *= 100

""" Put in county averages for precincts with no voters """
precinctShapes = pd.merge(left=precinctShapes,right=countyShapes[['County','Lean','Elasticity','Trend','Trump Effect']]\
.rename(index=str,columns={'Lean':'County Lean','Elasticity':'County Elasticity','Trend':'County Trend','Trump Effect':'County Trump Effect'}),\
how='inner',left_on='County',right_on='County')
precinctShapes.loc[precinctShapes.Lean.isnull(),'Lean'] = precinctShapes.loc[precinctShapes.Lean.isnull(),'County Lean']
precinctShapes.loc[precinctShapes.Elasticity.isnull(),'Elasticity'] = precinctShapes.loc[precinctShapes.Elasticity.isnull(),'County Elasticity']
precinctShapes.loc[precinctShapes.Trend.isnull(),'Trend'] = precinctShapes.loc[precinctShapes.Trend.isnull(),'County Trend']
precinctShapes.loc[precinctShapes['Trump Effect'].isnull(),'Trump Effect'] = precinctShapes.loc[precinctShapes['Trump Effect'].isnull(),'County Trump Effect']
del precinctShapes['County Lean'], precinctShapes['County Elasticity'], \
precinctShapes['County Trend'], precinctShapes['County Trump Effect']

if plotPrecincts:
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + precinctShapes['Precinct'].astype(str) + '<br>Partisan Lean: '
    precinctShapes.loc[precinctShapes.Lean < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes.Lean < 0,'Lean']),1).astype(str)
    precinctShapes.loc[precinctShapes.Lean == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes.Lean > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes.Lean > 0,'Lean']),1).astype(str)
    precinctShapes.Label += '<br>Projected Voters: ' + round(precinctShapes['Ballots Cast']).map('{:,.0f}'.format)
    heatMap(precinctShapes,'Lean',-50,50,20,'RdBu',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPartisanLeanCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Partisan Elasticity: ' + round(precinctShapes.Elasticity,1).astype(str)
    heatMap(precinctShapes,'Elasticity',0,25,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPartisanElasticityCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Partisan Correlation: ' + round(precinctShapes.Correlation,2).astype(str)
    heatMap(precinctShapes,'Correlation',-1,0,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPartisanCorrelationCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + precinctShapes['Precinct'].astype(str) + '<br>Partisan Trend: '
    precinctShapes.loc[precinctShapes.Trend < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes.Trend < 0,'Trend']),1).astype(str)
    precinctShapes.loc[precinctShapes.Trend == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes.Trend > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes.Trend > 0,'Trend']),1).astype(str)
    heatMap(precinctShapes,'Trend',-2.5,2.5,20,'RdBu',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPartisanTrendCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + precinctShapes['Precinct'].astype(str) + '<br>2014 Lean: '
    precinctShapes.loc[precinctShapes['Lean 2014'] < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes['Lean 2014'] < 0,'Lean 2014']),1).astype(str)
    precinctShapes.loc[precinctShapes['Lean 2014'] == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes['Lean 2014'] > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes['Lean 2014'] > 0,'Lean 2014']),1).astype(str)
    precinctShapes['Label'] += '<br>2018 Lean: '
    precinctShapes.loc[precinctShapes['Lean 2018'] < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes['Lean 2018'] < 0,'Lean 2018']),1).astype(str)
    precinctShapes.loc[precinctShapes['Lean 2018'] == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes['Lean 2018'] > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes['Lean 2018'] > 0,'Lean 2018']),1).astype(str)
    precinctShapes['Label'] += '<br>Trump Effect: '
    precinctShapes.loc[precinctShapes['Trump Effect'] < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes['Trump Effect'] < 0,'Trump Effect']),1).astype(str)
    precinctShapes.loc[precinctShapes['Trump Effect'] == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes['Trump Effect'] > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes['Trump Effect'] > 0,'Trump Effect']),1).astype(str)
    heatMap(precinctShapes,'Trump Effect',-20,20,20,'RdBu',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctTrumpEffectCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Flippability: ' + round(precinctShapes.Flippability,2).astype(str)
    heatMap(precinctShapes,'Flippability',-2,2,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctFlippabilityCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + precinctShapes['Precinct'].astype(str) + '<br>Lean: '
    precinctShapes.loc[precinctShapes.Lean < 0,'Label'] += 'R+' + round(abs(precinctShapes.loc[precinctShapes.Lean < 0,'Lean']),1).astype(str)
    precinctShapes.loc[precinctShapes.Lean == 0,'Label'] += 'Even'
    precinctShapes.loc[precinctShapes.Lean > 0,'Label'] += 'D+' + round(abs(precinctShapes.loc[precinctShapes.Lean > 0,'Lean']),1).astype(str)
    precinctShapes['Label'] += '<br>Elasticity: ' + round(precinctShapes.Elasticity,1).astype(str)
    heatMap(precinctShapes.loc[precinctShapes.Flippable > 0],'Flippable',0,1,2,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/FlippablePrecinctsCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + precinctShapes['Precinct'].astype(str) + '<br>UrbSubRur: ' + precinctShapes.UrbSubRur.astype(str)
    heatMap(precinctShapes,'UrbSubRur',0,3,4,'plasma',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctUrbSubRurCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Ballots Cast: ' + \
    round(precinctShapes['Ballots Cast']).map('{:,.0f}'.format)
    heatMap(precinctShapes,'Ballots Cast',0,2000,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctNumberOfVotersCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Presidential Voter Turnout: ' + \
    round(precinctShapes['Presidential Turnout %'],1).astype(str) + '%'
    heatMap(precinctShapes,'Presidential Turnout %',60,85,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPresidentialVoterTurnoutCO.html',False)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Midterm Voter Turnout: ' + \
    round(precinctShapes['Midterm Turnout %'],1).astype(str) + '%'
    heatMap(precinctShapes,'Midterm Turnout %',60,85,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctMidtermVoterTurnoutCO.html',False)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Amendment 73 Yes %: ' + \
    round(precinctShapes['Yes % on 73'],1).astype(str) + '%'
    heatMap(precinctShapes,'Yes % on 73',30,50,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctAmendment73YesPctCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Voter Density: ' + \
    round(precinctShapes['Voter Density']).map('{:,.0f}'.format) + ' per sq. mi.'
    heatMap(precinctShapes,'Voter Density',0,1000,20,'Purples',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctVoterDensityCO.html',True)
    
    precinctShapes['Label'] = precinctShapes['County'] + ' County<br>Precinct: ' + \
    precinctShapes['Precinct'].astype(str) + '<br>Primary Voter Density: ' + \
    round(precinctShapes['Primary Voter Density']).map('{:,.0f}'.format) + ' per sq. mi.'
    heatMap(precinctShapes,'Primary Voter Density',0,700,20,'Blues',3,[countyShapes.geometry.centroid.y.mean(),\
    countyShapes.geometry.centroid.x.mean()],5.5,True,'ElectionResults_CO/PrecinctPrimaryVoterDensityCO.html',True)

""" Online Presence of Declared Candidates as of June 23, 2019 at 11pm """

popularity = pd.read_csv('ElectionResults_CO/OnlinePresence.csv')



