# -*- coding: utf-8 -*-
from pprint import pprint
import pymongo
from pymongo import MongoClient
import plotly.offline as pyoff
import plotly.graph_objs as go
from datetime import datetime
from dateutil import tz
import numpy
from scipy import stats as st

keyword = u'Casio tr600'
client = MongoClient('59.110.155.140',27017)
db = client['xianyu_exchange']
coll = db[keyword]

last_request = coll.find_one({},sort=[("last_modified", pymongo.DESCENDING)])

last_modified = last_request['last_modified']
from_zone = tz.tzutc()
to_zone = tz.tzlocal()
utc = last_modified
utc = utc.replace(tzinfo=from_zone)
central = utc.astimezone(to_zone)
last_modified = central.strftime("%Y-%m-%d %H:%M:%S")

x_price = []
price_median = 0
for item in last_request['items']:
    price = item['price']
    x_price.append(price) 
price_median = numpy.median(x_price)
(mode,count) = st.mode(x_price)
price_mode = mode[0] 

print last_request['last_modified']

data = [go.Histogram(x=x_price,xbins={'start':1000,'end':'9000','size':'100'},histnorm='')]

layout = go.Layout(
        title=keyword+u' 市场价格分布,采样时间: '+last_modified,
        xaxis=dict(
                    title='价格（元）',
                    titlefont=dict(
                                    size=16,
                                    color='rgb(107, 107, 107)'
                                ),
                    tickfont=dict(
                                    size=14,
                                    color='rgb(107, 107, 107)'
                                )
                ),
        yaxis=dict(
                    title='数量',
                    titlefont=dict(
                                    size=16,
                                    color='rgb(107, 107, 107)'
                                ),
                    tickfont=dict(
                                    size=14,
                                    color='rgb(107, 107, 107)'
                                )
                ),
        legend={
                    'x':0,
                    'y':1.0,
                    'bgcolor':'rgba(255, 255, 255, 0)',
                    'bordercolor':'rgba(255, 255, 255, 0)'
                },
        shapes=[
                    {'type': 'line',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': price_median,
                    'y0': 0,
                    'x1': price_median,
                    'y1': 0.95,
                    'opacity': 0.7,
                    'line': {
                                'color': '#EB89B5',
                                'width': 2.5
                            }
                    }
                ],
        annotations=[
                 dict(
                    x=price_median,
                    y=0.9,
                    xref='x',
                    yref='paper',
                    text='市场均价 ' + str(int(price_median)),
                    showarrow=True,
                    arrowhead=2,
                    ax=-40
                    ),
                dict(
                    x=price_mode,
                    y=0.95,
                    xref='x',
                    yref='paper',
                    text='报价数量最多  ' + str(int(price_mode)),
                    showarrow=True,
                    arrowhead=2,
                    ax=40
                    )

                ]
                
                
)

fig = go.Figure(data=data,layout=layout)

pyoff.plot(fig, filename='price_histogram.html')
