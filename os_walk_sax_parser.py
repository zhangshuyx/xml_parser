#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#导入相关模块
import os
import gzip
import time
import xml.dom.minidom
from xml.parsers.expat import ParserCreate
from os.path import join, splitext, abspath, basename
from xml.dom.minidom import parse

#定义空列表，用于放入gz路径文件名
gzs = []
gz_cnt = 0
#指定每次处理多少个文件
paser_num = 1
#指定所处理的.gz文件所在路径
os.chdir('/home/mro2csv/input31/')
#变量声明
d_eNB = {}
d_obj = {}
str = ''
flag = True

#Sax解析类
class DefaultSaxHandler(object):
	#处理开始标签
	def start_element(self, name, attrs):
		global d_eNB
		global d_obj
		global str
		if name == 'eNB':
			d_eNB = attrs
		elif name == 'object':
			d_obj = attrs
		elif name == 'v':
			str = str + d_eNB['id'] + ' ' +  d_obj['id'] + ' '  + d_obj['MmeUeS1apId'] + ' '  + d_obj['MmeGroupId'] + ' '  + d_obj['MmeCode'] + ' '  + d_obj['TimeStamp']
		else:
			pass
	#处理中间文本
	def char_data(self, text):
		global d_eNB
		global d_obj
		global str
		global flag
		if text[0:1].isnumeric():
			str = str + text
		elif text.startswith('MR.LteScPlrULQci1'):
			flag = False
		else:
			pass
	#处理结束标签
	def end_element(self, name):
		global d_eNB
		global d_obj
		global str
		pass
		if name == 'v':
			str = str.strip() + '\r\n'
		else:
			pass
#Sax解析调用
handler = DefaultSaxHandler()
parser = ParserCreate()
parser.StartElementHandler = handler.start_element
parser.EndElementHandler = handler.end_element
parser.CharacterDataHandler = handler.char_data

#读入文件名到列表gzs
gzs = [x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1]=='.gz']
if paser_num == -1:
	paser_num = len(gzs)

print("*"*50)
print("\
程序处理启动。\
\n当前目录为：%s。\
\n输出目录为：%s。\
\n当前目录下.gz文件个数为：%d，本次处理其中的%d个。" % (os.getcwd(),os.getcwd().replace('input','output'),len(gzs),paser_num))
print("*"*50)

start_time = time.time()
#将gz文件解压为xml文件，并由dom程序解析，最后写入csv文件
for gz in gzs[0:paser_num]:
	gz_cnt = gz_cnt + 1	
	xm = gzip.open(gz,'rb')
	str = ''
	print("文件计数：%d/%d.\n已读入：%s.\n解析中：" % (gz_cnt,paser_num,os.path.abspath(gz)))
	with open(os.path.abspath(gz).replace('input','output').replace('.xml.gz','.csv'),'w') as t:
		for line in xm.read():
			if flag:
				parser.Parse(line) #解析xml文件内容
			else:
				break
		t.writelines(str)
		#t.write(' '.join(s).replace(' ',',').replace('T',' ').replace('NIL',''))
		print("运行时间：%f。\n已写入：%s。" % (time.time()-start_time, os.path.abspath(t.name)))
	xm.close()
	#try:
		#os.remove(gz)
		#print("已删除：%s.\n" % os.path.abspath(gz))
	#except:
		#print("文件删除失败：%s.\n" % os.path.abspath(gz))

print("*"*50)
print("程序处理结束。")
