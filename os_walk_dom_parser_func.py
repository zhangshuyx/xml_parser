#!/usr/bin/python
# -*- coding: UTF-8 -*-
#将gz文件解压为xml文件，并由dom或sax解析，最后写入csv文件

#导入相关模块
import os,sys,time,io
from os.path import join, splitext, abspath

#指定输入输出文件路径
input_path  = '/home/kkk/python/mro'
output_path = '/home/kkk/python/mro'
os.chdir(input_path)
#指定每次处理多少个文件，为-1时表示处理文件夹下所有文件
paser_num = -1

#设定默认值'ET_iter'，并判断命令行输入参数是否合理，如果参数错误给出提示并退出程序。
func_key = 'ET_iter'
if len(sys.argv) == 1:
	print('\nNO argument input, the default function ET_parser_iter is called.')
elif len(sys.argv) == 2 and sys.argv[1] in ['dom','sax','ET','ET_iter','ET_iter_list','lxml_TT','lxml_iter']:
	func_key = sys.argv[1]
else:
	print("ERROR: You have input the wrong arguments, NOTHING or ONE of 'dom','sax','ET','ET_iter','lxml_TT','lxml_iter' is needed!")
	sys.exit()

#DOM解析函数，输入gz文件，输出解析后的字符串和处理行数
def dom_parser(gz):
	'''Parse the .xml.gz file by dom_parser.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with dom_parser,
	at the end return the string and element v's row count.'''
	import gzip,io
	import xml.dom.minidom
	
	vs_cnt = 0
	str_s = ''
	file_io = io.StringIO()
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
			file_io.write(enbs[0].getAttribute("id")+' '+object.getAttribute("id")+' '+\
			object.getAttribute("MmeUeS1apId")+' '+object.getAttribute("MmeGroupId")+' '+object.getAttribute("MmeCode")+' '+\
			object.getAttribute("TimeStamp")+' '+v.childNodes[0].data+'\n')  #获取文本值
	str_s = (((file_io.getvalue().replace(' \n','\r\n')).replace(' ',',')).replace('T',' ')).replace('NIL','')
	xm.close()
	file_io.close()
	return (str_s,vs_cnt)


def sax_parser(gz):
	'''Parse the .xml.gz file by sax_parser.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with sax_parser,
	at the end return the string and element v's row count.'''
	import os,gzip,io
	from xml.parsers.expat import ParserCreate

	#变量声明
	d_eNB = {}
	d_obj = {}
	s = ''
	global flag 
	flag = False
	file_io = io.StringIO()
	
	#Sax解析类
	class DefaultSaxHandler(object):
		#处理开始标签
		def start_element(self, name, attrs):
			global d_eNB
			global d_obj
			global vs_cnt
			if name == 'eNB':
				d_eNB = attrs
			elif name == 'object':
				d_obj = attrs
			elif name == 'v':
				file_io.write(d_eNB['id']+' '+ d_obj['id']+' '+d_obj['MmeUeS1apId']+' '+d_obj['MmeGroupId']+' '\
					+d_obj['MmeCode']+' '+d_obj['TimeStamp']+' ')
				vs_cnt += 1
			else:
				pass
		#处理中间文本
		def char_data(self, text):
			global d_eNB
			global d_obj
			global flag
			if text[0:1].isnumeric():
				file_io.write(text)
			elif text[0:17] == 'MR.LteScPlrULQci1':
				flag = True
				#print(text,flag)
			else:
				pass
		#处理结束标签
		def end_element(self, name):
			global d_eNB
			global d_obj
			if name == 'v':
				file_io.write('\n')
			else:
				pass
	
	#Sax解析调用
	handler = DefaultSaxHandler()
	parser = ParserCreate()
	parser.StartElementHandler = handler.start_element
	parser.EndElementHandler = handler.end_element
	parser.CharacterDataHandler = handler.char_data
	vs_cnt = 0
	str_s = ''
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	for line in xm.readlines():
		parser.Parse(line) #解析xml文件内容
		if flag:
			break
	str_s = file_io.getvalue().replace(' \n','\r\n').replace(' ',',').replace('T',' ').replace('NIL','')	#写入解析后内容
	xm.close()
	file_io.close()
	return (str_s,vs_cnt)


def ET_parser(gz):
	'''Parse the .xml.gz file by ElementTree_parser.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with ElementTree_parser,
	at the end return the string and element v's row count.'''
	import os,gzip,io
	import xml.etree.cElementTree as ET

	vs_cnt = 0
	str_s = ''
	file_io = io.StringIO()
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	tree = ET.ElementTree(file=xm)
	root = tree.getroot()
	for elem in root[1][0].findall('object'):
			for v in elem.findall('v'):
					file_io.write(root[1].attrib['id']+' '+elem.attrib['TimeStamp']+' '+elem.attrib['MmeCode']+' '\
						+elem.attrib['id']+' '+ elem.attrib['MmeUeS1apId']+' '+ elem.attrib['MmeGroupId']+' '+ v.text+'\n')
			vs_cnt += 1
	str_s = file_io.getvalue().replace(' \n','\r\n').replace(' ',',').replace('T',' ').replace('NIL','')	#写入解析后内容
	xm.close()
	file_io.close()
	return (str_s,vs_cnt)

	
