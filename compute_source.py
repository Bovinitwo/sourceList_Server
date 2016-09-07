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
    '''
    初始化源开关列表，已经实际源的列表
    '''
    def __init__(self):
        self.init_source_tab()
    def init_source_tab(self):
        '''
        初始化mioji和self+mioji的source列表
        mioji中表包括mioji和self+mioji
        self_mioji中表只包括self+mioji
        '''
        self.source_mioji = dict()
        self.source_self_mioji = dict()
        '''
        两个表中的key都为‘hippe,car,hotel,flight_one_way,train,bus,flight_multi,flight_return’
        '''
        res = monitor.QueryBySQL("SELECT * FROM source WHERE pay_method != 'NULL'")    
        for line in res:
            if  line['pay_method'].find('mioji') != -1:
                tmp_type = line['type']
                self.source_mioji.setdefault(tmp_type,[])
                if line['name'] not in self.source_mioji[tmp_type]:
                    self.source_mioji[tmp_type].append(line['name'])
            if  line['pay_method'] == 'self+mioji':
                tmp_type=line['type']
                self.source_self_mioji.setdefault(tmp_type,[])
                self.source_self_mioji[tmp_type].append(line['name'])
                if line['name'] not in self.source_self_mioji[tmp_type]:
                    self.source_self_mioji[tmp_type].append(line['name'])
                
class Handle():
    '''
    存放保存各种方法的
    '''
    def __init__(self,pay_method,_tab):
        if pay_method == 'mioji':
            self.source_list = _tab.source_mioji
        elif pay_method == 'self':
            self.source_list = _tab.source_self_mioji

    
    def get_source_flight(self,dept,dest):
        '''
        飞机源
        '''
        res_source = []
        key=dept+'|'+dest
        i_SQL="SELECT source FROM flight_validation WHERE dept_id= "+'\''+str(dept)+'\''+" and dest_id="+'\''+str(dest)+'\''+" and status != 0 and type='oneway'"
        res = monitor.QueryBySQL(i_SQL)    
        validation=[]
        for _dict in res:
            validation.append(_dict['source'])
        print "validation",validation
        if  len(validation)==0:
            res_source.append('ctripFlight')
            res_source.append('expediaFligh')
            return res_source
        for source in self.source_list['flight_one_way']:
            if source in validation:
                res_source.append(source)
        if len(res_source)<=1:
            res_source.append('ctripFlight')
            res_source.append('expediaFlight')
        res_source = list(set(res_source))
        return res_source

    def get_source_hotel(self,hotel_id):
        '''
        酒店源
        '''
        res_source = []
        hotel_unid_source=[]
        i_SQL="SELECT source FROM hotel_unid WHERE uid = "+'\''+str(hotel_id)+'\''
        res = monitor.QueryBySQL(i_SQL)    
        print 'res',res
        print 'source_list',self.source_list['hotel']
        for source in self.source_list['hotel']:
            for _dict in res:
                if _dict['source'] == source:
                    res_source.append(source)
        res_source = list(set(res_source))
        return res_source

    def get_source_bus(self,dept,dest):
        '''
        大巴源
        '''
        res_source = []
        i_SQL="SELECT source FROM bus_validation WHERE dept_id= "+'\''+str(dept)+'\''+" and dest_id="+'\''+str(dest)+'\''+" and status != 0"
        res = monitor.QueryBySQL(i_SQL)    
        validation=[]
        for _dict in res:
            validation.append(_dict['source'])
        for source in self.source_list['bus']:
            if source in validation:
                res_source.append(source)
        res_source = list(set(res_source))
        return res_source

    def get_source_rail(self,dept,dest):
        '''
        火车源
        '''
        res_source = []
        i_SQL="SELECT source FROM rail_validation WHERE dept_id= "+'\''+str(dept)+'\''+" and dest_id="+'\''+str(dest)+'\''+" and status != 0"
        res = monitor.QueryBySQL(i_SQL)    
        validation=[]
        for _dict in res:
            validation.append(_dict['source'])

        for source in self.source_list['train']:
            if source in validation:
                res_source.append(source)
        res_source = list(set(res_source))
        return res_source
    def get_source_flightround(self,dept,dest):
        '''
        飞机往返源
        '''
        res_source = []
        i_SQL="SELECT source FROM flight_validation WHERE dept_id= "+'\''+str(dept)+'\''+" and dest_id="+'\''+str(dest)+'\''+" and status != 0 and type='round'"
        res = monitor.QueryBySQL(i_SQL)    
        validation=[]
        for _dict in res:
            validation.append(_dict['source'])
        for source in self.source_list['flight_return']:
            if source in validation:
                res_source.append(source)
        res_source = list(set(res_source))
        return res_source
    def get_source_flightmulti(self,dept1='',dept2='',dest1='',dest2='',date1=0,date2=0):
        '''
        返回连程
        '''
        res_source = []
        res_source = self.source_list['flight_multi']
        return res_source

    def get_source_car(self,dept='',dest='',date=0):
        res_source = []
        res_source = self.source_list['car']
        return res_source

    def get_source_hippe(self,dept='',dest='',date=0):
        res_source = []
        res_source = self.source_list['hippe']
        return res_source

class MainLogic(tornado.web.RequestHandler):
    def get(self):
        print self.request
        try:
            dept_id = self.get_argument('dept_id')
        except:
            print 'put in dept_id error'
        try:
            dest_id = self.get_argument('dest_id')
        except:
            print 'put in dest_id error'
        try:
            dept_city = self.get_argument('dept_city')
        except:
            print 'put in dept_id error'
        try:
            dest_city = self.get_argument('dest_city')
        except:
            print 'put in dept_id error'
        try:
            hotel_id = self.get_argument('hotel_unid')
        except:
            print 'put in hotel error'
        try:
            pay_method = self.get_argument('pay_method')
        except:
            print 'put in pay_method error'
        try:
            trans_type = self.get_argument('type')
        except:
            print 'put in trans_type error'

            
        handle = Handle(pay_method,_tab)
        source_list=[]
        if trans_type == 'flight':
            source_list = handle.get_source_flight(dept_id,dest_id)
        elif trans_type == 'flightround':
            source_list = handle.get_source_flightround(dept_id,dest_id)
        elif trans_type == 'rail':
            source_list = handle.get_source_rail(dept_city,dest_city)
        elif trans_type == 'hotel':
            source_list = handle.get_source_hotel(hotel_id)
        elif trans_type == 'bus':
            source_list = handle.get_source_bus(dept_city,dest_city)
        elif trans_type == 'flightmulti':
            source_list = handle.get_source_flightmulti()
        elif trans_type == 'car':
            source_list = handle.get_source_car()
        elif trans_type == 'hippe':
            source_list = handle.get_source_hippe()

        #source_list = list(set(source_list))   
        if 'mioji' in source_list:
            source_list.remove('mioji')
        
        self.write(json.dumps(source_list))


if __name__ == '__main__':
    _tab = Source_list()    
    print 'inited over'
    application = tornado.web.Application([
        (r"/slquery", MainLogic)
            ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(10081)
    http_server.start()
    tornado.ioloop.IOLoop.instance().start()
    














