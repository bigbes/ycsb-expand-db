#!/usr/bin/env python
from subprocess import Popen, PIPE
from shlex import split
from shutil import copy2 as copy, rmtree
from socket import gethostname
import sys
import os
import urllib2
import tarfile

Threads = '3'
DBS = ['MongoDB', 'Redis', 'Tarantool']
MongoDB = ["2.2.2"]
Redis = ["2.6.5"]
Tarantool_client = True
Tarantool = [
		('master', '02a8b0c54dedc087600b491fe467a76345b73480', ['tree', 'hash'])
		]

curdir = os.getcwd()
null = open('/dev/null', 'w')
logfile = open('logfile', 'w')
conffile = open('_db_serv.cfg', 'w')
dbfile = open('_bench.cfg.bak', 'w')

Port = '2000'

confstr1 = """
	[[%(name)s]]
		_d = %(_dir)s
		db = %(_type)s"""
confstr2 = """
	[[%(name)s]]
		_type = %(_type)s
		host = %(_host)s
		db_port = 
		serv_port = %(_port)s"""

def _print(str):
	print str,
	sys.stdout.flush()

def get_tarantool(container):
	branch = container[0]
	revision = container[1]
	client = Tarantool_client
	rev = container[1][-6:-1]
	fstr = 'tnt_' + branch + '_%s_'+rev
	ans = [(fstr % (i), os.getcwd() + '/' + fstr %(i), i) for i in container[2]]
	_print('Tarantool ' + branch + ' ' + revision + '..')
	for i in ans:
		try:
			os.mkdir(i[0])
		except OSError:
			print 'Tarantool already been built'
			return ans
	_print('Downloading..')
	Popen(split("git clone git://github.com/mailru/tarantool.git -b {0} tarantool-{0}".format(branch)), stdout=logfile, stderr=logfile).wait()
	os.chdir("tarantool-" + branch)
	Popen(split("git checkout -f " + revision), stdout=logfile, stderr=logfile).wait()
	
	_print('Building' + (' with client' if client else '') + '..')

	envir = dict(os.environ)
	envir['CFLAGS'] = ' -march=native '
	Popen(split("cmake . -DENABLE_TRACE=OFF -DCMAKE_BUILD_TYPE=Release "+('-DENABLE_CLIENT=TRUE' if client else '')), stdout=logfile, stderr=logfile, env=envir).wait()
	
	if Popen(split("make -j"+Threads), stdout=logfile, stderr=logfile).wait() != 0:
		print 'Tarantool make failed ' + branch + ' ' + revision
		os.chdir('..')
		for i in ans:
			rmtree(i[0])
		rmtree('tarantool-' + branch)
		exit()

	_print('Copying..')

	os.chdir("..")
	for i in ans:
		copy("tarantool-{0}/src/box/tarantool_box".format(branch), i[0])
		if client:
			copy("tarantool-{0}/client/tarantool/tarantool".format(branch), i[0])
		copy(curdir+"/confs/tarantool_"+i[2]+".cfg", i[0]+'/tarantool.cfg')
	
		os.chdir(i[0])
		Popen(split("./tarantool_box --init-storage"), stdout=logfile, stderr=logfile).wait()
		os.chdir("..")
	
	rmtree("tarantool-" + branch)
	print 'Done!'
	return ans

def get_redis(version):
	ans = ('rds_' + version, os.getcwd() + '/rds_' + version)
	_print('Redis ' + version + '..')

	try:
		os.mkdir("rds_"+version)
	except OSError:
		print 'Redis already been built'
		return [ans]
	
	_print('Downloading..')

	archive = "redis-"+version
	url = "http://redis.googlecode.com/files/{0}.tar.gz".format(archive)
	source = urllib2.urlopen(url)

	open(archive+".tar.gz", "wb").write(source.read())

	tar = tarfile.open(archive+".tar.gz", "r:gz")
	tar.extractall()
	tar.close()

	_print('Building..')
	os.chdir(archive)
	if Popen(split("make -j"+Threads), stdout=logfile, stderr=logfile) != 0:
		print 'Redis make failed ' + version
		os.chdir('..')
		rmtree(ans[0])
		rmtree(archive)
		exit()
	os.chdir('..')
	
	_print('Copying..')

	copy(archive+'/src/redis-cli','rds_'+version)
	copy(archive+'/src/redis-server','rds_'+version)
	copy(curdir+'/confs/redis_%s.conf' % (version), 'rds_'+version+'/redis.conf')

	rmtree(archive)
	os.remove(archive+".tar.gz")
	print 'Done!'
	return [ans]

def get_mongodb(version):
	ans = ('mongodb_' + version, os.getcwd() + '/mongodb_' + version)
	_print('MongoDB ' + version + '..')
	try:
		os.mkdir(ans[0])
	except OSError:
		print 'MongoDB already been built'
		return [ans]

	_print('Downloading..')
	archive = ('mongodb-src-r'+version)
	url = "http://fastdl.mongodb.org/src/{0}.tar.gz".format(archive)
	source = urllib2.urlopen(url)
	
	open(archive+".tar.gz", "wb").write(source.read())
	
	tar = tarfile.open(archive+".tar.gz", "r:gz")
	tar.extractall()
	tar.close()

	_print("Patching..")
	os.chdir(archive)
	if Popen(split("patch  -i ../../new-db-patches/mongodb_{1}.patch -p1".format(curdir+'/new-db-patches/', version)), stdout=logfile, stderr=logfile).wait() != 0:
		print 'MongoDB patching failed ' + version + tmp
		os.chdir('..')
		rmtree(ans[0])
		rmtree(archive)
		exit()
	_print ("Building..")
	if Popen(split("scons mongod mongo -j "+Threads), stdout=logfile, stderr=logfile).wait() != 0:
		print 'MongoDB make failed ' + version + tmp
		os.chdir('..')
		rmtree(ans[0])
		rmtree(archive)
		exit()
	os.chdir('..')

	_print ("Copying..")
	copy(archive+"/mongod", ans[0])
	copy(archive+"/mongo", ans[0])

	rmtree (archive)
	os.remove(archive + '.tar.gz')
	print "Done!"
	return [ans]

try:
	os.mkdir('envir')
except OSError:
	pass

conffile.write('DB = ' + str(DBS)[1:-1] + '\nport = '+Port+'\n')
conffile.write('[DBS]')
dbfile.write('[NET_DB]')

os.chdir('envir')
for i in DBS:
	for j in locals()[i]:
		_dir = globals()['get_'+i.lower()](j)
		for k in _dir:
			conffile.write(confstr1 % {
				'name' : k[0],
				'_dir' : k[1],
				'_type': i
				})
			dbfile.write(confstr2 % {
				'name' : k[0],
				'_type' : i.lower(),
				'_host' : gethostname(),
				'_port' : Port
				})


print 'Done!'
os.chdir('..')
