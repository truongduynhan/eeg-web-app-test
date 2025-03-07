import streamlit as st
from data_load import load_raw_data
import os

import plotly.graph_objs as go
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import chart_studio.plotly as py

from plotly import tools
from plotly.graph_objs import Layout, YAxis, Scatter, Annotation, Annotations, Data, Figure, Marker, Font

import mne  # If this line returns an error, uncomment the following line
from mne.datasets import sample

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
    st.write ('Main: Signal shape {}'.format(signals.shape))
    for signal_header in signal_headers:
        print (signal_header['label'], signal_header['sample_frequency'])
    # st.write (header)
st.write ('Done!')



# date_range = pd.date_range(start="2023-01-01", end="2023-12-31", freq='ME')
# data = date_range.month + np.random.normal(0, 1, size=len(date_range))
# data_green_line = np.linspace(start=20, stop=10, num=len(date_range)) + np.random.normal(0, 1, size=len(date_range))
# split_index = len(data) // 2

# trace_blue = go.Scatter(x=date_range[:split_index], y=data[:split_index], mode='lines', name='Blue Part', line=dict(color='blue'))
# trace_red = go.Scatter(x=date_range[split_index-1:], y=data[split_index-1:], mode='lines', name='Red Part', line=dict(color='red'))
# trace_green = go.Scatter(x=date_range, y=data_green_line, mode='lines', name='Green Line', line=dict(color='green'))

# data_combined = [trace_blue, trace_red, trace_green]

# layout = go.Layout(title='Combined Chart with Blue-Red Transition and Green Line',
#                    xaxis=dict(title='Date'),
#                    yaxis=dict(title='Data Value'),
#                    hovermode='closest')

# fig_combined = go.Figure(data=data_combined, layout=layout)

# st.plotly_chart(fig_combined)


# data_path = sample.data_path()

# raw_fname =  '{}/MEG/sample/sample_audvis_filt-0-40_raw.fif'.format(data_path)
# raw = mne.io.Raw(raw_fname, preload=False)
# print(raw)
# print(raw.ch_names[:5])

# fig1 = raw.plot()
# st.pyplot(fig1)

# picks = mne.pick_types(raw.info, meg='grad', exclude=[])
# start, stop = raw.time_as_index([0, 1000])

n_channels = 20
# data, times = raw[picks[:n_channels], start:stop]
# ch_names = [raw.info['ch_names'][p] for p in picks[:n_channels]]

st.number_input(label="Window size", value=10, key='window_size')

if st.button("Forward", key="forward"):
     st.session_state.starting += EPOCH_SIZE # Move to next epoch (next 10mins)
     print ('starting+', st.session_state.starting)   

start = st.session_state.starting
stop =  st.session_state.starting + EPOCH_SIZE
times = np.arange(start, stop, 1.0/256.0)

print ('starting', st.session_state.starting)

data = signals[:n_channels,start*256:stop*256]
ch_names = [signal_header['label'] for signal_header in signal_headers]
ch_names = ch_names[:n_channels]
print ('data shape', data.shape, times.shape)
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

step = 1. / n_channels
kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False, fixedrange= True)

# create objects for layout and traces
layout = Layout(yaxis=YAxis(kwargs), showlegend=False, 
                xaxis=dict(showticklabels=True, position=0),
                dragmode="pan")
traces = [Scatter(x=times, y=data.T[:, 0])]

# loop over the channels
for ii in range(1, n_channels):
        kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
        layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
        traces.append(Scatter(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1)))

layout.update(margin=dict(l=60))

# add channel names using Annotations
annotations = Annotations([Annotation(x=0, y=0, xanchor='left', xref='paper', xshift=-60, yref='y%d' % (ii + 1),
                                      text=ch_name, font=Font(size=12), showarrow=False)
                          for ii, ch_name in enumerate(ch_names)])
layout.update(annotations=annotations)

# set the size of the figure and plot it
layout.update(autosize=False, width=1000, height=600)

# limit xrange
layout.update(xaxis=dict(range=[st.session_state.starting,st.session_state.starting+st.session_state.window_size],
                         minallowed=st.session_state.starting,
                         maxallowed=st.session_state.starting+EPOCH_SIZE,
                         
                         ))


fig = Figure(data=Data(traces), layout=layout)
# py.iplot(fig, filename='shared xaxis')
print ('plotly_chart')

st.plotly_chart(fig)


  
     

if st.button("Reset", key="reset"):
     st.session_state.starting = 0   
     print ('starting', st.session_state.starting)  
     
          
