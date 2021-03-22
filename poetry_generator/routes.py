from flask import Blueprint, render_template, request, redirect, current_app
from .generator import ai
from . import socketio

generator = Blueprint('generator', __name__)

from time import sleep
from random import random
from threading import Thread, Event

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace='/test')
        socketio.sleep(5)

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@generator.route('/')
def index():
    return render_template('index.html')

@generator.route('/poem', methods=['POST'])
def analyse():
    text = "hello"
    return render_template('index.html', text=text)