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
        self.course_url = self.mislogin_url + '/module/module/280' 
        self.course_folder_url =  'http://cc.bjtu.edu.cn:81/meol/common/script/'
        self.schedule_url = "https://dean.bjtu.edu.cn/course_selection/courseselecttask/schedule/"


        self.header = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',   
        }
        self.login_data = {
            'loginname': number,
            'password': pwd,
        }      
        self.session = requests.session()
    
    """
    登录mis平台
    """
    def mis_auto_login(self):
        req = self.session.get(self.mislogin_url)

        login_url = req.url
        self.header['Referer'] = req.url
        
        soup = BeautifulSoup(req.content, 'lxml')
        csrfmiddlewaretoken = soup.find( 
            attrs={'name': 'csrfmiddlewaretoken'}).attrs['value']

        self.login_data['csrfmiddlewaretoken'] = csrfmiddlewaretoken
        
        next = str(req.url).replace('%3F', urllib.parse.unquote('%3F'), 10).replace('%3D', urllib.parse.unquote(
            '%3D'), 10).replace('%26', urllib.parse.unquote('%26'), 10).replace('%3A', urllib.parse.unquote('%3A'), 10)
        next = next[next.index("next=") + len('next='):]
        self.login_data['next'] = next

        # 模拟登陆mis
        req = self.session.post(
            login_url, data=self.login_data, headers=self.header)
        

    """
    登录教务处平台
    """
    def jwc_login(self):
        #先登陆mis
        self.mis_auto_login()

        # 进入jwc界面
        resp = self.session.get(self.jwc_url)
        html = resp.content.decode('utf-8','ignore')

        #从中转界面获取url跳转
        soup = BeautifulSoup(html, 'lxml')
        
        self.header['Referer'] = self.jwc_url

        resp = self.session.get(soup.form['action'], headers= self.header)
        html = resp.content.decode('utf-8','ignore')
        if self.check_login_dean(html):
            return True
        return False


    """
    检查教务处是否登录成功
    """
    def check_login_dean(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')

        if soup.find('span').attrs['class'][0] == 'user-info':
            print("成功登陆教务系统")
            return True
        else:
            print("登陆教务系统失败")
            return False
    

    """
    获取成绩，需登录教务处系统
    """
    def jwc_get_score(self):
    

        resp = self.session.get(self.jwc_score_url, headers= self.header)
        html = resp.content.decode('utf-8','ignore')
        print(html)
        soup = BeautifulSoup(html,'lxml')
        p = soup.find_all('tr')
        count1 = 0
        count2 = 0
        ans = ""
        for index in range(len(p)):
            if index == 0:
                continue
            tds = p[index].find_all('td')
            course = tds[2].text.replace(' ','').replace('\n','')[7:]
            score = tds[4].text.replace(' ','').replace('\n','')
            if score != "***":
                count2 += 1
            print("课程：{} \n成绩：{}\n\n".format(course,score))
            ans = ans + "课程：{} \n成绩：{}\n\n".format(course,score)
            count1 += 1

        print("总课程数：{},已出成绩：{}\n".format(course,score))
        return ans
    

    """
    登录课程平台。并拿到课程url,必须先执行
    """
    def course_login(self):
        #先进mis
        self.mis_auto_login()
        
        #进入课程平台的中转界面获取课程平台url和post数据
        resp = self.session.get(self.course_url)
        html = resp.content.decode('utf-8','ignore')
        
        soup = BeautifulSoup(html,'lxml')
        
        url = soup.form['action']
        inputs = soup.find_all('input')
        data = {}

        for each_input in inputs:
            data[each_input['name']] = each_input['value']
        
        self.header['Referer'] = self.course_url

        resp = self.session.post(url,data = data,headers=self.header)
        
        html = resp.content.decode('gbk','ignore')
        
        # 全部课程的url
        course_list_url =  url[0:url.index("meol")+4] +'/lesson/blen.student.lesson.list.jsp' 
        
        resp = self.session.get(course_list_url)  
        html = resp.content.decode('gbk','ignore')
        soup = BeautifulSoup(html,'lxml')
        trs = soup.find_all('tr')
            
        course_list = []
        for tr in trs[1:]:
            course_list.append({'course':tr.td.a.text.strip().replace(' ',''),'href':tr.td.a['href'],'id':tr.td.a['href'][tr.td.a['href'].index('=')+1:]})
        
        self.save(course_list,"course_list")
        
        #单返回课程名
        return [ each['course'] for each in course_list]
       

    """
    获取课程的目录url，并写入json，更新时调用
    """
    def get_folder_urls(self):
        
        course_list = self.load('course_list')

        listview_url_template = 'http://cc.bjtu.edu.cn:81/meol/common/script/listview.jsp?groupid=4&lid={}&folderid=0'
        listview_urls = [(listview_url_template.format(course['id']),course['course'] )for course in course_list]
        #获取folderurl
        folder_urls = []
        for listview_url in listview_urls:
            resp = self.session.get(listview_url[0])
            html = resp.content.decode('gbk','ignore')
            soup = BeautifulSoup(html,'lxml')
            #第一个就是要找的td标签
            folder_urls.append({'url':self.course_folder_url + soup.find('td').a['href'],'course':listview_url[1]})

        self.save(folder_urls,'folder_urls')
        return folder_urls

    """
    获取文件列表,用于更新文件
    """
    def get_file_list(self):

        folder_urls = self.load('folder_urls')    
        files = []

        for folder_url in folder_urls:
            resp = self.session.get(folder_url['url'])
            
            html = resp.content.decode('gbk','ignore')
            soup = BeautifulSoup(html,'lxml')
            trs = soup.find_all(attrs={"table-margin-alternation-td"})
            for tr in trs:
                link = tr.find('td').a
                files.append({'fname':link.text,'href':link['href'],'type':tr.find('td').img['src'][19:-4],'course':folder_url['course']})
        
        self.save(files,'files_list')
        return files

    """
    按照下载url,_file是上面定义的字典
    """
    def download_file(self,_file):
        
        resp = self.session.get(self.course_folder_url + _file['href'])
        if _file['type'] in type_to_suffix.keys():
            with open(_file['fname']+type_to_suffix[_file['type']],'wb') as f:
                f.write(resp.content)
                print("源文件:{}下载成功！".format(_file['fname']))   
        else:
            print("源文件:{}不支持此类型文件下载:{}".format(_file['fname'],_file['type']))


    def save(self,dic,fname):
        js = json.dumps(dic)
        f = open(fname,'w')
        f.write(js)
        f.close

    def load(self,fname):
        f = open(fname,'r')
        js = f.read()
        dic = json.loads(js)
        f.close()
        return dic
    """
    获取课程表
    """

    def get_schedule(self):
        if(self.jwc_login()):
            logging.info("登录教务系统成功")
        else:
            logging.info("登录教务系统失败")
            return 0
        
        resp = self.session.get(self.schedule_url,headers=self.header)
        html  = resp.content.decode('utf-8','ignore')
        soup = BeautifulSoup(html,'lxml')

        table = soup.find('table',class_='table table-bordered')
        trs = table.find_all('tr')
        schedule_dic = {}
      
        for tr in trs[1:]:
            tds = tr.find_all('td')
            
            section = tds[0].text.strip()[0:3]
            
            week = 1
            section_list = []
            for td in tds[1:]:
                if td.div:
                    spans = td.div.find_all('span')
                    lesson_dic = {}
                    lesson_dic['week'] = week
                    lesson_dic['name'] = spans[0].text.strip().split('\n')[1].strip()
                    lesson_dic['location'] = spans[1].text.strip()
        
                    section_list.append(lesson_dic)

                week += 1
            schedule_dic[section] = section_list
        
        self.save(schedule_dic,'16231324_schedule')



if __name__ == '__main__':
    tool = tools("16231324","pwd")
    tool.get_schedule()
