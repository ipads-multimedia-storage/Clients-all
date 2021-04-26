import socket
import time
import json
import argparse

def receive_message():
    
    while 1:
        data = s.recvfrom(1024)[0]
        #print("Receive Data: ", data)
        try:
            response = json.loads(data.decode())
        except TypeError:
            print("Received Message With Wrong Format!!!")
            continue

        # get information related to object
        current_time = int(round(time.time() * 1000))
        print("time now is" + str(current_time))
        if response:
            print("object (ID:{})".format(str(response["id"])))
            print("\ttime: {}".format(str(response["time"])))
            #print("\tspeed: {}".format(str(response["speed"])))
            print("\tlocation: ({}, {})".format(str(response["x"]), str(response["y"])))
            #print("\tlatency: {}".format(str(current_time-response["time"])))
            # NOTE: AC.move will block execution of this thread
            if mode != 'debug':
                AC.move(response["x"]/10, response["y"]/10, response["angle"], 0, response["time"])

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', type=str, default='run', help="mode: run(with arm) or debug(without arm)")
    parser.add_argument('-s', '--server', type=str, default='localhost', help='server url')
    args = parser.parse_args()
    mode = args.mode
    server_url = args.server
    print("Your server's ip is: " + server_url)
    
    if mode == 'debug':
        print("Running without arm")
    else:
        import arm_controller as AC
        AC.move_to_init_pos()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(('NEW#'+str(int(round(time.time() * 1000)))+'#{"type":"Arm", "x":300, "y":820, "r":250}').encode(), (server_url, 50090))    

    receive_message()
