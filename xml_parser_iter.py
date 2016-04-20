#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#本脚本完成MRO_XML文件转换为可入库的csv文件
import os,gzip,time,cStringIO
from lxml import etree
from os.path import join, splitext

d_eNB = {}
d_obj = {}
file_io = cStringIO.StringIO()
smr_cnt = 0
vs_cnt = 0
start_time = time.time()
xm = gzip.open('TD-LTE_MRO_NSN_OMC_234598_20160224060000.xml.gz','rb')
for event,elem in etree.iterparse(xm,events=("start","end")):
	if smr_cnt >= 2:
		break
	elif event == 'start' and elem.tag == 'eNB':
		d_eNB = elem.attrib
	elif event == 'start' and elem.tag == 'object':
		d_obj = elem.attrib
	elif event == 'end' and elem.tag == 'smr':
		smr_cnt += 1
	elif event == 'end' and elem.tag == 'v':
		file_io.write(d_eNB['id']+' '+d_obj.get('TimeStamp','0')+' '+d_obj.get('MmeCode','0')+' '+d_obj.get('id','0')+' '+ d_obj.get('MmeUeS1apId','0')+' '+ d_obj.get('MmeGroupId','0')+' '+elem.text+'\n')
		vs_cnt += 1
	#elem.clear()
with open('TD-LTE_MRO_NSN_OMC_234598_20160224060000.csv','w') as t:		#生成csv文件以写入数据
	t.writelines(file_io.getvalue().replace(' \n','\r\n').replace(' ',',').replace('T',' ').replace('NIL',''))	#写入解析后内容
print('文件行计数：%d，处理用时：%f。' % (vs_cnt,time.time()-start_time))
