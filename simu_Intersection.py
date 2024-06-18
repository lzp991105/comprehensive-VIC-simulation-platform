import random
import time
import threading
import pygame
import sys
from VECGUI import *
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from openpyxl import Workbook, load_workbook
import os

# Default values of signal timers信号定时器的默认值
# 四对键-值对
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 20
defaultYellow = 10

signals = []

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}  # average speeds of vehicles

# Coordinates of vehicles' start车辆启动坐标
# x = {'right': [0, 0, 0], 'down': [770, 698, 623], 'left': [1551, 1551, 1551], 'up': [789, 855, 930]}
# y = {'right': [796, 862, 936], 'down': [0, 0, 0], 'left': [780, 630, 565], 'up': [1558, 1558, 1558]}
x = {'right': [0, 0, 0], 'down': [657, 627, 602], 'left': [1400, 1400, 1400], 'up': [697, 727, 755]}
y = {'right': [436, 466, 498], 'down': [0, 0, 0], 'left': [398, 370, 348], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count信号图像、计时器和车辆计数的坐标
# signalCoods = [(456, 456), (1093, 456), (1093, 1030), (456, 1030)]  # 红绿灯坐标
# signalTimerCoods = [(456, 436), (1093, 436), (1093, 1010), (456, 1010)]  # 计时器坐标
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]  # 红绿灯坐标
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]  # 计时器坐标

# Coordinates of stop lines 停止线坐标
# stopLines = {'right': 520, 'down': 512, 'left': 1036, 'up': 1044}
# defaultStop = {'right': 510, 'down': 502, 'left': 1046, 'up': 1054}
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles 车辆之间的间隙
stoppingGap = 25  # stopping gap 停止间隙
movingGap = 25  # moving gap 移动间隙

# set allowed vehicle types here 在此处设置允许的车辆类型
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': False}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {0: [], 1: [], 2: []}, 'down': {0: [], 1: [], 2: []}, 'left': {0: [], 1: [], 2: []},
                  'up': {0: [], 1: [], 2: []}}
vehiclesNotTurned = {'right': {0: [], 1: [], 2: []}, 'down': {0: [], 1: [], 2: []}, 'left': {0: [], 1: [], 2: []},
                     'up': {0: [], 1: [], 2: []}}
rotationAngle = 3
mid = {'right': {'x': 646, 'y': 909}, 'down': {'x': 600, 'y': 300}, 'left': {'x': 898, 'y': 643},
       'up': {'x': 893, 'y': 882}}
# set random or default green signal time here  在此处设置随机或默认绿色信号时间
randomGreenSignalTimer = True
# set random green signal time range here 在此设置随机绿色信号时间范围
randomGreenSignalTimerRange = [10, 20]

pygame.init()
simulation = pygame.sprite.Group()


