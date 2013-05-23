#!/usr/bin/env python

from db import DB
from db import timet, chroot_, cleanup, get_time
import shlex
import os
from subprocess import PIPE, STDOUT, Popen
from time import sleep, time
import fileinput

class Redis(DB):
	_exe = "redis-server"
	_cli = "redis-cli"
	_cnf = "redis.conf"
	_log = "redis.log"

	_clean = [".rdb", ".aof", ".log"]

	def __init__(self, _dir):
		self._dir = _dir
		self._run = None
		self.port = '3679'
		if not (os.path.exists(self._dir+'/'+self._exe) and
				os.path.exists(self._dir+'/'+self._cli)):
			raise Exception('No such file or directory in DB: ' + self._dir)

	def __del__(self):
		self.stop()

	@chroot_
	def init(self):
		cleanup(self._clean)
		print ">>Cleanup Redis"

	def flush_db(self):
		if not self._run:
			print "<<Start Redis, Please"
			return -1
		Popen(shlex.split(self._dir+self._cli_dir+self._cli+" -p "
			+self.port+" \"flushall\"")).wait()

	def save_snapshot(self):
		@timet
		def _get_time():
			Popen(shlex.split(self._dir+self._cli_dir+self._cli+" -p "
				+self.port+" \"save\""), stderr).wait()

		if not self._run:
			print "<<Start Redis, Please"
			return -1
		return _get_time()

	def load_snapshot(self):
		if self._run:
			print "<<Stop Redis, Please"
			return -1
		return get_time(self)

	@chroot_
	def start(self, delay):
		if self._run:
			print "Redis already started"
		print ">>Starting Redis"
		self._run = Popen(shlex.split("./"+self._exe+" "+self._cnf))
		print ">>Redis PID:", self._run.pid
	
	def stop(self):
		if not self._run:
			print ">>Redis already stopped"
			return -1
		self._run.terminate()
		self._run.wait()
		self._run = None
		print ">>Stopping Redis"
