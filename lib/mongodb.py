#!/usr/bin/env python

from db import DB
from db import timet, chroot_, get_time

import shlex
import shutil
import os
import fileinput
import socket

from time import sleep, time
from subprocess import PIPE, STDOUT, Popen
from copy import deepcopy
from pprint import pprint

class MongoDB(DB):
    _exe = "mongod"
    _cli = "mongo"
    _cnf = "mongodb.conf"
    _log = "mongodb.log"

    def __init__(self, _dir):
        self._dir = _dir
        self._run = None
        if not (os.path.exists(self._dir+'/'+self._exe) and
                os.path.exists(self._dir+'/'+self._cli)):
            raise Exception('No such file or directory in DB: ' + self._dir)

    def set_port(self, port):
        self.port = port

    def __del__(self):
        self.stop()

    @chroot_
    def cleanup(self):
        try:
            shutil.rmtree('temp')
        except OSError:
            pass
        try:
            os.mkdir('temp')
            os.mkdir('temp/journal')
        except OSError:
            pass

    def init(self):
        self.cleanup()
        print ">>Cleanup MongoDB"

    def flush_db(self):
        if self._run:
            print "<<Start MongoDB, Please"
            return -1
        Popen(shlex.split(self._dir+self._cli+"localhost"
            +self.port+"/ycsb --eval \"db.dropDatabase()\"")).wait()
        print ">>Flushing MongoDB"

    def load_snapshot(self):
        if self._run:
            print "<<Stop MongoDB, Please"
            return -1
        return get_time(self)

    # Cause MongoDB use Memory Maped files - not implementing
    def save_snapshot(self):
        print "<<Not Yet Implemented"
        return 0

    @chroot_
    def start(self, delay = None):

        if delay == None:
            delay = True
        os.environ["LD_LIBRARY_PATH"] = "."
        if self._run:
            print "<<MongoDB already started."
            return -1
        print ">>Starting MongoDB"
        args = shlex.split("./"+self._exe+" -f mongodb.conf")
        self._run = Popen(args)
        if delay:
            print get_time(self)
        print ">>MongoDB PID:", self._run.pid

    def stop(self):
        if not self._run:
            print ">>MongoDB already stopped"
            return -1
        self._run.send_signal(2)
        self._run.wait()
        self._run = None
        print ">>Stopping MongoDB"
