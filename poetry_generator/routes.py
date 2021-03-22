from flask import Blueprint, render_template, request, redirect, current_app
from .generator import ai
from . import socketio
import serial

generator = Blueprint('generator', __name__)
arduino = serial.Serial('/dev/tty.usbmodem14201', 9600)

from time import sleep
from random import random
from threading import Thread, Event

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def readArduino():
    print("Reading Arduino serial")
    while not thread_stop_event.isSet():
        datastream = arduino.readline()
        decoded_proximity = float(datastream[0:len(datastream)-2].decode("utf-8"))
        print(decoded_proximity)
        socketio.emit('arduinoread', {'number': decoded_proximity}, namespace='/arduino')
        socketio.sleep(1)

@socketio.on('connect', namespace='/arduino')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(readArduino)

@generator.route('/')
def index():
    return render_template('index.html')