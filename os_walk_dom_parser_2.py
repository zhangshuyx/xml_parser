#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#将gz文件解压为xml文件，并由dom程序解析，最后写入csv文件
#最新修改为读入指定个文件，解析后写入一个文件，总体来看效率提升不明显，改用cStringIO后还是不明显。
#考虑采用其他多线程方式。
#先改成函数调用结构

#导入相关模块
import os,gzip,time,cStringIO
from os.path import join, splitext, abspath
#from xml.dom.minidom import parse

#DOM解析函数，输入gz文件，输出解析后的字符串和处理行数
def dom_parser(gz):
	import gzip,cStringIO
	import xml.dom.minidom
	#from xml.dom.minidom import parseString
	vs_cnt = 0
	file_io = cStringIO.StringIO()
	str = ''
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	doc = xml.dom.minidom.parseString(xm.read())
	bulkPmMrDataFile = doc.documentElement
	#读入子元素
	enbs = bulkPmMrDataFile.getElementsByTagName("eNB")
	measurements = enbs[0].getElementsByTagName("measurement")
	objects = measurements[0].getElementsByTagName("object")
	#写入csv文件
	for object in objects:
		vs = object.getElementsByTagName("v")
		vs_cnt += len(vs)
		for v in vs:
			file_io.write(enbs[0].getAttribute("id")+' '+object.getAttribute("id")+' '+object.getAttribute("MmeUeS1apId")+' '\
			+object.getAttribute("MmeGroupId")+' '+object.getAttribute("MmeCode")+' '+object.getAttribute("TimeStamp")+' '\
			+v.childNodes[0].data+'\n')  #获取文本值
	str = (((file_io.getvalue().replace(' \n','\r\n')).replace(' ',',')).replace('T',' ')).replace('NIL','')
	xm.close()
	file_io.close()
	return (str,vs_cnt)

#定义空列表，用于放入gz路径文件名
gzs = []
vs_cnt = 0
#指定每次处理多少个文件
paser_num = 5
#指定输入输出文件路径
input_path  = '/tmcdata/mro2csv/input31/'
output_path = '/tmcdata/mro2csv/output31/'
os.chdir(input_path)

#读入文件名到列表gzs
gzs = [x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1]=='.gz']
#检查并纠正paser_num设置
if paser_num < 0 or paser_num >= len(gzs):
	paser_num = len(gzs)

print("*"*50)
print("\
程序处理启动。\
\n输入目录为：%s。\
\n输出目录为：%s。\
\n输入目录下.gz文件个数为：%d，本次处理其中的%d个。" % (input_path,output_path,len(gzs),paser_num))
print("*"*50)

#截短gzs
gzs = gzs[0:paser_num]
with open(os.path.join(output_path,'mro_0001.csv'),'w') as t:		#生成csv文件以写入数据
	output = cStringIO.StringIO()
	start_time = time.time()
	gz_cnt = 0
	for gz in gzs:
		cnt = 0
		str = ''
		gz_cnt += 1
		print("文件计数：%d/%d." % (gz_cnt,paser_num))
		str,cnt = dom_parser(gz)
		output.write(str)
		vs_cnt += cnt
	t.write(output.getvalue())	#写入解析后内容
	output.close()
	print("VS行计数：%d，运行时间：%f，每秒处理行数：%d。\n已写入：%s。\n" % (vs_cnt, time.time()-start_time, vs_cnt/(time.time()-start_time), os.path.abspath(t.name)))
	#try:
		#os.remove(gz)
		#print("已删除：%s.\n" % os.path.abspath(gz))
	#except:
		#print("文件删除失败：%s.\n" % os.path.abspath(gz))

print("*"*50)
print("程序处理结束。")
