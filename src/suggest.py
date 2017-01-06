#coding=utf-8

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urllib
import io
import shutil
import struct 
import sys
import jieba

class MyRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.process(2)
	def do_POST(self):
		self.process(1)
	def getRelate(self, query):
		global words, size, vocab, vocab_list, M, stop_dict
		querys = []
		seglist = jieba.cut(query.encode('utf-8'))
		for i in seglist:
			if stop_dict.has_key(str(i)):
				continue
			querys.append(str(i))
		cn = len(querys)
		print 'cn:%d' % cn 
		N = 10	

		words_idx = [-1] * cn
		bestd = [-1] * N
		bestw = [''] * N
		vector = [0] * size
		real_word_cnt = 0
		for i in range(cn):
			if stop_dict.has_key(querys[i]):
				continue
			if vocab.has_key(querys[i]):
				words_idx[i] = vocab[querys[i]]
			else:
				continue
			real_word_cnt += 1
			print "Word: %s  Position in vocabulary: %d" % (querys[i], words_idx[i])
			for j in range(size):
				vector[j] += M[words_idx[i]][j]

		if real_word_cnt == 0:
			return ''
		sqrt_sum = sum(j * j for j in M[i])
		sqrt_sum = sqrt_sum ** 0.5
		for j in range(size):
			vector[i] /= sqrt_sum
		
		for i in range(words):
			if i in words_idx:
				continue
			dist = sum(vector[j] * M[i][j] for j in range(size))
			for j in range(N):
				if dist > bestd[j]:
					bestd[j+1:N] = bestd[j:N-1]
					bestw[j+1:N] = bestw[j:N-1]
					bestd[j] = dist
					bestw[j] = vocab_list[i]
					break
		return ' '.join(bestw)
	def process(self,type):
		content =""
		#分析参数
		if '?' in self.path:
			query = urllib.splitquery(self.path)
			action = query[0]

			if query[1]:#接收get参数
				queryParams = {}
				for qp in query[1].split('&'):
					kv = qp.split('=')
					queryParams[kv[0]] = urllib.unquote(kv[1]).decode("utf-8", 'ignore')
				if queryParams.has_key('query'):
					print queryParams['query']
					#content = queryParams['query']
					content = self.getRelate(queryParams['query'])

			print content
			#指定返回编码
			enc="UTF-8"
			content = content.encode(enc)
			f = io.BytesIO()
			f.write(content)
			f.seek(0)
			self.send_response(200)
			self.send_header("Content-type", "text/html; charset=%s" % enc)
			self.send_header("Content-Length", str(len(content)))
			self.end_headers()
			shutil.copyfileobj(f,self.wfile)
	
def init():
	fd = open('vectors.bin', 'rb')
	items = fd.readline().strip('\n').split(' ')
	print items
	global words, size, vocab, vocab_list, M, stop_dict
	words = int(items[0])
	size = int(items[1])
	vocab = {}
	vocab_list = []
	M = [[] for i in range(size)] * words
	
	for i in range(words):
		ch = ''
		word = ''
		while ch != ' ':
			word += ch
			ch = fd.read(1)
		vocab[word] = i
		vocab_list.append(word)
		s = struct.unpack('%df' % size, fd.read(size * 4))
		M[i] = list(s)
		fd.read(1)
		sqrt_sum = sum(j * j for j in M[i])
		sqrt_sum = sqrt_sum ** 0.5
		for j in range(size):
			M[i][j] /= sqrt_sum
	fd.close	
	fd = open('stopwords.txt', 'r')
	stop_dict = {}
	while True:
		line = fd.readline()
		if not line:
			break
		else:
			stop_dict[line.strip('\n')] = True
	
reload(sys)
sys.setdefaultencoding('utf-8')
init()
server = HTTPServer(('', 8000), MyRequestHandler)
print 'started httpserver...'
server.serve_forever()

