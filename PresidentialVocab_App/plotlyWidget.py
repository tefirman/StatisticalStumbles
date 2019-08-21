#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 19:36:27 2019

@author: tefirman
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

""" ADD REPUBLICAN VS DEMOCRAT!!! """
""" FIX TIME ALIGNMENT ISSUE!!! """

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('Presidential_Vocabs.csv')
for col in df.columns:
    df[col] = df[col].fillna(0.0)
del col
df = pd.merge(left=df,right=pd.read_csv('Presidential_Parties.csv'),how='inner',on='President')
byParty = df.groupby(['Party','Word']).Count.sum().reset_index()
totCount = df.groupby('Party').Count.sum().reset_index().rename(index=str,columns={'Count':'Total'})
byParty = pd.merge(left=byParty,right=totCount,how='inner',on='Party')
byParty['Frequency'] = byParty.Count/byParty.Total
del byParty['Total'], totCount

available_indicators = df['Word'].unique()

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=['america','americans'],
                multi=True
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['By President','By Party']],
                value='By President',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '96%', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Barack Obama'}]}
        )
    ], style={'width': '96%', 'display': 'inline-block', 'padding': '0 20'})
])


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_graph(yaxis_column_name,xaxis_type):
    if xaxis_type == 'By Party':
        dff = byParty.loc[byParty['Word'].isin(yaxis_column_name)]
        for word in dff.Word.unique():
            for party in df.Party.unique():
                if party not in dff.Party.unique():
                    dff = dff.append({'Word':word,'Party':party,'Frequency':0.0},ignore_index=True)
        dff = dff.sort_values(by=['Word','Party'])
        return {
            'data': [go.Bar(
                x=dff.loc[dff.Word == word,'Party'],
                y=100*dff.loc[dff.Word == word,'Frequency'],
                name=word,
                hovertext=dff.loc[dff.Word == word,'Party'] + '<br>' + \
                dff.loc[dff.Word == word,'Word'] + ': ' + \
                round(100*dff.loc[dff.Word == word,'Frequency'],4).astype(str) + '%',
                hoverinfo="text"
            ) for word in yaxis_column_name],
            'layout': go.Layout(
                yaxis={
                    'title': '% of words',
                    'type': 'linear'
                },
                margin={'l': 60, 'b': 80, 't': 10, 'r': 50},
                height=450,
                barmode='group',
                hovermode='closest'
            )
        }
    else:
        dff = df.loc[df['Word'].isin(yaxis_column_name)]
        for word in dff.Word.unique():
            for president in df.President.unique():
                if president not in dff.President.unique():
                    dff = dff.append({'Word':word,'President':president,\
                    'Actual_Year':df.loc[df.President == president,'Actual_Year'].values[0],\
                    'Ngram_Year':df.loc[df.President == president,'Ngram_Year'].values[0],\
                    'Frequency':0.0},ignore_index=True)
        dff = dff.sort_values(by=['Word','Actual_Year'])
        return {
            'data': [go.Bar(
                x=dff.loc[dff.Word == word,'President'],
                y=100*dff.loc[dff.Word == word,'Frequency'],
                name=word,
                hovertext=dff.loc[dff.Word == word,'President'] + '<br>' + \
                dff.loc[dff.Word == word,'Word'] + ': ' + \
                round(100*dff.loc[dff.Word == word,'Frequency'],4).astype(str) + '%',
                hoverinfo="text"
            ) for word in yaxis_column_name],
            'layout': go.Layout(
                yaxis={
                    'title': '% of words',
                    'type': 'linear'
                },
                margin={'l': 60, 'b': 80, 't': 10, 'r': 50},
                height=450,
                barmode='group',
                hovermode='closest'
            )
        }

if __name__ == '__main__':
    app.run_server(debug=True)



