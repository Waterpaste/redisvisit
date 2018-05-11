#!/usr/bin/env python
#coding:utf-8
#Author:luoshu

import time
import redis
import sys
import getopt 
import threading
from queue import Queue

import warnings
warnings.filterwarnings("ignore")
class redisvis:
	def __init__(self):
		self.suc_count = 0
		self.lock = threading.Lock()
		self.queue = Queue()	

	def getip(self,host,port):
		helps = 'Input format error, correct format:\n' \
             'python redis-visit.py -h 127.0.0.1 -p 6379\n' \
             'python redis-visit.py -h test.txt(127.0.0.1/127.0.0.1:6379)'\
             ''
		getiplist=[]
		if '.txt' in host:
			fp = open(host,'r')
			#print(fp.read())
			for ip in fp:
				if ip!='\n' and ip !='' and ip !='\r':
					getiplist.append(ip.strip()+':'+str(port))
			fp.close()
		elif '.' in host:
			ips = host.split('.')
			ipslen = len(ips)
			if ipslen == 4:
				getiplist.append(host.strip()+':'+str(port))
			else:
				print(helps)
				exit()
		else:
			print(helps)
			exit()

		return getiplist

	def scanque(self,ip):
		for i in ip:
			self.queue.put(i)

	def run(self,threadnum):
		threads = [threading.Thread(target=self.scan) for i in range(int(threadnum))]
		list(map(lambda x:x.start(),threads))
		print('请等待...')
		list(map(lambda x:x.join(),threads))
		print('%s个地址存在匿名访问,请查看当前目录下%s文件 ' % (self.suc_count,self.filename))

	def scan(self):
		while True:
			self.lock.acquire()			
			if self.queue.empty():
				self.lock.release()
				break
			ips = self.queue.get().split(':')
			self.lock.release()
			#print(ips)
			r = redis.Redis(host=ips[0], port=ips[1])
			try:
				r.ping()
				self.lock.acquire()
				self.suc_count =self.suc_count+1
				self.lock. release()
				fp = open(self.filename,'a+')
				fp.write(ips[0]+':'+ips[1]+'\n')
				fp.close()
			except:
				pass		

if __name__ == '__main__':
	host = ""
	port = 6379
	threadnum = 500
	filename = "success.txt"
	options,args = getopt.getopt(sys.argv[1:],'h:p:f:t:')
	for i in options:
		if i[0] == '-h':
			host = i[1]
		elif i[0] == '-p':
			port = i[1]
		elif i[0] == '-f':
			filename = i[1]
		elif i[0] == '-t':
			threadnum = i[1]
		
	red = redisvis()
	red.filename = filename
	red.scanque(red.getip(host,port))
	red.run(threadnum)