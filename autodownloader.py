# coding=utf-8
#=============================================================
# File name: autodownloader.py
# Created time: 2018年08月27日 星期一 21时36分49秒
# Copyright (C) 2018 Richado
# Mail: 16231324@bjtu.edu.cn
#=============================================================

import bjtutools
import os,time,threading,sys

def create_folder(course_list):
    for each_course in course_list:
        if not os.path.exists(each_course + "课件"):
            os.mkdir(each_course + "课件")


#init tools,返回了课程名
tools = bjtutools.tools('id','pwd')

course_list = tools.course_login()

create_folder(course_list)
