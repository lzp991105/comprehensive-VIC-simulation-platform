# import需求模块

# 用户自定义函数区

# 系统成本
SC = 0
# 任务丢失
task_loss = 0

# 车辆间卸载任务函数,vfrequency为传入的车辆频率
def vehicle_to_vehicle(task_loss,SC,vfrequency):

    return task_loss,SC

# 基站卸载任务函数,bx为基站横坐标,by为基站纵坐标,bcoverage为基站覆盖范围,bbandwidth为传入的基站带宽,bfrequency为传入的基站计算频率
def vehicle_to_base(task_loss,SC,bx,by,bcoverage,bbandwidth,bfrequency):

    return task_loss,SC
# 云卸载任务函数,cx为云横坐标,cy为云纵坐标,ccoverage为云覆盖范围,cbandwidth为传入的云带宽,cfrequency为传入的云计算频率
def vehicle_to_cloud(task_loss,SC,cx,cy,ccoverage,cbandwidth,cfrequency):

    return task_loss,SC
# 基站/云卸载任务函数
def vehicle_to_base_cloud(task_loss,SC,vfrequency,bx,by,bcoverage,bbandwidth,bfrequency,cx,cy,ccoverage,cbandwidth,cfrequency):

    return task_loss,SC
