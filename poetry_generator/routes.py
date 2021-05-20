from flask import Blueprint, render_template, request, redirect, current_app
from .generator import poet
from . import socketio
import serial

generator = Blueprint('generator', __name__)
arduino = serial.Serial('/dev/tty.usbmodem14101', 9600)

import time
from random import random
from threading import Thread, Event

thread = Thread()
thread_stop_event = Event()
poem = ""
last_poem = 0

@socketio.on('connect')
def test_connect():
    socketio.emit('my response', {'data': 'Connected'})

def readArduino():
    global poem, last_poem
    time_elapsed = 0
    print("Reading Arduino serial")
    while not thread_stop_event.isSet():
        datastream = arduino.readline()
        decoded_proximity = float(datastream[0:len(datastream)-2].decode("utf-8"))
        # print(decoded_proximity)
        current_time = time.time()
        time_elapsed = current_time - last_poem
        if decoded_proximity < 800 and time_elapsed > 70:
            print("Generating poem...")
            poem = poet.generate_poetry()
            print("=" * 20 + " START POEM " + "=" * 20)
            print(poem)
            print("=" * 20 + " END POEM " + "=" * 20)
            last_poem = time.time()
            socketio.emit('poem', {'poem': poem})
        socketio.emit('arduinoread', {'number': decoded_proximity})
        socketio.sleep(1)

@socketio.on('connect')
def test_connect():
    global thread
    print('Client connected')
    socketio.emit('poem', {'poem': poem})

    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(readArduino)

@socketio.on('buttonclicked')
def handle_click(data):
    print("Generating poem...")
    global poem
    # start = time.time()
    poem = poet.generate_poetry()
    print(poem)
    # end = time.time()
    global last_poem
    last_poem = time.time()
    # print(end - start)
    socketio.emit('poem', {'poem': poem})

@generator.route('/')
def index():
    return render_template('index.html')