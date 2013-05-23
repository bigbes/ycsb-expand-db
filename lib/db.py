#!/usr/bin/env python
import os
import time
import psutil
import socket
from subprocess import Popen, PIPE

def timet(func):
	def new_func(self, *args, **kw):
		ts = time.time()
		func(self, *args, **kw)
		te = time.time()
		return te-ts
	return new_func

@timet
def get_time(self):
	def fun():
		try:
			sock.connect(('localhost', int(self.port)))
		except socket.error:
			time.sleep(0.01)
			return -1
		return 0
		
	sock = socket.socket(socket.AF_INET)
	sock.settimeout(120)
	if self.start(False) == -1:
		sock.close()
		return -1
	while(fun()):
		pass
	sock.close()

def chroot_(func):
	def new_func(self, *args, **kw):
		_prev_root = os.getcwd()
		_new_root = self._dir
		os.chdir(_new_root)
		result = func(self, *args, **kw)
		os.chdir(_prev_root)
		return result
	return new_func

def cleanup(_clean):
	for i in os.listdir("."):
		for j in _clean:
			if i.find(j) != -1:
				os.remove(i)

class DB:
	def set_dir(self, _dir):
		self._dir = _dir

	def set_port(self, port):
		self.port = int(port)

	def init(self):
		pass

	def flush_db(self):
		pass

	def save_snapshot(self):
		pass

	def load_snapshot(self):
		pass

	def start(self, delay):
		pass

	def stop(self):
		pass

	def mem(self):
		if not _run:
			print "<<Can't check size. Start "+self.__class__.__name__+" Please"
			return -1
		return psutil.Process(self._run.pid).get_ext_memory_info().rss
#		return int(Popen(split('ps o rss -p '+str(self._run.pid)), stdout=PIPE).communicate().split()[1])
