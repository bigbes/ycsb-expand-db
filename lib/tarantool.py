#!/usr/bin/env python

from db import DB
from db import timet, chroot_, cleanup, get_time
import shlex
import os
from subprocess import PIPE, STDOUT, Popen
from time import sleep, time
import fileinput

class Tarantool(DB):
	_exe = "tarantool_box"
	_cli = "tarantool"
	_cnf = "tarantool.cfg"
	_log = "tarantool.log"

	_clean = [".snap", ".xlog", ".log"]

	def __init__(self, _dir):
		self._dir = _dir
		self._run = None
		self.port = '33013'
		if not (os.path.exists(self._dir+'/'+self._exe)):
			raise Exception('No such file or directory in DB: ' + self._dir)

	def set_port(self, port):
		self.port = port

	def __del__(self):
		self.stop()

	@chroot_
	def init(self):
		if self._run:
			print "<<Stop Tarantool, Please"
			return -1
		cleanup(self._clean)
		Popen(shlex.split("./"+self._exe+" --init-storage"), 
			stdout=PIPE, stderr=PIPE).wait()
		print ">>Cleanup Tarantool"

	def flush_db(self):
		if not self._run:
			print "<<Start Tarantool, Please"
			return -1
		Popen(shlex.split(self._dir+self._cli+" -p "
			+self.port+" \"lua box.space[0]:truncate()\"")).wait()

	@timet
	def save_snapshot(self):
		if not self._run:
			print "<<Start Tarantool, Please"
			return -1
		Popen(shlex.split(self._dir+self._cli+" -p "
			+self.port+" \"save snapshot\"")).wait()

	def load_snapshot(self):
		if self._run:
			print "<<Stop Tarantool, Please"
			return -1
		return get_time(self)

	@chroot_
	def start(self, delay=True):
		if self._run:
			return
		print ">>Starting Tarantool"
		self._run = Popen(shlex.split("./"+self._exe))
		if delay:
			get_time(self)
		print ">>Tarantool PID:", self._run.pid

	def stop(self):
		if not self._run:
			print ">>Tarantool already stopped"
			return -1
		self._run.terminate()
		self._run = None
		print ">>Stopping Tarantool"
