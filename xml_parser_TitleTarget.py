#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#本脚本完成MRO_XML文件转换为可入库的csv文件
import os,gzip,time,cStringIO
from lxml import etree
from os.path import join, splitext

class TitleTarget(object):
	def __init__(self):
		self.text = []
		self.is_v = False
		self.eNB = {}
		self.obj = {}
	def start(self, tag, attrib):
		if tag == 'eNB':
			self.eNB = attrib
		elif tag == 'object':
			self.obj = attrib
		elif tag == 'v':
			self.is_v = True
	def end(self, tag):
		self.is_v = False
	def data(self, data):
		if self.is_v:
			self.text.append(self.eNB['id']+' ')
			self.text.append(self.obj['id']+' ')
			self.text.append(self.obj['MmeUeS1apId']+' ')
			self.text.append(self.obj['MmeGroupId']+' ')
			self.text.append(self.obj['MmeCode']+' ')
			self.text.append(self.obj['TimeStamp']+' ')
			self.text.append(data.strip())
			self.text.append('\n')
	def close(self):
		return self.text

parser = etree.XMLParser(target = TitleTarget())
# This and most other samples read in the Google copyright data
infile = 'test.xml'
results = etree.parse(infile, parser)	
# When iterated over, 'results' will contain the output from 
# target parser's close() method
#with open('test.txt','wb') as f:
#	f.write(','.join(results))
print(''.join(results).rstrip('\n').replace(' ',',').replace('T',' ').replace('NIL',''))
#print(results)
