# -*- coding: utf-8 -*-  
import md5
import os
import json
import sys
import codecs


reload(sys)
sys.setdefaultencoding('utf-8')
fd = open('hupu.json.fresh', 'r')
fout = codecs.open('../data/solr.json.fresh', 'w', 'utf-8')
index = 1
parse_err = 0
download_err = 0
sign = False
fout.write("[\n")
while 1:
#for line in fd.readlines():
	line = fd.readline()
	if not line:
		break
	print index
	index = index + 1
	line = line.strip('\n')
	try:
		dj = json.loads(line)
	except Exception as err:
		print err
		parse_err += 1
		continue
	if dj['author_level'] == -1:
		download_err += 1
		continue
	r_users = []
	r_summs = []
	r_lights = []
	for item in dj['remark']:
		r_users.append(item['user'])
		r_lights.append(item['light'])
		r_summs.append(item['summary'])
	dj['r_users'] = r_users
	dj['r_summs'] = r_summs
	dj['r_lights'] = r_lights
	m = md5.new()
	m.update(dj['url'])
	dj['id'] = m.hexdigest()
	del dj['remark']
	wstr = json.dumps(dj, ensure_ascii=False)
	if sign == True:
		fout.write(",\n%s" % wstr)
	else:
		fout.write("%s" % wstr)
		sign = True

fout.write("\n]")
print "parse_err:%d download_err:%d\n" % (parse_err, download_err)
