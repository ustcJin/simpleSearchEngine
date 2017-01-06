#coding:utf-8
import bs4
from bs4 import BeautifulSoup
import urllib2
import urllib
import re
import time
import datetime
import sys
import os
import json

class HupuParser():
	def __init__(self, save_file):
		self.save_fd = open(save_file, 'w')

		self.title_re = re.compile('(\d+)回复/(\d+)亮 (\d+)浏览')
		self.level_re = re.compile('(\d+)级')
		self.seed_re = re.compile('a id=\"\" href=\"/(\d{7,8}\.html)\"')

		self.reset()
		self.solr_url = 'http://112.74.45.38:8983/solr/hupu/update?_=1481262376514&boost=1.0&commitWithin=1000&overwrite=true&wt=json'

		#init label list vector
		self.plist = []
		self.plist.append('class' + ' ' + 'hp-wrap')
		self.plist.append('class' + ' ' + 'rel')
		self.plist.append('*' + ' ' + '*')
		self.plist.append('*' + ' ' + '*')
		self.plist.append('class' + ' ' + 'hidden')

		self.phead = self.plist[:]
		self.phead.append('class' + ' ' + 'bbs_head')
		self.phead.append('class' + ' ' + 'bbs-hd-h1')

		self.pbody = self.plist[:]
		self.pbody.append('class' + ' ' + 'floor')
		self.pbody.append('class' + ' ' + 'floor_box')

		self.pauthor = self.pbody[:]
		self.pauthor.append('class' + ' ' + 'author')
		self.pauthor.append('class' + ' ' + 'left')

		self.pcontent = self.pbody[:]
		self.pcontent.append('class' + ' ' + 'case')
		self.pcontent.append('*' + ' ' + '*')
		self.pcontent.append('*' + ' ' + '*')

		self.preply = self.plist[:]
		self.preply.append('class' + ' ' + 'w_reply clearfix')
		self.preply.append('name' + ' ' + 'div')

		self.flist = []
		self.flist.append('class' + ' ' + 'floor_box')
		self.flist.append('class' + ' ' + 'author')
		self.flist.append('class' + ' ' + 'left')

		self.slist = []
		self.slist.append('class' + ' ' + 'floor_box')	
		self.slist.append('class' + ' ' + 'case')	
		self.slist.append('*'+ ' ' + '*')	
		self.slist.append('*'+ ' ' + '*')	

		self.rrlist = []
		self.rrlist.append('*' + ' ' + '*')
		self.rrlist.append('class' + ' ' + 'stime')
	def reset(self):
		self.url = ""
		self.author = ""
		self.author_level = -1
		self.title = ""
		self.content = ""
		self.pdate = 0 
		self.pvnum = 0 
		self.reply = 0 
		self.remark = []
	def flush(self):
		self.save_fd.flush()

	def getTitle(self, div):
		if type(div) != bs4.element.Tag:
			return False
		for child in div:
			if child.name == 'h1':
				self.title = child.attrs['data-title'].encode("utf-8")
			if child.name == 'span':
				text = child.string.encode("utf8")
				matches = self.title_re.match(text)
				if matches == None:
					return False
				self.reply = int(matches.group(1))
				self.pvnum = int(matches.group(3))
		return True
	
	def getAuthor(self, div):
		if type(div) != bs4.element.Tag:
			return False
		for child in div:
			if child.name == 'a':
				self.author = child.string.encode("utf-8")
			if getAttr(child, 'class') == 'f666':
				for cc in child:
					if cc.name == 'a':
						text = cc.string.encode("utf-8")
						matches = self.level_re.match(text)
						if matches == None:
							continue
						self.author_level = int(matches.group(1))
			elif getAttr(child, 'class') == 'stime':
						d = datetime.datetime.strptime(child.string,"%Y-%m-%d %H:%M")
						self.pdate = (int)(time.mktime(d.timetuple()))

	def getContent(self, div):
		if type(div) != bs4.element.Tag:
			return False
		for child in div:
			if getAttr(child, 'class') == 'subhead' or child.name == 'small':
				continue
			for cc in child:
				if (type(cc) == bs4.element.NavigableString or type(cc) == unicode) and cc != None:
					self.content += cc
				elif type(cc) == bs4.element.Tag and cc.name == 'a' and cc.string != None:
					self.content += cc.string
			if child.name == 'div':
				self.content += '\n'
			else:
				self.content += ' '
		self.content = self.content.encode("utf8").strip(' \r\n')

	def getContentFromDiv(self, div):
		if type(div) != bs4.element.Tag or div.name == 'small' or div.name == 'blockquote':
			return ""
		summ = ""
		for child in div:
			if type(child) == bs4.element.NavigableString:
				summ += child.encode("utf8").strip(' \r\n')
			elif child.name == 'b' and child.string != None:
				summ += child.string.encode("utf-8").strip(' \r\n')
			elif type(child) == bs4.element.Tag and child.name != 'blockquote' and child.name != 'small':
				summ += self.getContentFromDiv(child) 
		return summ	


	def getReply(self, div):
		rank = 1
		if type(div) != bs4.element.Tag:
			return False

		for child in div:
			user = ""
			light = 0
			summary = ""

			if type(child) != bs4.element.Tag:
				continue
			first = getDeepDiv(child, self.flist)
			if first == None:
				continue
			for cc in first:
				if cc.name == 'a':
					user = cc.string.encode("utf8").strip(' \r\n')
				elif getAttr(cc, 'class') != 'stime' and type(cc) == bs4.element.Tag:
					light_div = getDeepDiv(cc, self.rrlist)
					if light_div == None:
						continue
					light = int(light_div.string)

			second = getDeepDiv(child, self.slist)
			if second == None:
				continue
			for cc in second:
				if type(cc) == bs4.element.NavigableString:
					summary += cc.encode("utf8").strip(' \r\n')
				elif type(cc) == bs4.element.Tag:
					summary += self.getContentFromDiv(cc)
				if type(cc) == bs4.element.Tag and cc.name == 'div':
					summary += '\n'
				else:
					summary += ' '
			summary = summary.strip(' \r\n')

			item = {}
			item['user'] = user
			item['rank'] = rank
			item['light'] = light
			item['summary'] = summary
			self.remark.append(item)
			rank = rank + 1

	def handleOneHupuUrl(self, url):
		#print url
		html_str = getHtml(url)
		#print html_str
		hupu = BeautifulSoup(html_str)	
		self.url = url

		title_div = getDeepDiv(hupu.body, self.phead)
		author_div = getDeepDiv(hupu.body, self.pauthor)
		content_div = getDeepDiv(hupu.body, self.pcontent)
		reply_div = getDeepDiv(hupu.body, self.preply)

		if title_div == None or author_div == None or content_div == None or reply_div == None:
			return False

		self.getReply(reply_div)
		self.getTitle(title_div)
		self.getAuthor(author_div)
		self.getContent(content_div)

		return True

	def saveOneRecord(self):
		json_item = {}
		json_item["title"] = self.title
		json_item["author"] = self.author
		json_item["author_level"] = self.author_level
		json_item["content"] = self.content
		json_item["pvnum"] = self.pvnum
		json_item["pdate"] = self.pdate
		json_item["reply"] = self.reply
		json_item["remark"] = self.remark
		json_item["url"] = self.url
		#print json_item
		self.save_fd.write("%s\n" % json.dumps(json_item, ensure_ascii=False))
		
