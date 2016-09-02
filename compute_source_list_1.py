#!/usr/bin/python
#! -*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
import sys
sys.path.append('/home/workspace/ProxyServer/bin')
sys.path.append('/home/fangwang/statistic_scripts/')
import os
from DBHandle import DBHandle
import re

monitor_source = DBHandle("10.10.87.87","root","miaoji@2014!","devdb")


source_mioji_dict=dict()
source_self_mioji_dict=dict()
source_raw=[]
flight_validation_dict=dict()

def init_source_tab():
    #初始化源列表
    res=monitor_source.QueryBySQL("SELECT * FROM source WHERE pay_method != 'NULL'")    
    for line in res:
        if  line['pay_method'].find('mioji') != -1:
            tmp_type=line['type']
            source_mioji_dict.setdefault(tmp_type,[])
            source_mioji_dict[tmp_type].append(line['name'])
        elif  line['pay_method'] == 'self+mioji':
            tmp_type=line['type']
            source_self_mioji_dict.setdefault(tmp_type,[])
            source_self_mioji_dict[tmp_type].append(line['name'])


def init_flight_validation_tab():
    #初始化过滤列表
    res=monitor_source.QueryBySQL("SELECT * FROM flight_validation where status != 0")
    for line in res:
        if line['type']=='oneway':
            key=line['dept_id']+'|'+line['dest_id']
            flight_validation_dict.setdefault(key,[])
            flight_validation_dict[key].append(line['source'])

def add_source(_type,pay_method):
    #取出source所有源
    source_list=[]
    global source_raw
    if  _type == 'flight':
        if pay_method == 'mioji':
            source_raw=source_mioji_dict['flight_one_way']
        elif pay_method == 'self+mioji':
            source_raw=source_self_mioji_dict['flight_one_way']
        for source in source_raw:
            source_list.append(source)
    return source_list

def validation_source(dept,dest,_type,source_list):
    #过滤source表
    if _type == 'flight':
        source_validation=[]
        key=dept+'|'+dest
        if key not in flight_validation_dict.keys():
            source_validation.append('ctripFlight')
            source_validation.append('expediaFligh')
            return source_validation
        tmp_source = flight_validation_dict[key]
        for source in source_raw:
            if source in tmp_source:
                source_validation.append(source)
        if len(source_validation)<=1:
            source_validation.append('ctripFlight')
            source_validation.append('expediaFlight')
        return source_validation
class hello(tornado.web.RequestHandler):
    def get(self):
        print self.request
        try:
            dept = self.get_argument('dept')
        except:
            print 'put in dept error'
        try:
            dest = self.get_argument('dest')
        except:
            print 'put in dest error'
        try:
            pay_method = self.get_argument('pay_method')
        except:
            print 'put in pay_method error'
        try:
            trans_type = self.get_argument('type')
        except:
            print 'put in trans_type error'
        print("dept: %s, dest: %s, trans_type: %s, pay_method: %s" % (dept, dest, trans_type,pay_method))
        source_list = []
        #根据类型计算source_list
        #...
                
        source_list = add_source(trans_type,pay_method)
        source_list = validation_source(dept,dest,trans_type,source_list)
        
        source_list = list(set(source_list))
        if 'mioji' in source_list:
            source_list.remove('mioji')

        self.write(json.dumps(source_list))

if __name__ == '__main__':
    init_source_tab()
    init_flight_validation_tab()
    print 'inited over'
    application = tornado.web.Application([
        (r"/slquery", hello)
            ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(10081)
    http_server.start()
    tornado.ioloop.IOLoop.instance().start()
