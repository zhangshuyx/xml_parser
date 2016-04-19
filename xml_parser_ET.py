#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#本脚本完成MRO_XML文件转换为可入库的csv文件,使用ElementTree方法
import os,gzip,time
import xml.etree.cElementTree as ET
from os.path import join, splitext

#tree = ET.ElementTree(file='TD-LTE_MRO_NSN_OMC_234598_20160224060000.xml')
#root = tree.getroot()
#print(root[1].tag,root[1].attrib)

vs_cnt = 0
d_eNB = {}
d_obj = {}
for event,elem in ET.iterparse('TD-LTE_MRO_NSN_OMC_234598_20160224060000.xml',events=('start','end')):
	if event == 'start':
		if elem.tag == 'eNB':
			d_eNB = elem.attrib
		elif elem.tag == 'object':
			d_obj = elem.attrib
		elif elem.tag == 'v':
			print(d_eNB['id']+' '+d_obj['TimeStamp']+' '+d_obj['MmeCode']+' '+d_obj['id']+' '+ d_obj['MmeUeS1apId']+' '+ d_obj['MmeGroupId']+' '+str(elem.text))
			#print(d_eNB,d_obj,elem.text)
			vs_cnt += 1
		elif elem.tag == 'smr' and elem.text.startswith('MR.LteScPlrULQci1'):
			break
		else:
			pass
	#if vs_cnt >= 20:
	#	break
	elem.clear()
print('row count:%d' % vs_cnt)
	#i += 1
	#if i >= 20:
	#	break