def getHtml(url):
	time.sleep(0.1)
	try:
		page = urllib2.urlopen(url, data=None, timeout=3)
		html = page.read()
	except Exception as err:
		print(err)
	return html

def getAttr(div, attr):
	if type(div) != bs4.element.Tag:
		return None
	if div.attrs.has_key(attr) == False:
		return None
	if type(div.attrs[attr]) == list:
		return div.attrs[attr][0]
	elif type(div.attrs[attr]) == str:
		return div.attrs[attr]
	
	return None

def getDiv(div, attr, target):
	#print "attr:%s, target:%s" % (attr, target)
	if type(div) != bs4.element.Tag:
		return None
	for child in div:
		if type(child) != bs4.element.Tag:
			continue
		#for att in child.attrs:
		#	print getAttr(child, att)
		if attr == '*':
			return child
		if attr == 'name' and child.name == target:
			return child
		if child.attrs.has_key(attr) == False:
			continue
		if getAttr(child, attr) != target:
			continue;
		return child
	return None	

def getDeepDiv(div, plist):
	for item in plist:
		items = item.split()
		if len(items) < 2:
			return None
		attr = items[0]
		target = items[1]
		div = getDiv(div, attr, target)
		if div == None:
			print "Wrong attr:%s target:%s" % (attr, target)
			return None
		#else:
			#print "get %s %s succss" % (attr, target)
	return div
						
if __name__ == "__main__":

	#test_str = getHtml("http://bbs.hupu.com/17858233.html")
	#print "title:%s reply:%d pv:%d author:%s level:%d time:%d" % (hpp.title, hpp.reply, hpp.pvnum, hpp.author, hpp.author_level, hpp.pdate)
	#print "content:%s" % hpp.content

	#for item in hpp.remark:
	#	#fd.write("rank:%d remark:%s user:%s light:%d" % (item['rank'], item['summary'], item['user'], item['light']))
	#	print "rank:%d ruser:%s light:%d remark:%s" % (item['rank'], item['user'], item['light'], item['summary'])
	#re_extract = re.compile('id=\"\" href=\"(/\d{8}.html)\"')
	hupu = HupuParser('hupu.json.fresh')
	done = 1

	now_fresh = getHtml("http://bbs.hupu.com/vote");
	all_urls = hupu.seed_re.findall(now_fresh)

	for line in all_urls:
		url = "http://bbs.hupu.com/" + line.strip('\n')
		print url
		try:
			hupu.handleOneHupuUrl(url)
			hupu.saveOneRecord()
		except Exception as err:
			print(err)
		hupu.reset()
		done = done + 1
		if done % 100 == 0:
			hupu.flush()
