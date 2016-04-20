#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#本脚本完成MRO_XML文件转换为可入库的csv文件
import os,gzip,time
from lxml import etree
from os.path import join, splitext

lst = []
i = 0	#rowcount
start_time = time.time()
root = etree.parse('TD-LTE_MRO_NSN_OMC_234598_20160224060000.xml.gz')
objs = root.xpath('/bulkPmMrDataFile/eNB/measurement[1]/object')
for obj in objs:
	for v in obj.xpath('./v/node()'):
		i += 1
		if i%10000 == 0:
			print('------>%d' % i)
		lst.extend(root.xpath('/bulkPmMrDataFile/eNB/@id'))
		lst.extend(obj.xpath('@*'))
		lst.append(v+'\n')
with open('TD-LTE_MRO_NSN_OMC_234598_20160224060000.csv','w') as t:		#生成csv文件以写入数据
	t.writelines(' '.join(lst).replace(' \n ','\r\n').replace(' ',',').replace('T',' ').replace('NIL',''))	#写入解析后内容
print('文件行计数：%d，处理用时：%f。' % (i,time.time()-start_time))
