#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys
import traceback
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005


def btn_down(id, leds):
    print "[%d]btn_down" % id
    GPIO.output(leds[id], GPIO.HIGH)

def btn_up(id, leds, millis):
    print "[%d]btn_up %d" % (id, millis)
    GPIO.output(leds[id], GPIO.LOW)

def process_message_with_id(id, leds, message):
    if message == "btn_down":
        btn_down(id, leds)
    elif message.startswith("btn_up"):
        # parse millis
        millis = int(message[len("btn_up "):])
        btn_up(id, leds, millis)
    else:
        print "Got unknown message %s from %d" % (message,id)

def process_message(message, leds):
    if message.startswith("[0]"):
        process_message_with_id(0, leds, message[3:])
    elif message.startswith("[1]"):
        process_message_with_id(1, leds, message[3:])
    else:
        print "Unknown message %s" % message

def check_idx(idx):
    if idx < 1 or idx > 40:
        print "Invalid index"
        exit

def main():
    led0 = 18
    led1 = 23
    if len(sys.argv) == 2:
        led0 = int(sys.argv[1])
        led1 = int(sys.argv[2])
    check_idx(led0)
    check_idx(led1)
    leds = (led0, led1)
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(led0, GPIO.OUT)
        GPIO.setup(led1, GPIO.OUT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            process_message(data, leds)
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
