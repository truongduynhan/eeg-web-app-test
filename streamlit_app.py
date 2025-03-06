import streamlit as st
from data_load import load_raw_data
import os

import plotly.graph_objs as go
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import chart_studio.plotly as py

import mne  # If this line returns an error, uncomment the following line
from mne.datasets import sample

st.set_page_config(
    page_title="Visualize EEG",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Visualize EEG signals")

fn = 'data/chb01_01.edf'
if os.path.isfile(fn):
    signals, signal_headers, header = load_raw_data(fn)
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


data_path = sample.data_path()

raw_fname =  '{}/MEG/sample/sample_audvis_filt-0-40_raw.fif'.format(data_path)
raw = mne.io.Raw(raw_fname, preload=False)
print(raw)
print(raw.ch_names[:5])

from plotly import tools
from plotly.graph_objs import Layout, YAxis, Scatter, Annotation, Annotations, Data, Figure, Marker, Font

picks = mne.pick_types(raw.info, meg='grad', exclude=[])
start, stop = raw.time_as_index([0, 10])

n_channels = 20
data, times = raw[picks[:n_channels], start:stop]
ch_names = [raw.info['ch_names'][p] for p in picks[:n_channels]]
print ('data shape', data.shape, times.shape)
# print (times[:100])

step = 1. / n_channels
kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False)

# create objects for layout and traces
layout = Layout(yaxis=YAxis(kwargs), showlegend=False, xaxis=dict(showticklabels=True, position=0))
traces = [Scatter(x=times, y=data.T[:, 0])]

# loop over the channels
for ii in range(1, n_channels):
        kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
        layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
        traces.append(Scatter(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1)))

layout.update(margin=dict(l=10))

# add channel names using Annotations
annotations = Annotations([Annotation(x=-0.08, y=0, xref='paper', yref='y%d' % (ii + 1),
                                      text=ch_name, font=Font(size=12), showarrow=False)
                          for ii, ch_name in enumerate(ch_names)] 
                        #   + 
                        #   [Annotation(x=-0.08, y=-0.05, xref='x%d' % (iii + 1), yref='paper',
                        #               text=ch_name, font=Font(size=12), showarrow=False)
                        #   for iii, ch_name in enumerate(times[::1000])]
                          )
layout.update(annotations=annotations)

# set the size of the figure and plot it
layout.update(autosize=False, width=1000, height=600)

# set position of x ticks
layout.update(xaxis=dict(tick0=2))

fig = Figure(data=Data(traces), layout=layout)
# py.iplot(fig, filename='shared xaxis')
print ('plotly_chart')
st.plotly_chart(fig)