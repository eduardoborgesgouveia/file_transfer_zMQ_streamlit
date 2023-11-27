import streamlit as st
import pandas as pd
from io import StringIO
import zmq
ctx = zmq.Context()
CHUNK_SIZE = 250000
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    #st.write(bytes_data)

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    # st.write(dataframe)
    st.table(dataframe.head())
    dataframe.to_csv('file_upload.csv', index=False)

    dealer = ctx.socket(zmq.ROUTER)
    dealer.connect("tcp://172.23.32.1:6000")
    
    file = open('file_upload.csv', 'rb')

    while True: 
        # First frame in each message is the sender identity
        # Second frame is "fetch" command
        try:
            identity, command = dealer.recv_multipart()
            print(identity, command)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # shutting down, quit
            else:
                raise

        assert command == b"fetch"

        while True:
            data = file.read(CHUNK_SIZE)
            dealer.send_multipart([identity, data])
            if not data:
                break