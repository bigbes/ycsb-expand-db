#!/usr/bin/env python
from subprocess import Popen, PIPE
from shlex import split
from shutil import copy2 as copy, rmtree
import os
import urllib2
import tarfile

DBS = ['MongoDB', 'Redis', 'Tarantool']
#DBS = ['Redis', 'Tarantool']
MongoDB = ["2.2.1"]
#Redis = ["2.4.17", "2.6.0"]
Redis = ["2.6.0"]
Tarantool_client = False
Tarantool = [
#		('master', '1af7b0b9c61222369c77a87d4e683e258d36753a'),
		('master-stable', '90918f898b3975351211766b939d1338a25dfc84')
		]

curdir = os.getcwd()
null = open('/dev/null', 'w')
logfile = open('logfile', 'w')
conffile = open('_db_serv.cfg', 'w')

confstr = """
	[[%(name)s]]
		_d=%(_dir)s
		db=%(_type)s"""

def get_tarantool(container):
	branch = container[0]
	revision = container[1]
	client = Tarantool_client
	ans = ('tnt_' + branch, os.getcwd() + '/tnt_' + branch)
	print 'Downloading Tarantool ' + branch + ' ' + revision
	try:
		os.mkdir("tnt_"+branch)
	except OSError:
		print 'Tarantool already been built'
		return ans
	Popen(split("git clone git://github.com/mailru/tarantool.git -b {0} tarantool-{0}".format(branch)), stdout=logfile, stderr=logfile).wait()
	os.chdir("tarantool-" + branch)
	Popen(split("git checkout -f " + revision), stdout=logfile, stderr=logfile).wait()
	
	print 'Building Tarantool' + (' with client' if client else '')
	Popen(split("cmake . "+('-DENABLE_CLIENT=TRUE' if client else '')), stdout=logfile, stderr=logfile).wait()
	tmp = Popen(split("make -j3"), stdout=logfile, stderr=logfile)
	tmp.wait()
	if tmp.returncode != 0:
		print 'Tarantool make failed ' + branch + ' ' + version
		exit()

	print 'Copying Tarantool files'
	os.chdir("..")
	try:
		copy("tarantool-{0}/src/box/tarantool_box".format(branch), "tnt_"+branch)
	except:
		copy("tarantool-{0}/mod/box/tarantool_box".format(branch), "tnt_"+branch)
	if client:
		copy("tarantool-{0}/client/src/tarantool".format(branch), "tnt_"+branch)
	copy(curdir+"/confs/tarantool.cfg", "tnt_"+branch)
	
	os.chdir("tnt_"+branch)
	Popen(split("./tarantool_box --init-storage"), stdout=logfile, stderr=logfile).wait()
	os.chdir("..")
	
	rmtree("tarantool-" + branch)
	return ans

def get_redis(version):
	ans = ('rds_' + version, os.getcwd() + '/rds_' + version)
	print 'Building Redis ' + version
	try:
		os.mkdir("rds_"+version)
	except OSError:
		print 'Redis already been built'
		return ans

	archive = "redis-"+version
	url = "http://redis.googlecode.com/files/{0}.tar.gz".format(archive)
	source = urllib2.urlopen(url)

	open(archive+".tar.gz", "wb").write(source.read())

	tar = tarfile.open(archive+".tar.gz", "r:gz")
	tar.extractall()
	tar.close()

	os.chdir(archive)
	tmp = Popen(split("make -j4"), stdout=logfile, stderr=logfile)
	tmp.wait()
	if tmp.returncode != 0:
		print 'Redis make failed ' + version
		exit()
	os.chdir('..')
	
	print 'Copying Redis files'
	copy(archive+'/src/redis-cli','rds_'+version)
	copy(archive+'/src/redis-server','rds_'+version)
	copy(curdir+'/confs/redis.conf', 'rds_'+version)

	rmtree(archive)
	os.remove(archive+".tar.gz")
	return ans


def dwn_mongodb(version):
	ans = ('mongodb_' + version, os.getcwd() + '/mongodb_' + version)
	print 'Downloading MongoDB ' + version
	try:
		os.mkdir(ans[0])
	except OSError:
		return ans
		
	archive = "mongodb-linux-x86_64-"+version
	url = "http://fastdl.mongodb.org/linux/{0}.tgz".format(archive)
	source = urllib2.urlopen(url)

	open(archive+".tar.gz", "wb").write(source.read())

	tar = tarfile.open(archive+".tar.gz", "r:gz")
	tar.extractall()
	tar.close()

	print 'Copying MongoDB files'
	copy(archive+"/bin/mongod", ans[0])
	copy(archive+"/bin/mongo", ans[0])

	rmtree (archive)
	os.remove(archive+".tar.gz")
	return ans

def get_mongodb(version):
	ans = ('mongodb_' + version, os.getcwd() + '/mongodb_' + version)
	print 'Downloading MongoDB ' + version
	try:
		os.mkdir(ans[0])
	except OSError:
		return ans

	archive = ('mongodb-src-r'+version)
	url = "http://fastdl.mongodb.org/src/{0}.tar.gz".format(archive)
	source = urllib2.urlopen(url)
	
	open(archive+".tar.gz", "wb").write(source.read())
	
	tar = tarfile.open(archive+".tar.gz", "r:gz")
	tar.extractall()
	tar.close()

	print "Building MongoDB"
	os.chdir(archive)
#	tmp = 
	tmp = Popen(split("patch <../../new-db-patches/mongodb_{1}.patch -p1".format(curdir+'/new-db-patches/', version))).wait()
	if tmp != 0:
		print 'MongoDB patching failed ' + version + tmp
		exit()
	tmp = Popen(split("Scons mongod mongo -j 5")).wait()
	if tmp != 0:
		print 'MongoDB make failed ' + version + tmp
		exit()
	os.chdir('..')

	print "Copying MongoDB files"
	copy(archive+"/mongod", ans[0])
	copy(archive+"/mongo", ans[0])

	rmtree (archive)
	os.remove(archive + '.tar.gz')
	return ans	

try:
	os.mkdir('envir')
except OSError:
	pass

<<<<<<< HEAD
conffile.write('DB = ' + str(DBS)[1:-1] + '\nport = 2000\n')
=======
conffile.write('DB = ' + str(DBS)[1:-1] + '\nport=2000\n')
>>>>>>> 91c536cf78cdd6caadd91128db44117fbc9386aa
conffile.write('[DBS]')

os.chdir('envir')
for i in DBS:
	for j in locals()[i]:
		_dir = globals()['get_'+i.lower()](j)
		if isinstance(_dir, (tuple, list)):
			conffile.write(confstr % {
				'name' : _dir[0],
				'_dir' : _dir[1],
				'_type': i
				})
print 'Done!'
os.chdir('..')
