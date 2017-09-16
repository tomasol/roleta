#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import sys
import traceback
import socket

# constants
DISREGARD_FIRST_PUSHED_MILLIS = 100
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
btn = int(sys.argv[1])

def send(message):
    print "Sending %s" % message
    sock.sendto(message, (UDP_IP, UDP_PORT))

def btn_down():
    send("btn_down %d" % btn)

def btn_up(after_millis):
    send("btn_up %d %d" % (btn, after_millis))


def main():
    just_pushed=False
    pushed_millis=0
    if btn < 1 or btn > 40:
        print "Invalid index"
        exit
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        while 1:
            if GPIO.input(btn): # button is released
                if pushed_millis > DISREGARD_FIRST_PUSHED_MILLIS:
                    btn_up(pushed_millis)
                pushed_millis = 0
                just_pushed = False
            else:
                pushed_millis = pushed_millis + 1
                if pushed_millis > DISREGARD_FIRST_PUSHED_MILLIS and just_pushed == False:
                    # start push action
                    just_pushed = True
                    btn_down()
            time.sleep(0.001)
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