class TrafficLight:
    def __init__(self, state):
        self.state = state  # 红绿灯状态，0代表红灯，1代表绿灯，2代表黄灯
        if (self.state == 0):
            self.time = 20
        else:
            self.time = 10  # 记录经过的时间
        self.periods = [19, 9, 9]  # 红绿灯周期，红灯20s，绿灯和黄灯10s
        self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, id, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)
        self.time_car = time.time()

        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
            if (direction == 'right'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                - vehicles[direction][lane][self.index - 1].image.get_rect().width
                - stoppingGap
            elif (direction == 'left'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                + vehicles[direction][lane][self.index - 1].image.get_rect().width
                + stoppingGap
            elif (direction == 'down'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                - vehicles[direction][lane][self.index - 1].image.get_rect().height
                - stoppingGap
            elif (direction == 'up'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                + vehicles[direction][lane][self.index - 1].image.get_rect().height
                + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif (direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif (direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 0):
                    if (self.x + self.image.get_rect().width < stopLines[self.direction] + 95):
                        if ((self.x + self.image.get_rect().width <= self.stop or signals[
                            1].state == 2 or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.speed = speeds[self.vehicleClass]
                            self.x += self.speed
                        else:
                            self.speed = 0
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif (self.lane == 2):
                    if (self.x + self.image.get_rect().width < mid[self.direction]['x']):
                        if ((self.x + self.image.get_rect().width <= self.stop or signals[
                            1].state != 3 or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
            else:
                if (self.crossed == 0):
                    if ((self.x + self.image.get_rect().width <= self.stop or signals[1].state == 1) and (
                            self.index == 0 or self.x + self.image.get_rect().width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                        self.speed = speeds[self.vehicleClass]
                        self.x += self.speed
                    else:
                        self.speed = 0
                else:
                    if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                        self.x += self.speed
        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 0):
                    if (self.y + self.image.get_rect().height < stopLines[self.direction] + 90):
                        if ((self.y + self.image.get_rect().height <= self.stop or signals[
                            0].state == 2 or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.speed = speeds[self.vehicleClass]
                            self.y += self.speed
                        else:
                            self.speed = 0
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 2.9
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.x + self.image.get_rect().width) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                                self.x += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y + self.image.get_rect().height < mid[self.direction]['y']):
                        if ((self.y + self.image.get_rect().height <= self.stop or signals[
                            0].state != 3 or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y + self.image.get_rect().height <= self.stop or signals[0].state == 1) and (
                            self.index == 0 or self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                        self.speed = speeds[self.vehicleClass]
                        self.y += self.speed
                    else:
                        self.speed = 0
                else:
                    if ((self.crossedIndex == 0) or (self.y + self.image.get_rect().height < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                        self.y += self.speed
        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 0):
                    if (self.x > stopLines[self.direction] - 100):
                        if ((self.x >= self.stop or signals[3].state == 2 or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.speed = speeds[self.vehicleClass]
                            self.x -= self.speed
                        else:
                            self.speed = 0
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.x > mid[self.direction]['x']):
                        if ((self.x >= self.stop or signals[3].state != 3 or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.x >= self.stop or signals[3].state == 1) and (self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().width + movingGap))):
                        self.speed = speeds[self.vehicleClass]
                        self.x -= self.speed
                    else:
                        self.speed = 0
                else:
                    if ((self.crossedIndex == 0) or (self.x > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn == 1):
                if (self.lane == 0):
                    if (self.crossed == 0 or self.y > stopLines[self.direction] - 100):
                        if ((self.y >= self.stop or signals[2].state == 2 or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.speed = speeds[self.vehicleClass]
                            self.y -= self.speed
                        else:
                            self.speed = 0
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y > mid[self.direction]['y']):
                        if ((self.y >= self.stop or signals[2].state != 3 or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y -= self.speed
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x -
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y >= self.stop or signals[2].state == 1) and (
                            self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().height + movingGap))):
                        self.speed = speeds[self.vehicleClass]
                        self.y -= self.speed
                    else:
                        self.speed = 0
                else:
                    if ((self.crossedIndex == 0) or (self.y > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed


def initialize():
    tl1 = TrafficLight(0)
    signals.append(tl1)
    tl2 = TrafficLight(1)
    signals.append(tl2)
    tl3 = TrafficLight(0)
    signals.append(tl3)
    tl4 = TrafficLight(1)
    signals.append(tl4)
    repeat()


def update_values():
    for i in range(4):
        if signals[i].time == 0:
            if signals[i].state == 0:
                signals[i].state = 1  # 红灯变绿灯
                signals[i].time = 9
            elif signals[i].state == 1:
                signals[i].state = 2  # 绿灯变黄灯
                signals[i].time = 9
            elif signals[i].state == 2:
                signals[i].state = 0  # 黄灯变红灯
                signals[i].time = 19
        else:
            signals[i].time -= 1


def repeat():
    while True:
        update_values()
        time.sleep(1)


# Generating vehicles in the simulation 生成车辆
def generateVehicles():
    global id
    id = 0
    while (True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(0, 2)
        # 左转
        if (lane_number == 0):
            will_turn = 1
        # 直行
        elif (lane_number == 1):
            will_turn = 0
        # 右转
        else:
            will_turn = 1
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if (temp < dist[0]):
            direction_number = 0
        elif (temp < dist[1]):
            direction_number = 1
        elif (temp < dist[2]):
            direction_number = 2
        elif (temp < dist[3]):
            direction_number = 3
        Vehicle(id, lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                will_turn)
        id += 1
        time.sleep(1)


start_time = time.time()  # 获取开始时间
if len(sys.argv) > 1:
    end_time = int(sys.argv[1])

class Main(end_time):
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    excel_file_path = os.path.join(desktop_path, 'Dataset.xlsx')

    # 检查文件是否存在，如果存在则删除
    if os.path.exists(excel_file_path):
        os.remove(excel_file_path)

    wb = Workbook()
    ws = wb.active
    ws.append(
        ['编号', '横坐标', '纵坐标', '速度', '时刻', '是否为任务车辆', '任务带宽需求', '任务频率需求',
         '工作负载', '任务大小', '本地时间', '本地能耗', '基站时间', '基站能耗',
         '云卸载时间', '云卸载能耗'])
    # if len(sys.argv) > 1:
    #     end_time = int(sys.argv[1])
    run_time = 0
    count = 0

    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if (allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread1.daemon = True
    thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    # screenWidth = 1551
    # screenHeight = 1558
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/Intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread2.daemon = True
    thread2.start()

    while run_time <= end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.blit(background, (0, 0))  # display background in simulation

        # print(start_time)
        for i in range(0, 4):  # display signal and set timer according to current status: green, yello, or red
            if (signals[i].state == 2):
                signals[i].signalText = signals[i].time
                # 将对应的信号灯图片绘制到游戏窗口上
                screen.blit(yellowSignal, signalCoods[i])
            elif (signals[i].state == 1):
                signals[i].signalText = signals[i].time
                screen.blit(greenSignal, signalCoods[i])
            else:
                signals[i].signalText = signals[i].time
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]
        # display signal timer
        for i in range(0, 4):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # 记录开始时间
        interval = 0.5  # 0.2秒间隔
        data_to_append = []  # 存储车辆数据的列表

        # 创建 UDP 套接字
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 主窗口的 IP 地址和端口号（需要替换为你实际的 IP 地址和端口号）
        host = '127.0.0.1'
        port = 9999

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # sock.sendto(f"{vehicle.id}, {vehicle.x}".encode(), ('localhost', 12345))
            # if vehicle.x < 0 or vehicle.x > screenWidth or vehicle.y < 0 or vehicle.y > screenHeight:
            #     simulation.remove(vehicle)
            vehicle.move()
            if (
                    0 <= vehicle.x <= screenWidth and 0 <= vehicle.y <= screenHeight) and time.time() - vehicle.time_car >= interval:
                # 保留一位小数并进行四舍五入
                rounded_run_time = round(run_time, 1)
                # 检查小数点后一位是否在0到0.5之间
                if 0 <= rounded_run_time % 1 < 0.5:
                    rounded_run_time = int(rounded_run_time) + 0.5
                else:
                    rounded_run_time = int(rounded_run_time) + 1
                # 构造消息字符串
                message = f"车辆编号{vehicle.id}在时间{rounded_run_time}s行驶到位置({vehicle.x:.2f}, {vehicle.y:.2f})"
                sock.sendto(message.encode(), ('localhost', 12345))
                data_to_append.append([
                    vehicle.id, vehicle.x, vehicle.y, vehicle.speed, rounded_run_time,
                    1 if random.random() <= 0.3 else 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                vehicle.time_car = time.time()
            for data in data_to_append:
                ws.append(data)
            data_to_append = []  # 清空数据
        # if vehicle.x < 0 or vehicle.x > screenWidth or vehicle.y < 0 or vehicle.y > screenHeight:
        #      simulation.remove(vehicle)
        udp_socket.close()
        pygame.display.update()
        # 计算时间的流逝
        elapsed_time = time.time() - start_time
        # print(elapsed_time)
        run_time += elapsed_time  # 更新 run_time，将时间的流逝取整并减去
        # 重置开始时间
        start_time = time.time()
        # print(run_time)
    wb.save(excel_file_path)
    quit()


# Main()
