from pyedflib import highlevel
import os
import streamlit as st

@st.cache_data
def load_raw_data(fn):
    signals, signal_headers, header = highlevel.read_edf(fn)
    return signals, signal_headers, header

if __name__ == '__main__':
    fn = 'data/chb01_03.edf'
    if os.path.isfile(fn):
        signals, signal_headers, header = load_raw_data(fn)
    print ('Signal shape {}'.format(signals.shape))
    for signal_header in signal_headers:
        print (signal_header['label'], signal_header['sample_frequency'])
    print (header)
    print ('Done!')