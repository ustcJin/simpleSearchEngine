#encoding:utf-8
import jieba
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8') 

fd = open('stopwords.txt', 'r')
stop_dict = {}
while True:
	line = fd.readline()
	if not line:
		break
	else:
		stop_dict[line.strip('\n')] = True

fin = open('../data/solr.json', 'r')
fout = open('../data/hupu.cut', 'w')
index = 0
while True:
	index += 1
	print index
	line = fin.readline()
	if not line:
		break
	item = json.loads(line.strip('\n'))
	title = item['title']
	print title
	seglist = jieba.cut(title)
	for i in seglist:
		if stop_dict.has_key(str(i)):
			continue
		fout.write(str(i) + ' ')
	fout.write('\n')

