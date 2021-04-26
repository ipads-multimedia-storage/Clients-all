import sys
import os
import time
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

AK = ArmIK()

# turn on the light to red
def set_light():
    Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
    Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
    Board.RGB.show()

# turn off the light
def reset_light():
    Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
    Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
    Board.RGB.show()

# ring the buzzer for prompt
def set_buzzer(ring_time):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(ring_time)
    Board.setBuzzer(0)

def move_to_init_pos():
    Board.setBusServoPulse(1, 450, 300)
    rotater_reset()
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 500)

# make the arm move to specified position
def move_to_pos(x, y, z, movetime=None):
    result = AK.setPitchRangeMoving((x, y, z), -90, -90, 0, movetime)
    if result == False:
        return False
    
    # result[2] is the time spent to move to that position
    return result

# servo 1 (aka. gripper) is responsible to grab the object
def gripper_tighten(movetime=200):
    Board.setBusServoPulse(1, 600, movetime)

def gripper_loose(movetime=200):
    Board.setBusServoPulse(1, 220, movetime)

# servo 2 (aka. rotater) is responsible to rotate the gripper
def rotater_set_to(angle, movetime=200):
    Board.setBusServoPulse(2, angle, movetime)

def rotater_reset():
    rotater_set_to(500)


def convertByTimeInterval(image_x, image_y, speed, event_time):
    # XXX: where to get the direction of speed
    # assume it's along +x direction
    current_time = round(time.time() * 1000)
    # sleep time is 2.0s
    sleep_time = 2000
    # assume 200ms deviation
    episilon = 0
    # episilon = 200

    delta_time = current_time + sleep_time + episilon - event_time
    print("delta time: {}".format(delta_time))
    image_x += delta_time * speed * 0.001 * 0.001
    return image_x, image_y
    
def move(image_x, image_y, angle, speed=None, event_time=None, needInfer=True):
    # convert image coord to world coord
    #print(image_x, image_y)
    #world_x, world_y = convertCoordinate(image_x, image_y)
    #print(world_x, world_y)
    #if needInfer:
    #    world_x, world_y = convertByTimeInterval(world_x, world_y, speed, event_time)

    world_x, world_y = image_x, image_y
    # set light and buzzer just for a prompt
    set_light()
    set_buzzer(0.1)
    
    print(world_x, world_y)
    result = move_to_pos(world_x, world_y, 10, 800)
    
    if result == False:
        print("cannot move to specified position")
        return False
    
    time.sleep(0.8)

    rotater_angle = getAngle(world_x, world_y, angle)
    gripper_loose()
    rotater_set_to(rotater_angle)
    time.sleep(0.2)
    
    move_to_pos(world_x, world_y, 3, 200)
    time.sleep(0.2)

    # at this point, gripper should arrive at the catching position
    # so the total sleep time is 2.1s

    gripper_tighten()
    # if not perform well, 
    # we could lower the sleep time here to let gripper catch more quickly
    
    # sleep 0.2s more to grip well
    time.sleep(0.4)

    rotater_reset()
    move_to_pos(world_x, world_y, 12, 200)
    time.sleep(0.2)

    coord_to_put = (-14.5, 11.5)

    result = move_to_pos(coord_to_put[0], coord_to_put[1], 12, 600)
    assert result != False
    time.sleep(0.6)
    
    rotater_angle = getAngle(coord_to_put[0], coord_to_put[1], -90)
    rotater_set_to(rotater_angle)
    time.sleep(0.2)

    # result = move_to_pos(coord_to_put[0], coord_to_put[1], 4.5)
    # time.sleep(0.5)
    
    result = move_to_pos(coord_to_put[0], coord_to_put[1], 3, 200)
    time.sleep(0.2)

    gripper_loose(200)
    time.sleep(0.2)

    result = move_to_pos(coord_to_put[0], coord_to_put[1], 12, 200)
    time.sleep(0.2)

    move_to_init_pos()
    time.sleep(0.5)

    reset_light()
    