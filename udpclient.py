#!/usr/bin/env python

# exec(open('./udpclient.py').read(), globals())
# or just import udpclient - separate namespace
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def send(message, btnId, sock):
    message = "[%d]%s" % (btnId, message)
    print "Sending %s" % message
    sock.sendto(message, (UDP_IP, UDP_PORT))

def send_heartbeat(sock):
    sock.sendto("", (UDP_IP, UDP_PORT))

def btn_down(btnId, sock):
    send("btn_down", btnId, sock)

def btn_up(after_millis, btnId, sock):
    send("btn_up %d" % after_millis, btnId, sock)


