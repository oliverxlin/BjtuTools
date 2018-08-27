# coding=utf-8
#=============================================================
# File name: bjtutools.py
# Created time: 2018年08月27日 星期一 15时50分31秒
# Copyright (C) 2018 Richado
# Mail: 16231324@bjtu.edu.cn
#=============================================================
import requests
import re
import sys
from time import sleep
import urllib
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from django.views.decorators.csrf import csrf_protect
import logging
import json   
#类型转后缀
from config import type_to_suffix

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

class tools(object):
    def __init__(self,number,pwd):
        # set of url
        self.mislogin_url = 'https://mis.bjtu.edu.cn'
        self.mis_url = 'https://mis.bjtu.edu.cn/home/'
        self.jwc_url = self.mislogin_url + '/module/module/322/'
        self.submit_url = 'https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects_action/?action=submit'
        self.kua_url = 'https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects_action/?action=load&iframe=cross&page=29'
        self.zyxx_url = 'https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects/'
        self.rx_url = 'https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects_action/?'
        self.jwc_score_url = 'https://dean.bjtu.edu.cn/score/scores/stu/view/'
        self.lesson_url = self.mislogin_url + '/module/module/280' 
        self.lesson_folder_url =  'http://cc.bjtu.edu.cn:81/meol/common/script/'
        self.header = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',   
        }
        self.login_data = {
            'loginname': number,
            'password': pwd,
        }      
        self.session = requests.session()
    

    def mis_auto_login(self):
        req = self.session.get(self.mislogin_url)

        login_url = req.url
        self.header['Referer'] = req.url
        
        soup = BeautifulSoup(req.content, 'lxml')
        csrfmiddlewaretoken = soup.find( 
            attrs={'name': 'csrfmiddlewaretoken'}).attrs['value']

