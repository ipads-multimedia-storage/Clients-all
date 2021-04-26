import socket
import cv2
import numpy
import time
import sys
import json
import threading
import argparse

def send_video():
    global frame_size
    global fps
    global encode_rate
    global s

    # estimate frame_size and fps
    capture = cv2.VideoCapture(0)
    frame_size_tot = 0
    start_time = int(round(time.time()))
    itr = 100  # iteration times set to 100, you can change it as you want
    # jpeg, 'encode_rate' for quality, higher the number, higher the quality(0-100)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), encode_rate]
    for i in range(itr):
        ret, frame = capture.read()
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        frame_size_tot += data.size
    frame_size = frame_size_tot/itr/1000  # unit: KB
    time_interval = time.time() - start_time

    if time_interval <= 0:
        fps = 100
    else:
        fps = int(itr / time_interval)

    print("Average frame size is: " + str(frame_size) + "KB, fps is: " + str(fps))
    print("Initialization finished.")

    if 0 < fps_exp < fps:
        wait_time = int(1000 / fps_exp - 1000 / fps)
        print("Wait " + str(float(wait_time / 1000)) +
              " s every frame to match expected fps")
    else:
        wait_time = 0

    ret, frame = capture.read()  # ret == 1 for success, 0 for failure
    time_stamp = int(round(time.time() * 1000))  # record event time

    while ret:
        # time.sleep(0.01)  # you can put it to sleep in each loop to release the pressure of server
        reset_flag = False
        if needAdjust.is_set():  # need to adjust image quality to adapt to bandwidth
            encode_param[1] = int(encode_rate)
            reset_flag = True
            needAdjust.clear()
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        # built mat
        data = numpy.array(imgencode)
        if reset_flag:  # update frame size
            frame_size = data.size
        string_data = data.tostring()
        # 'current_time': enable server to calculate bandwidth
        current_time = int(round(time.time() * 1000))

        print("Send: ", len(string_data))
        body = ('POST#'+str(time_stamp)+'#').encode()+string_data
        s.sendto(body, (server_url, 50090))
        time.sleep(float(wait_time / 1000))
        # then read next frame
        ret, frame = capture.read()
        time_stamp = int(round(time.time() * 1000))
        # if cv2.waitKey(10) == 27:
        #     break

def detect_bandwidth():
    global encode_rate
    global frame_size
    global fps
    global s

    if fps_exp > 0:
        expected = fps_exp * frame_size
    else:
        expected = fps * frame_size
    up_count = down_count = 0
    average_bandwidth = 1000000  # unit: KB/s, 1GB/s for initial value
    while 1:
        data = s.recvfrom(1024)
        print("Receive Data: ", data)
        response = json.loads(data)

        # compare current bandwidth and expected bandwidth
        send_time = response["sendTime"]
        process_time = response["processTime"]
        data_length = response["dataLength"]
        transport_time = int(round(time.time() * 1000)) - send_time - process_time
        print("transport time: " + str(transport_time) + " ms")
        if transport_time > 0:
            bandwidth = data_length/transport_time*2
        else:
            bandwidth = 1000000
        average_bandwidth = min(average_bandwidth*0.8 + bandwidth*0.2, 1000000)

        print("current bandwidth: " + str(bandwidth) +
              " KB/s, average bandwidth: " + str(average_bandwidth) + " KB/s")
        if average_bandwidth < expected - 100:
            down_count += 1
            up_count = max(up_count-1, 0)
            if down_count > 5:
                encode_rate /= 2
                print("bandwidth is not enough, performing downgrade")
                down_count = 0
                needAdjust.set()
        if average_bandwidth > expected + 100 and encode_rate < 100:
            up_count += 1
            down_count = max(down_count-1, 0)
            if up_count > 5:
                if encode_rate < 100:
                    encode_rate = min(encode_rate + 10, 100)
                    print("bandwidth is enough, performing upgrade")
                    needAdjust.set()
                up_count = 0


if __name__ == '__main__':
    
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, default='localhost', help='server url')
    parser.add_argument('-f', '--fps', type=int, default=10, help='expected fps')
    parser.add_argument('-e', '--encodeRate', type=int, default=30, help='encoding rate(0-100, 100 for best)')
    args = parser.parse_args()
    fps_exp = args.fps
    server_url = args.server
    encode_rate = args.encodeRate
    print("Your server's ip is: " + server_url)
    print("Expected fps(-1 for disabled): " + str(fps_exp))
    print("Initial encoding rate is: " + str(encode_rate))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(('NEW#'+str(int(round(time.time() * 1000)))+'#{"type":"Camera", "x":500, "y":1150, "w":240, "h":180, "rot":-1.5707}').encode(), (server_url, 50090))

    fps = 0
    frame_size = 0
    needAdjust = threading.Event()
    t2 = threading.Thread(target=detect_bandwidth)
    t2.start()
    send_video()