def ET_parser_iter(gz):
	'''Parse the .xml.gz file by ElementTree_parser_iter.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with ElementTree_parser_iter,
	at the end return the string and element v's row count.'''
	import os,gzip,io
	import xml.etree.cElementTree as ET

	vs_cnt = 0
	str_s = ''
	file_io = io.StringIO()
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	d_eNB = {}
	d_obj = {}
	i = 0
	for event,elem in ET.iterparse(xm,events=('start','end')):
		if i >= 2:
			break		
		elif event == 'start':
			if elem.tag == 'eNB':
				d_eNB = elem.attrib
			elif elem.tag == 'object':
				d_obj = elem.attrib
		elif event == 'end' and elem.tag == 'smr':
			i += 1
		elif event == 'end' and elem.tag == 'v':
			file_io.write(d_eNB['id']+' '+d_obj['TimeStamp']+' '+d_obj['MmeCode']+' '+d_obj['id']+' '\
				+ d_obj['MmeUeS1apId']+' '+ d_obj['MmeGroupId']+' '+str(elem.text)+'\n')
			vs_cnt += 1
	elem.clear()
	str_s = file_io.getvalue().replace(' \n','\r\n').replace(' ',',').replace('T',' ').replace('NIL','')	#写入解析后内容
	xm.close()
	file_io.close()
	return (str_s,vs_cnt)


def lxml_parser_TitleTarget(gz):
	'''Parse the .xml.gz file by lxml_parser_TitleTarget.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with lxml_parser_TitleTarget,
	at the end return the string and element v's row count.'''
	from lxml import etree
	class TitleTarget(object):
		def __init__(self):
			self.text = []
			self.is_v = False
			self.eNB = {}
			self.obj = {}
			self.vs_cnt = 0
			self.i = 0
		def start(self, tag, attrib):
			if tag == 'eNB':
				self.eNB = attrib
			elif tag == 'smr':
				self.i += 1
			elif tag == 'object':
				self.obj = attrib
			elif tag == 'v':
				self.is_v = True
		def end(self, tag):
			self.is_v = False
		def data(self, data):
			if self.is_v and self.i < 2:
				self.text.append(self.eNB['id']+' ')
				self.text.append(self.obj['id']+' ')
				self.text.append(self.obj['MmeUeS1apId']+' ')
				self.text.append(self.obj['MmeGroupId']+' ')
				self.text.append(self.obj['MmeCode']+' ')
				self.text.append(self.obj['TimeStamp']+' ')
				self.text.append(data.strip())
				self.text.append('\n')
				self.vs_cnt += 1
		def close(self):
			return(''.join(self.text).rstrip('\n').replace(' ',',').replace('T',' ').replace('NIL',''),self.vs_cnt)
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	parser = etree.XMLParser(target = TitleTarget())
	return etree.parse(gz, parser)


def lxml_parser_iter(gz):
	'''Parse the .xml.gz file by lxml_parser_iter.
	
	This function read a .xml.gz file each time, and ungzip it, then parse it to string with lxml_parser_iter,
	at the end return the string and element v's row count.'''
	import os,gzip,io
	from lxml import etree

	vs_cnt = 0
	str_s = ''
	file_io = io.StringIO()
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))
	d_eNB = {}
	d_obj = {}
	i = 0
	for event,elem in etree.iterparse(xm,events=('start','end')):
		if i >= 2:
			break		
		elif event == 'start':
			if elem.tag == 'eNB':
				d_eNB = elem.attrib
			elif elem.tag == 'object':
				d_obj = elem.attrib
		elif event == 'end' and elem.tag == 'smr':
			i += 1
		elif event == 'end' and elem.tag == 'v':
			file_io.write(d_eNB['id']+' '+d_obj['TimeStamp']+' '+d_obj['MmeCode']+' '+d_obj['id']+' '\
				+ d_obj['MmeUeS1apId']+' '+ d_obj['MmeGroupId']+' '+str(elem.text)+'\n')
			vs_cnt += 1
	elem.clear()
	str_s = file_io.getvalue().replace(' \n','\r\n').replace(' ',',').replace('T',' ').replace('NIL','')	#写入解析后内容
	xm.close()
	file_io.close()
	return (str_s,vs_cnt)


#定义空列表，用于放入gz路径文件名
gzs = []
vs_cnt = 0
#读入文件名到列表gzs
gzs = [x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1]=='.gz']
#检查并纠正paser_num设置
if paser_num < 0 or paser_num >= len(gzs):
	paser_num = len(gzs)

#函数字段，根据命令行读入的字符来调用相应的函数
dic_func = {'dom':dom_parser,'sax':sax_parser,'ET':ET_parser,'ET_iter':ET_parser_iter,
		'lxml_TT':lxml_parser_TitleTarget,'lxml_iter':lxml_parser_iter}
print(dic_func[func_key].__doc__)
#help(dic_func[func_key])

print("*"*50)
print("\
程序处理启动。\
\n输入目录为：%s。\
\n输出目录为：%s。\
\n输入目录下.gz文件个数为：%d，本次处理其中的%d个。" % (input_path,output_path,len(gzs),paser_num))
print("*"*50)

#截短gzs
gzs = gzs[0:paser_num]
output = io.StringIO()
start_time = time.time()
gz_cnt = 0
for gz in gzs:
	cnt = 0
	str_s = ''
	gz_cnt += 1
	print("文件计数：%d/%d." % (gz_cnt,paser_num))
	str_s,cnt = dic_func[func_key](gz)	#通过函数字典表查找函数并调用
	output.write(str_s)
	vs_cnt += cnt
with open(os.path.join(output_path,'mro_0001.csv'),'w') as t:		#生成csv文件以写入数据
	t.write(output.getvalue())	#写入解析后内容
	print("VS行计数：%d，运行时间：%f，每秒处理行数：%d。\n已写入：%s。\n" % \
		(vs_cnt, time.time()-start_time, vs_cnt/(time.time()-start_time), os.path.abspath(t.name)))
output.close()
	#try:
		#os.remove(gz)
		#print("已删除：%s.\n" % os.path.abspath(gz))
	#except:
		#print("文件删除失败：%s.\n" % os.path.abspath(gz))
print("*"*50)
print("程序处理结束。")
