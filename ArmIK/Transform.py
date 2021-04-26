import math

#机械臂原点即云台中心，距离摄像头画面中心的距离， 单位cm
image_center_distance = 20

#计算每个像素对应的实际距离
map_param_ = 0.037581999058713275 

#数值映射
#将一个数从一个范围映射到另一个范围
def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#将图形的像素坐标转换为机械臂的坐标系
#传入坐标及图像分辨率，例如(100, 100, (640, 320))
def convertCoordinate(x, y, size=(640, 480)):
    x = leMap(x, 0, size[0], 0, 640)
    x = x - 320
    x = -x
    x_ = round(x * map_param_, 2)
    x_ -= 1

    y = leMap(y, 0, size[1], 0, 480)
    y = 240 - y
    y = -y
    y_ = round(y * map_param_ + image_center_distance, 2)
    y_ += 1

    return x_, y_
    # TODO: coord conversion
    # return 0, 0

# 获取旋转的角度
# 参数：机械臂末端坐标, 木块旋转角
def getAngle(x, y, angle):
    theta6 = round(math.degrees(math.atan2(abs(x), abs(y))), 1)
    angle = abs(angle)
    
    if x < 0:
        if y < 0:
            angle1 = -(90 + theta6 - angle)
        else:
            angle1 = theta6 - angle
    else:
        if y < 0:
            angle1 = theta6 + angle
        else:
            angle1 = 90 - theta6 - angle

    if angle1 > 0:
        angle2 = angle1 - 90
    else:
        angle2 = angle1 + 90

    if abs(angle1) < abs(angle2):
        servo_angle = int(500 + round(angle1 * 1000 / 240))
    else:
        servo_angle = int(500 + round(angle2 * 1000 / 240))
    return servo_angle
