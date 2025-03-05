import streamlit as st
from data_load import load_raw_data
import os

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
    print ('Main: Signal shape {}'.format(signals.shape))
#     for signal_header in signal_headers:
#         print (signal_header['label'], signal_header['sample_frequency'])
#     print (header)
# print ('Done!')