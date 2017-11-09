#!/usr/bin/env python

# Usage: 
# $0 whole_cycle_seconds
# $0 whole_cycle_seconds motor_0_pin motor_1_pin

import time
import RPi.GPIO as GPIO
import sys
import traceback
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
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
            # log("[%d] Switching motor on? %s", (last_event_btn_id, last_event_down))
            GPIO.output(leds[last_event_btn_id], gpio_state)
            # the other motor must be OFF
            GPIO.output(leds[abs(last_event_btn_id - 1)], MOTOR_OFF)
            # if both motors are off, set event to none
            if last_event_down == False:
                log("[%d] Switching motor off", (last_event_btn_id,))
                last_event_btn_id = None

def update_last_event(btn_id, down, released_after_millis):
    global last_event_millis, last_event_down, last_event_btn_id
    # did last event happen long in the past?
    now = current_time_millis()
    previous_event_down = last_event_down
    last_event_down = down
    last_event_btn_id = btn_id

    if down and last_event_millis > now:
        # if we are already in whole cycle (last event in future) and the event is down, cancel everything
        log("[%d] Cancelling everything",(btn_id,))
        last_event_millis = now
        last_event_down = False
    elif down == False and released_after_millis < MIN_MOTOR_UP_MILLIS:
        if previous_event_down == False:
            log("[%d] Blip after cancel detected, ignoring", (btn_id,))
        else:
            last_event_millis = now + WHOLE_CYCLE_MILLIS 
            log("[%d] Blip detected, scheduling release to %d", (btn_id,last_event_millis))
    else:
        # normal change
        log("[%d] Normal change to %s", (btn_id, "down" if down else "up"))
        last_event_millis = now
    tick()

def btn_down(btn_id):
    log("[%d]btn_down",  (btn_id,))
    update_last_event(btn_id, True, None)

def btn_up(btn_id, millis):
    log("[%d]btn_up %d", (btn_id, millis))
    update_last_event(btn_id, False, millis)

def process_message_with_id(btn_id, message):
    if message == "btn_down":
        btn_down(btn_id)
    elif message.startswith("btn_up"):
        # parse millis
        millis = int(message[len("btn_up "):])
        btn_up(btn_id, millis)
    else:
        log("Got unknown message %s from %d", (message,btn_id))

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
    global WHOLE_CYCLE_MILLIS
    if len(sys.argv) > 1:
        WHOLE_CYCLE_MILLIS = int(sys.argv[1]) * 1000
    if len(sys.argv) == 4:
        global vcc,leds
        led0 = int(sys.argv[2])
        led1 = int(sys.argv[3])
        print "Using %s %s as outputs" % (led0, led1)
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
