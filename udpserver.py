#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys
import traceback
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MIN_EVENT_DURATION_MILLIS = 500
MIN_MOTOR_UP_MILLIS = 500
WHOLE_CYCLE_MILLIS = 2000
MOTOR_ON = GPIO.LOW
MOTOR_OFF = GPIO.HIGH
# mutable state
leds=(18,23)
last_event_millis = 0
last_event_down = False
last_event_btn_id = None

def current_time_millis():
    return int(round(time.time() * 1000))

def log(message, tuple):
    message2 = "%d " + message
    tuple2 = (current_time_millis(),) + tuple
    print message2 % tuple2

def tick():
    global last_event_millis, last_event_down, last_event_btn_id
    if last_event_btn_id != None:
        if current_time_millis() >= last_event_millis:
            gpio_state = MOTOR_ON if last_event_down else MOTOR_OFF
            GPIO.output(leds[last_event_btn_id], gpio_state)
            # the other motor must be OFF
            GPIO.output(leds[abs(last_event_btn_id - 1)], MOTOR_OFF)
        else:
            log("future",())

def update_last_event(id, down):
    global last_event_millis, last_event_down, last_event_btn_id
    # did last event happen long in the past?
    now = current_time_millis()
    last_event_down = down
    last_event_btn_id = id
    # it is not safe to turn on motor for less than MIN_MOTOR_UP_MILLIS
    # does not matter when turning it on again
    if now - last_event_millis > MIN_MOTOR_UP_MILLIS:
        last_event_millis = now
    else:
        # if we are already in whole cycle (last event in future) and the event is down, cancel everything
        if last_event_millis <= now and down:
            last_event_millis = now
            log("Cancelling everything",())
        else:
            last_event_millis = now + WHOLE_CYCLE_MILLIS
            log("Scheduling whole cycle",())
    tick()

def btn_down(id):
    log("[%d]btn_down",  (id,))
    update_last_event(id, True)

def btn_up(id, millis):
    log("[%d]btn_up %d", (id, millis))
    update_last_event(id, False)

def process_message_with_id(id, message):
    if message == "btn_down":
        btn_down(id)
    elif message.startswith("btn_up"):
        # parse millis
        millis = int(message[len("btn_up "):])
        btn_up(id, millis)
    else:
        log("Got unknown message %s from %d", (message,id))

def process_message(message):
    if message.startswith("[0]"):
        process_message_with_id(0, message[3:])
    elif message.startswith("[1]"):
        process_message_with_id(1, message[3:])
    elif message == "":
        tick()
    else:
        log("Unknown message %s", (message,))

def check_idx(idx):
    if idx < 1 or idx > 40:
        print "Invalid index"
        exit

def main():
    if len(sys.argv) == 2:
        global vcc,leds
        led0 = int(sys.argv[2])
        led1 = int(sys.argv[3])
        leds = (led0, led1)
        check_idx(led0)
        check_idx(led1)
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(leds[0], GPIO.OUT)
        GPIO.setup(leds[1], GPIO.OUT)
        GPIO.output(leds[0], MOTOR_OFF)
        GPIO.output(leds[1], MOTOR_OFF)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            process_message(data)
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
