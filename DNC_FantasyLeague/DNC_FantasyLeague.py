#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:45:40 2020

@author: tefirman
"""

import re
import pandas as pd

picks = {'Joel':['healthcare','hope','hopes','hoping','racism','racist','police','policing','defund'],\
         'Ashley':['jobs','job','family','families','lewis','tweet','twitter'],\
         'Angela':['leader','leaders','leadership','working','billionaires','corporate','corporations'],\
         'Mike Kim':['soul','barack','obama','expert','experts','malarkey'],\
         'Jake':['progress','progressive','change','changes','changed','changing','community','communities','climate'],\
         'Shannon':['pandemic','covid','mail','postal','obamacare','build back'],\
         'Priya':['economy','economies','economic','science','scientist','scientists','scientific','middle class','essential workers','first responders'],\
         'Naoko':['fighter','tough','unity','unite','unites','social security','recovery act']}

scores = pd.DataFrame(columns=['Player','Night','Speaker','Word','Points'])
for speech in ['Night1_BernieSanders.txt','Night1_MichelleObama.txt','Night2_JillBiden.txt']:
    tempData = open(speech,'r')
    words = tempData.read()
    tempData.close()
    one_gram = re.sub('[^\w\s]',' ',words).lower().split()
    two_gram = [one_gram[ind] + ' ' + one_gram[ind + 1] for ind in range(len(one_gram) - 1)]
    for name in picks:
        for word in picks[name]:
            scores = scores.append({'Player':name,'Night':speech.split('_')[0],\
            'Speaker':speech.split('_')[1].split('.')[0],'Word':word,\
            'Points':one_gram.count(word) + two_gram.count(word)},ignore_index=True)
standings = scores.groupby('Player').Points.sum().sort_values(ascending=False).reset_index()
byWord = scores.groupby(['Player','Word']).Points.sum().sort_values(ascending=False).reset_index()
byNight = scores.groupby(['Player','Night']).Points.sum().unstack().reset_index()
bySpeaker = scores.groupby(['Player','Speaker']).Points.sum().unstack().reset_index()

def excelAutofit(df,name,writer):
    f = writer.book.add_format()
    f.set_align('center')
    f.set_align('vcenter')
    df.to_excel(writer,sheet_name=name,index=False)
    for idx, col in enumerate(df):
        series = df[col]
        max_len = min(max((series.astype(str).map(len).max(),len(str(series.name)))) + 1,50) + 5
        writer.sheets[name].set_column(idx,idx,max_len,f,{'hidden':col.split('_')[0] \
        in ['arriba','starfusion','ericscript','squid'] or col == 'Explained score'})
    writer.sheets[name].autofilter('A1:' + (chr(64 + (df.shape[1] - 1)//26) + \
    chr(65 + (df.shape[1] - 1)%26)).replace('@','') + str(df.shape[0] + 1))
    return writer

writer = pd.ExcelWriter('DNC_FantasyStandings.xlsx',engine='xlsxwriter')
writer = excelAutofit(standings,'Standings',writer)
writer.sheets['Standings'].conditional_format('B2:B' + str(standings.shape[0] + 1),\
{'type':'3_color_scale','min_color':'#FF6347','mid_color':'#FFD700','max_color':'#3CB371'})
writer = excelAutofit(byWord,'By Word',writer)
writer.sheets['By Word'].conditional_format('C2:C' + str(byWord.shape[0] + 1),\
{'type':'3_color_scale','min_color':'#FF6347','mid_color':'#FFD700','max_color':'#3CB371'})
writer = excelAutofit(byNight,'By Night',writer)
writer = excelAutofit(bySpeaker,'By Speaker',writer)
writer.save()

