import time
import zmq
import numpy as np
from datetime import datetime
from daqmx import NIDAQmxInstrument


## Paramentros para rotina
NUMBER_SENSORS = 4
RATE = 2048
FLAG_MOCK_DATA = True


## buscando o NI Device
if not FLAG_MOCK_DATA:
    daq = NIDAQmxInstrument()
    print(daq)

## instanciando o socket zeroMQ
## para acessar, via WSL, o servidor zMQ que está rodando no windows é necessário verificar o caminho
## para isso é necessário executar: vim /etc/resolv.conf e ver o localhost
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")



def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype = str(A.dtype),
        shape = A.shape,
    )
    socket.send_json(md, flags|zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)

def decode_message(message):
    if "|" in message:
        dt = message.split("|")[1].strip()
        return int(dt)
    return 1

def get_like_data(fa, duration):
    samples = duration*fa
    edge_pyz_data = np.zeros((fa*duration,NUMBER_SENSORS))
    if not FLAG_MOCK_DATA:
        values = daq.ai0.capture(
                sample_count=samples, rate=fa,
                max_voltage=5.0, min_voltage=0,
                mode='single-ended referenced', timeout=duration+1
        )  # capture fa*dt samples from ai0 at a rate of fa in single-ended referenced mode
    else:
        values = np.random.randint(0,5,(1,fa*duration))
    for n in range(NUMBER_SENSORS):
        # print("sensor de numero: ", NUMBER_SENSORS)
        # copy_valeus = values.copy()
        # delay = int(samples*0.5)
        # aux = np.zeros_like(values)
        # size_array = len(aux)
        # # print("aux: ", aux)
        # # print("tamanho de aux: ", len(aux))
        # aux[0:size_array - delay] = copy_valeus[delay:size_array]
        # aux[delay:size_array] = copy_valeus[0:size_array-delay]
        # edge_pyz_data[:,n] = aux
        # values = aux
        edge_pyz_data[:,n] = values
    return edge_pyz_data

while True:
    try:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: {}".format(message))
        req_mess = message.decode()
        dt = decode_message(req_mess)
        print("duração [s]: ", dt)
        edge_pyz_data = np.zeros((RATE,4))
        if 'train' in req_mess:
            edge_pyz_data = get_like_data(RATE,dt)
        elif 'test' in req_mess:
            edge_pyz_data = get_like_data(RATE,dt)
            
        #  Send reply back to client
        send_array(socket,edge_pyz_data)
    except Exception as e:
        socket.send(b"error")
        print("erro: ", e)
        f = open("log.txt", "a")
        f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ": ERROR = " + str(e))
        f.close()
        