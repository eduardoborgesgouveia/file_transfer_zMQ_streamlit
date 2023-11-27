import time
import numpy as np
import pandas as pd
import os
from threading import Lock
import sys
from utils.threadHandler import ThreadHandler
from daqmx import NIDAQmxInstrument


FLAG_TESTE = False

def writeData():
    global daq, TIME_INTERVAL,mutex, tf_thread,data_um_sensor,fs, i,STEP_DATA
    mutex.acquire()
    if ((time.time() - tf_thread) >= TIME_INTERVAL):
        tf_thread = time.time()
        if not FLAG_TESTE:
            daq.ao0 = data_um_sensor[i]
        else:
            print(data_um_sensor[i])
        i = i + STEP_DATA
        if i >= len(data_um_sensor):
            i = 0

    mutex.release()


def normalizacao(data):
    max_value = max(data)
    min_value = min(data)
    multipl = 4
    return ((data - min_value)/(max_value - min_value))*multipl


if __name__ == '__main__':
    global daq, TIME_INTERVAL,mutex, tf_thread,data_um_sensor,fs,i ,STEP_DATA
    tf_thread = 0
    mutex = Lock()
    if not FLAG_TESTE:
        daq = NIDAQmxInstrument()
        print(daq)


    path = 'C:\\Users\\lmest\\OneDrive\\Documentos\\projetos\\beta_edge\\app\\data_benchmark\\Teste_4.npy'

    data = np.load(path)
    data = pd.DataFrame(data)

    data_um_sensor = data.iloc[:,0]
    fs = 10000
    TIME_INTERVAL = 1/fs
    # MAX_FS = fs
    MAX_FS = 500
    # TIME_INTERVAL = 1/MAX_FS
    if fs > MAX_FS:
        TIME_INTERVAL = 1/MAX_FS
    STEP_DATA = int(fs/MAX_FS)
    # STEP_DATA = 1
    i = 0
    
    data_um_sensor = normalizacao(data_um_sensor)



    threadAquisicao = ThreadHandler(writeData)
    threadAquisicao.start()
    input('Ctrl c to quit \n')