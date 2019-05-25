#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 08:58:11 2019

@author: firman.taylor
"""

import numpy as np
import plotly.graph_objs as graph_objs
from plotly.offline import init_notebook_mode, plot
init_notebook_mode()
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

def logFactorial(value):
    """
    Returns the log of the factorial of the value given
    Uses Sterling's Approximation for very large numbers
    """
    if all([value > 0,abs(round(value) - value) < 0.000001,value <= 500]):
        return sum(np.log(range(1,int(value) + 1)))
    elif all([value > 0,abs(round(value) - value) < 0.000001,value > 500]):
        return float(value)*np.log(float(value)) - float(value) + \
        0.5*np.log(2.0*np.pi*float(value)) - 1.0/(12.0*float(value))
    elif value == 0:
        return float(0)
    else:
        return float('nan')

def anyPlayerZeroMatch(gridSize,cardsInDeck):
    """
    Returns an array containing the probabilities of either player winning
    with the other player having zero matches after that many cards have
    been revealed, i.e. the value at index 20 is the zero match probability
    when 20 cards have been revealed.
    """
    diffGridProb = np.exp(2*logFactorial(cardsInDeck - gridSize) - \
    logFactorial(cardsInDeck - 2*gridSize) - logFactorial(cardsInDeck))
    winProbs = [0.0 for turns in range(gridSize)]
    winProbs.extend([np.exp(logFactorial(cardsInDeck - 2*gridSize) + logFactorial(turns - 1) + \
    logFactorial(cardsInDeck - turns) + np.log(gridSize) - logFactorial(turns - gridSize) - \
    logFactorial(cardsInDeck - gridSize - turns) - logFactorial(cardsInDeck)) \
    for turns in range(gridSize,cardsInDeck + 1 - gridSize)])
    winProbs.extend([0.0 for turns in range(gridSize)])
    return 2*diffGridProb*np.array(winProbs)

""" Calculating Zero Match Probability for Standard Parameters """

gridSize = 16
cardsInDeck = 54
totProb = anyPlayerZeroMatch(gridSize,cardsInDeck)

""" Plotting the Standard Probability as a Function of Cards Revealed """

data = [graph_objs.Scatter(
    x = np.arange(len(totProb)),
    y = 1e13*totProb,
    mode = 'lines+markers',
    marker= dict(size=6),
    name = 'Analytical',
    line = dict(width=3,color='blue')
)]

layout = dict(xaxis=dict(title='# of turns',range=[-1,55],dtick=10),
yaxis=dict(title='Probability of either player<br>ending with zero matches',dtick=2),
legend=dict(x=0.9,y=1),height=400,width=500,
margin=graph_objs.layout.Margin(l=50,r=50,b=100,t=50),
annotations=[{"x": 0.03, "y": 1.0,"font": {"size": 12},
"showarrow":False,"text":"x 10<sup>-13","xanchor":"center",\
"xref":"paper","yanchor":"bottom","yref":"paper"}])

fig = dict(data=data, layout=layout)
plot(fig, filename='Loteria_ZeroMatches.html')
del data, layout, fig

""" Slider Graph of Grid Size and Deck Size Dependencies """

gridSizeVals = np.arange(1,31)
deckSizeVals = np.arange(1,101)

data = [graph_objs.Scatter(
    x = deckSizeVals,
    y = [sum(anyPlayerZeroMatch(gridSize,cardsInDeck)) for cardsInDeck in deckSizeVals],
    mode = 'lines+markers',
    marker= dict(size=6),
    name = 'Unique Images',
    line = dict(width=3,color='blue'),
    xaxis='x1',yaxis='y1',
    visible = False
) for gridSize in gridSizeVals]
data[15]['visible'] = True

steps = []
for i in range(len(data)):
    step = dict(
        method = 'restyle',
        label = str(gridSizeVals[i]),
        args = ['visible', [False] * len(data)],
    )
    step['args'][1][i] = True
    steps.append(step)

sliders = [dict(
    active = 15,
    currentvalue = {"prefix": "Grid Size, G = "},
    pad = {"t": 50},
    steps = steps
)]

layout = dict(sliders=sliders,height=500,width=800,\
margin=graph_objs.layout.Margin(l=50,r=50,b=100,t=20),\
xaxis=dict(title='Unique Images, D'),\
yaxis=dict(title='Zero Match Probability, P<sub>tot',anchor='x2'))
fig = dict(data=data, layout=layout)
plot(fig, filename='Loteria_Slidebar.html')

""" Simulation of Small Number Scenarios for Verification """

numSims = 300000
if os.path.exists('LoteriaSimulations.csv'):
    simulations = pd.read_csv('LoteriaSimulations.csv')
else:
    simulations = pd.DataFrame(columns=['Players','GridSize','CardsInDeck','Total','Zero'])
for gridSize in range(3,6):
    for cardsInDeck in range(gridSize*2,11):
        totProb = anyPlayerZeroMatch(gridSize,cardsInDeck)
        print('Grid Size = ' + str(gridSize) + ', Deck Size = ' + str(cardsInDeck))
        print('Probability of either player ending with a zero-match: ' + str(sum(totProb)))
        
        deck = np.arange(cardsInDeck)
        loteriaCards = np.array([np.arange(cardsInDeck) for ind in range(2)])
        for numTry in range(simulations.loc[(simulations.Players == 2) & \
        (simulations.GridSize == gridSize) & (simulations.CardsInDeck == cardsInDeck)].shape[0],numSims):
            if numTry%1000 == 0:
                print('Try #' + str(numTry) + ', ' + str(datetime.datetime.now()))
                simulations.to_csv('LoteriaSimulations.csv',index=False)
            np.random.shuffle(deck)
            _ = [np.random.shuffle(loteriaCards[ind,:]) for ind in range(len(loteriaCards))]
            turns = gridSize
            while np.all(np.sum(np.isin(loteriaCards[:,:gridSize],deck[:turns]),axis=1) < gridSize):
                turns += 1
            vals = {'Players':2,'GridSize':gridSize,'CardsInDeck':cardsInDeck,'Total':turns}
            turns = cardsInDeck - gridSize
            while np.all(np.sum(np.isin(loteriaCards[:,:gridSize],deck[:turns]),axis=1) > 0):
                turns -= 1
            vals['Zero'] = turns
            simulations = simulations.append(vals,ignore_index=True)
            del turns, vals
        simulations.to_csv('LoteriaSimulations.csv',index=False)
        
        graphSims = simulations.loc[(simulations.Players == 2) & \
        (simulations.GridSize == gridSize) & (simulations.CardsInDeck == cardsInDeck)]
        
        simHist,simInds = np.histogram(np.array(graphSims.Total)\
        [np.array(graphSims.Zero) >= np.array(graphSims.Total)],\
        bins=np.arange(cardsInDeck + 2) - 0.5)
        simHist = simHist/len(graphSims.Total)
        simInds = simInds[:-1] + 0.5
        plt.figure()
        plt.plot(range(len(totProb)),totProb)
        plt.plot(simInds,simHist,'.',markersize=10)
        plt.grid(True)
        plt.legend(['Analytical','Simulation'])
        plt.xlabel('# of cards')
        plt.ylabel('Probability of game ending on that turn\nwith one player having zero matches')
        plt.title('Grid Size = ' + str(gridSize) + ', Deck Size = ' + str(cardsInDeck))
        plt.savefig('NoMatchWinProb_Grid' + str(gridSize) + '_Deck' + str(cardsInDeck) + '.png')
        plt.close()
        del simHist, simInds
    
    del cardsInDeck
del gridSize



