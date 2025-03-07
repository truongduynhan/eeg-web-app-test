import streamlit as st
from data_load import load_raw_data
import os
from datetime import datetime, timedelta

import plotly.graph_objs as go
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import chart_studio.plotly as py

from plotly import tools
from plotly.graph_objs import Layout, YAxis, Scatter, Scattergl, Annotation, Annotations, Data, Figure, Marker, Font

# import mne  # If this line returns an error, uncomment the following line
# from mne.datasets import sample

from streamlit_shortcuts.streamlit_shortcuts import add_keyboard_shortcuts

EPOCH_SIZE = 300

st.set_page_config(
    page_title="Visualize EEG",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Visualize EEG signals")

if "starting" not in st.session_state:
    st.session_state.starting = 0  # Initialize counter if not present

  

fn = 'data/chb01_01.edf'
if os.path.isfile(fn):
    signals, ch_names, signal_headers, header = load_raw_data(fn)
    st.write ('Signal shape {}'.format(signals.shape))
    for signal_header in signal_headers:
        print (signal_header['label'], signal_header['sample_frequency'])
    # st.write (header)
st.write ('Loading data is done!')

max_time = signals.shape[-1]/256

n_channels = signals.shape[0]
# data, times = raw[picks[:n_channels], start:stop]
# ch_names = [raw.info['ch_names'][p] for p in picks[:n_channels]]

with st.form("settings"):
    st.write("Settings")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input(label="Window size", value=10, key='window_size')
    with c2:
        st.number_input(label="Scale signal", value=16, key='scale_signal')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Window size", st.session_state.window_size, "Scale signal", st.session_state.scale_signal)


c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Prev Epoch", key="backward"):
        #  st.session_state.starting += EPOCH_SIZE # Move to next epoch (next 10mins)
        st.session_state.starting = max(st.session_state.starting - EPOCH_SIZE, 0)
        print ('starting+', st.session_state.starting)   

with c2:
    if st.button("Next Epoch", key="forward"):
        #  st.session_state.starting += EPOCH_SIZE # Move to next epoch (next 10mins)
        st.session_state.starting = min(st.session_state.starting + EPOCH_SIZE, max_time - EPOCH_SIZE)
        print ('starting+', st.session_state.starting)   

with c3:
    if st.button("Reset", key="reset"):
        st.session_state.starting = 0   
        print ('starting', st.session_state.starting)       

start = st.session_state.starting
stop =  min(st.session_state.starting + EPOCH_SIZE, max_time)
times = np.arange(start, stop, 1.0/256.0)

times = [datetime.strptime('2013-02-26', '%Y-%m-%d') + timedelta(seconds=_time) for _time in times]
# print (times[:10])
print ('starting', st.session_state.starting)

data = signals[:n_channels,start*256:stop*256] * st.session_state.scale_signal
ch_names = [signal_header['label'] for signal_header in signal_headers]
ch_names = ch_names[:n_channels]
# print ('data shape', data.shape, times.shape)
# print (times[:100])




# if st.button("Right", key="arrowright"):     
#      st.write("Clicked right", st.session_state.starting)
#      st.session_state.starting = st.session_state.starting + 1     
#      print ('starting', st.session_state.starting)

# add_keyboard_shortcuts({"ctrl+ArrowRight": "Right"})

# if st.button("Left", key="arrowleft"):     
#      st.write("Clicked left", st.session_state.starting)
#      st.session_state.starting = st.session_state.starting - 1
#      print ('starting', st.session_state.starting)

# add_keyboard_shortcuts({"ctrl+ArrowLeft": "Left"})

step = 1. / (n_channels + 1)
kwargs = dict(domain=[1 - step - step*0.5, 1], showticklabels=False, zeroline=False,             
              showgrid=False, fixedrange= True,
              range=[-5000,5000],
              minallowed=-5000,
              maxallowed=5000,)

# create objects for layout and traces
layout = Layout(yaxis=YAxis(kwargs), showlegend=False, 
                xaxis=dict(showticklabels=True, position=0),
                dragmode="pan",                 
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
traces = [Scattergl(x=times, y=data.T[:, 0], hovertext=None)]

# loop over the channels
for ii in range(1, n_channels):
        kwargs.update(domain=[max(1 - (ii + 1) * step - step*0.5, 0) , min(1 - ii * step, 1)])
        layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
        traces.append(Scattergl(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1), hovertext=None))
        
layout.update(margin=dict(l=60))

# add channel names using Annotations
annotations = Annotations([Annotation(x=0, y=0, xanchor='left', xref='paper', xshift=-60, yref='y%d' % (ii + 1),
                                      text=ch_name, font=Font(size=12), showarrow=False)
                          for ii, ch_name in enumerate(ch_names)])
layout.update(annotations=annotations)

# set the size of the figure and plot it
layout.update(autosize=False, width=1000, height=800)

# limit xrange
layout.update(xaxis=dict(range=[datetime.strptime('2013-02-26', '%Y-%m-%d') + timedelta(seconds=st.session_state.starting),
                                datetime.strptime('2013-02-26', '%Y-%m-%d') + timedelta(seconds=st.session_state.starting+st.session_state.window_size)],                      
                         ))

# Add range slider
layout.update(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=5,
                     label="5s",
                     step="second",
                     stepmode="todate"),
                dict(count=10,
                     label="10s",
                     step="second",
                     stepmode="todate"),
                dict(count=20,
                     label="20s",
                     step="second",
                     stepmode="todate"),
                dict(count=1,
                     label="60s",
                     step="minute",
                     stepmode="todate"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            # visible=True
        ),
        type="date"
    )
)


fig = Figure(data=Data(traces), layout=layout)
# py.iplot(fig, filename='shared xaxis')
print ('plotly_chart')

st.plotly_chart(fig)



     
          
