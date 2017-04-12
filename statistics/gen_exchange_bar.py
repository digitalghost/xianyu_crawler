# -*- coding: utf-8 -*-
from pprint import pprint
import pymongo
from pymongo import MongoClient
import plotly.offline as pyoff
import plotly.graph_objs as go
from datetime import datetime
from dateutil import tz


keyword = u'iphone 7 plus 256gb'
client = MongoClient('localhost',27017)
db = client['xianyu_exchange']
coll = db[keyword]
coll_exchange = db[keyword + '_exchange']
x_axis = []
in_trace_y = []
in_trace_texts = []
out_trace_y = []
out_trace_texts = []

for exchange in coll_exchange.find():
    compare_end_time = exchange['compare_end']
    # METHOD 1: Hardcode zones:
    #from_zone = tz.gettz('UTC')
    #to_zone = tz.gettz('America/New_York')
    # METHOD 2: Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = compare_end_time
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)
    # Convert time zone
    central = utc.astimezone(to_zone)
    compare_end_time = central.strftime("%Y-%m-%d %H:%M:%S")
    x_axis.append(compare_end_time)
    inc_cnt = len(exchange['inc'])
    dec_cnt = len(exchange['dec'])
    in_trace_y.append(inc_cnt)
    out_trace_y.append(dec_cnt)
    in_text = ''
    for inc_item in exchange['inc']:
        in_text = in_text + inc_item['title'] + '<br>'
    in_trace_texts.append(in_text)
    out_text = ''
    for out_item in exchange['dec']:
        out_text = out_text + out_item['title'] + '<br>'
    out_trace_texts.append(out_text)
client.close()

in_trace = go.Bar(
        x=x_axis,
        y=in_trace_y,
        name='流入',
        text = in_trace_texts,
        textposition = "top",
        marker=dict(
                    color='rgb(55, 83, 109)'
                )
)
out_trace = go.Bar(
        x=x_axis,
        y=out_trace_y,
        name='流出',
        text = out_trace_texts,
        textposition = "top",
        marker=dict(
                    color='rgb(26, 118, 255)'
                )
)
data = [in_trace, out_trace]
layout = go.Layout(
        title=keyword+u' 市场流入流出',
        xaxis=dict(
                    tickfont=dict(
                                    size=14,
                                    color='rgb(107, 107, 107)'
                                )
                ),
        yaxis=dict(
                    title='流入流出量（单）',
                    titlefont=dict(
                                    size=16,
                                    color='rgb(107, 107, 107)'
                                ),
                    tickfont=dict(
                                    size=14,
                                    color='rgb(107, 107, 107)'
                                )
                ),
        legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
)

fig = go.Figure(data=data, layout=layout)
pyoff.plot(fig, filename='exchange_info.html')

