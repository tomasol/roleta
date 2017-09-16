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

DEFAULT_IDX = (17, 22)

def send(message, btnId, sock):
    message = "[%d]%s" % (btnId, message)
    print "Sending %s" % message
    sock.sendto(message, (UDP_IP, UDP_PORT))

def btn_down(btnId, sock):
    send("btn_down", btnId, sock)

def btn_up(after_millis, btnId, sock):
    send("btn_up %d" % after_millis, btnId, sock)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    btnId = int(sys.argv[1])
    if btnId < 0 or btnId > 1:
        print "Invalid id %s" % btnId
        sys.exit(1)
    btn = DEFAULT_IDX[btnId]
    if len(sys.argv) == 3:
        btn = int(sys.argv[2])
        if btn < 1 or btn > 40:
            print "Invalid index %s" % index
            sys.exit(1)
    print "Id %d uses pin index %d" % (btnId, btn)
    just_pushed=False
    pushed_millis=0
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        while 1:
            if GPIO.input(btn): # button is released
                if pushed_millis > DISREGARD_FIRST_PUSHED_MILLIS:
                    btn_up(pushed_millis, btnId, sock)
                pushed_millis = 0
                just_pushed = False
            else:
                pushed_millis = pushed_millis + 1
                if pushed_millis > DISREGARD_FIRST_PUSHED_MILLIS and just_pushed == False:
                    # start push action
                    just_pushed = True
                    btn_down(btnId, sock)
            time.sleep(0.001)
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
