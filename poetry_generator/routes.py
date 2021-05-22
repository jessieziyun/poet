from flask import Blueprint, render_template
from .generator import poet
from . import socketio
import serial
import csv
import atexit
from collections import deque
import pandas as pd
from io import StringIO

generator = Blueprint('generator', __name__)
arduino = serial.Serial('/dev/tty.usbmodem14101', 9600)

import time
from threading import Thread, Event

thread = Thread()
thread_stop_event = Event()
poem = ""
last_poem = 0

class DataLogger:
    def __init__(self):
        self.csvfile = open('data.csv', 'a+')
        self.writer = csv.writer(self.csvfile)
        self.reader = csv.reader(self.csvfile)
        print("csv initiated")
        atexit.register(self.csvfile.close)
    def writeData(self, data):
        self.writer.writerow(data)
        print(data)
        self.csvfile.flush()
    def readData(self):
        lines = deque(self.csvfile, 2)
        print(lines)
        pd.read_csv(StringIO(''.join(lines)), header=None)


arduinoCSV = DataLogger()

def readArduino():
    global poem, last_poem, arduinoCSV
    time_elapsed = 0
    print("Reading Arduino serial")
    while not thread_stop_event.isSet():
        datastream = arduino.readline()
        datastring = datastream[0:len(datastream)-2].decode("utf-8")
        vals = datastring.split()
        # 0: soil moisture, 1: humidity, 2: temperature, 3: ecg
        current_time = time.time()
        time_elapsed = current_time - last_poem
        if int(vals[3]) < 800 and time_elapsed > 70:
            print("Generating poem...")
            poem = poet.generate_poetry(1) # val[0] / 100 or something
            print("=" * 20 + " START POEM " + "=" * 20)
            print(poem)
            print("=" * 20 + " END POEM " + "=" * 20)
            last_poem = time.time()
            socketio.emit('poem', {'poem': poem})
        if int(current_time) % 10 == 0:
            socketio.emit('arduinoread', {'humidity': vals[1], 'temperature': vals[2]})
        arduinoCSV.writeData([vals[0], vals[1], vals[2], vals[3]])
            # arduinoCSV.readData()

@socketio.on('connect')
def connect():
    global thread, poem
    print('Client connected')
    socketio.emit('poem', {'poem': poem})
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(readArduino)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@generator.route('/')
def index():
    return render_template('index.html')