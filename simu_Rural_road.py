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


speeds = {'car': 0.08, 'truck': 0.05}  # average speeds of vehicles

# Coordinates of vehicles' start车辆启动坐标
x = {'right': [0], 'left': [847]}
y = {'right': [75], 'left': [20]}

vehicles = {'right': {0: [], 1: [], 2: [], 3: [],'crossed': 0}, 'left': {0: [], 1: [], 2: [], 3: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'truck'}
directionNumbers = {0: 'right', 1: 'left'}


# Gap between vehicles 车辆之间的间隙
stoppingGap = 25  # stopping gap 停止间隙
movingGap = 25  # moving gap 移动间隙

# set allowed vehicle types here 在此处设置允许的车辆类型
allowedVehicleTypes = {'car': True, 'truck': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {0: []}, 'left': {0: []}}
vehiclesNotTurned = {'right': {0: []}, 'left': {0: []}}

pygame.init()
simulation = pygame.sprite.Group()




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
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)
        self.time_car = time.time()

        if (len(vehicles[direction][lane]) > 1):
            if (direction == 'right'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                - vehicles[direction][lane][self.index - 1].image.get_rect().width
                - stoppingGap
            elif (direction == 'left'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                + vehicles[direction][lane][self.index - 1].image.get_rect().width
                + stoppingGap

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp

        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.direction == 'right'):
            if (self.crossed == 0):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                vehiclesNotTurned[self.direction][self.lane].append(self)
                self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                    vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                self.x += self.speed
        if (self.direction == 'left'):
            if (self.crossed == 0):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                vehiclesNotTurned[self.direction][self.lane].append(self)
                self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if ((self.crossedIndex == 0) or (self.x > (
                    vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                    vehiclesNotTurned[self.direction][self.lane][
                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                self.x -= self.speed



# Generating vehicles in the simulation 生成车辆
def generateVehicles():
    global id
    id = 0
    while (True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = 0
        will_turn = 0
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [50, 100]
        if (temp < dist[0]):
            direction_number = 0
        elif (temp < dist[1]):
            direction_number = 1

        Vehicle(id, lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                will_turn)
        id += 1
        time.sleep(0.5)


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


    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 847
    screenHeight = 108
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/Rural_road.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread2.daemon = True
    thread2.start()

    while run_time <= end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.blit(background, (0, 0))  # display background in simulation

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
