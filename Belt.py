import socket
import time
import serial
import argparse

def send_message():
    while 1:
        data = ser.readline()
        print(data)

        s.sendto(('POST#'+str(int(round(time.time() * 1000)))+'#').encode()+data[:4], (server_url, 50090))
        

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, default='localhost', help='server url')
    parser.add_argument('-p', '--portx', type=str, default='/dev/ttyUSB0', help='serial portx')
    args = parser.parse_args()
    server_url = args.server
    portx = args.portx
    print("Your server's ip is: " + server_url)
    print("Your serial's portx is: " + server_url)
    

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(('NEW#'+str(int(round(time.time() * 1000)))+'#{"type":"Belt", "x":500, "y":750, "s":0, "w":200, "h":1300, "rot":0}').encode(), (server_url, 50090))

    ser = serial.Serial(portx, 9600, timeout=0.5)
    ser.flushInput()

    send_message()
