from flask import Blueprint, render_template
from .generator import poet
from .data import DataLog
from . import socketio
import serial

generator = Blueprint('generator', __name__)
arduino = serial.Serial('/dev/tty.usbmodem14101', 9600)

import time
from threading import Thread, Event

thread = Thread()
thread_stop_event = Event()
poem = ""
last_poem = 0

database = DataLog()

def readArduino():
    global poem, last_poem, database
    time_elapsed = 0
    print("Reading Arduino serial")
    while not thread_stop_event.isSet():
        datastream = arduino.readline()
        datastring = datastream[0:len(datastream)-2].decode("utf-8")
        vals = datastring.split()
        current_time = time.time()
        time_elapsed = current_time - last_poem
        if int(vals[4]) > 600 and time_elapsed > 120:
            mood = database.getMood()
            if mood > 0.5:
                print("Generating poem with temperature {}...".format(mood))
                poem = poet.generate_poetry(mood)
                print("=" * 20 + " START POEM " + "=" * 20)
                print(poem)
                print("=" * 20 + " END POEM " + "=" * 20)
                database.logInteraction(current_time)
                last_poem = time.time()
                socketio.emit('poem', {'poem': poem})
        if int(current_time) % 60 == 0:
            humidity, temperature = database.getHumidityAndTemperature()
            socketio.emit('mood', {'soil_moisture': database.getSoil(), 'humidity': humidity, 'temperature': temperature, 'luminosity': database.getLuminosity(), 'interaction': database.getInteraction()})
        database.logData(current_time, vals)
        socketio.sleep(1)

@socketio.on('connect')
def test_connect():
    global thread, poem, database
    print('Client connected')
    socketio.emit('poem', {'poem': poem})
    humidity, temperature = database.getHumidityAndTemperature()
    socketio.emit('arduinoread', {'soil_moisture': database.getSoil(), 'humidity': humidity, 'temperature': temperature, 'luminosity': database.getLuminosity(), 'interaction': database.getInteraction()})
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(readArduino)

@generator.route('/')
def index():
    return render_template('index.html')