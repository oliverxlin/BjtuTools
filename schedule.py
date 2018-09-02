# coding=utf-8
#=============================================================
# File name: schedule.py
# Created time: 2018年09月01日 星期六 23时59分02秒
# Copyright (C) 2018 Richado
# Mail: 16231324@bjtu.edu.cn
#=============================================================
import time
from bjtutools import tools
from config import time as time_dic


#user info
userid = 'id'
pwd = 'pwd'

tool = tools(userid,pwd)
tool.get_schedule()
schedule = tool.load(userid+'_schedule')



key = '第{}节'

"""
获取周x的课程
"""
def get_lesson_by_week(x):
    lesson_dic = {}
    for num in range(7):
        lesson =  schedule[key.format(num+1)]
        for each in lesson:
            if each['week'] == x:
                 each['time']='{}-{}'.format(time_dic[str(num+1)]['start'],time_dic[str(num+1)]['end'])
                 lesson_dic[str(num+1)] = each
    return lesson_dic


"""
获取现在最近的几节课,只有没上过的课
"""
def get_lesson_recent():
    now = time_now()
    num = 0#描述节次
    
    # now = ['2018','09','03','10','00','2']

    for key in range(1,8):
        key = str(key)
        start = time_dic[key]['start'].replace(':','')
        if(int(now[3]+now[4]) < int(start)):
            # print(int(now[3]+now[4]) , int(start)) 
            num = int(key)#下一课的节次
            break
    recent_list = [] 
    lesson_dic =  get_lesson_by_week(int(now[5]))
    
    for key in range(num,8):
        if str(key) in lesson_dic.keys():
            recent_list.append(lesson_dic[str(key)])

    # print(recent_list)
    return recent_list

"""
获取年月日时分周,返回list
"""
def time_now():
    return  time.strftime('%Y-%m-%d-%H-%M-%w',time.localtime()).split('-')

