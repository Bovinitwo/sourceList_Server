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

monitor = DBHandle("10.10.87.87","root","miaoji@2014!","devdb")



class Source_list:
    def __init__(self):
        self.init_source_tab()
        self.init_validation_tab()
    def init_source_tab(self):
        '''
        初始化mioji和self+mioji的source列表
        mioji中表包括mioji和self+mioji
        self_mioji中表只包括self+mioji
        '''
        self.source_mioji = dict()
        self.source_self_mioji = dict()
        res = monitor.QueryBySQL("SELECT * FROM source WHERE pay_method != 'NULL'")    
        for line in res:
            if  line['pay_method'].find('mioji') != -1:
                tmp_type = line['type']
                self.source_mioji.setdefault(tmp_type,[])
                self.source_mioji[tmp_type].append(line['name'])
            if  line['pay_method'] == 'self+mioji':
                tmp_type=line['type']
                self.source_self_mioji.setdefault(tmp_type,[])
                self.source_self_mioji[tmp_type].append(line['name'])
    def init_validation_tab(self):
        '''
        初始化validation表:flight,roundflight,rail,bus
        '''
        self.flight_validation = dict()
        self.round_flight_validation = dict()
        self.rail_validation = dict()
        self.bus_validation = dict()
        self.hotel_validation = dict()
        '''
        res_flight = monitor.QueryBySQL("SELECT * FROM flight_validation where status != 0") 
        for line in res_flight:
            if line['type'] == 'oneway':
                flight_key = line['dept_id']+'|'+line['dest_id']
                self.flight_validation.setdefault(flight_key,[])
                self.flight_validation[flight_key].append(line['source'])
            if line['type'] == 'round':
                round_key = line['dept_id']+'|'+line['dest_id']
                self.round_flight_validation.setdefault(round_key,[])
                self.round_flight_validation[round_key].append(line['source'])
        print 'flight inited'    
        res_rail = monitor.QueryBySQL("SELECT * FROM rail_validation where status != 0")
        for line in res_rail:
            if line['type'] == 'rail':
                rail_key = line['dept_id']+'|'+line['dest_id']
                self.rail_validation.setdefault(rail_key,[])
                self.rail_validation[rail_key].append(line['source'])
        print 'rail inited'
        res_bus = monitor.QueryBySQL("SELECT * FROM bus_validation where status != 0")
        for line in res_bus:
            if line['type'] == 'bus':
                bus_key = line['dept_id']+'|'+line['dest_id']
                self.bus_validation.setdefault(bus_key,[])
                self.bus_validation[bus_key].append(line['source'])
        print 'bus inited'
        '''
        res_hotel = monitor.QueryBySQL("SELECT * FROM hotel_unid where status != 0")
        for line in res_hotel:
            hotel_key = line['uid']
            self.hotel_validation.setdefault(hotel_key,[])
            self.hotel_validation[hotel_key].append(line['source'])
        print 'hotel inited'

if __name__ == '__main__':
    _tab = Source_list()    

    














