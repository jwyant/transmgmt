#/usr/bin/env python2.7
import json
import os
import transmissionrpc
import urlparse
import glob
import shutil
import torrent

class daemon(object):
	def __init__(self,jsonconfig=None):

		if jsonconfig:
			self._name = jsonconfig['name']
			#self._downloadbase = os.path.expanduser(jsonconfig['downloadbase'])
			#self._rpcusername = c['rpc-username']
			self._configdirectory = os.path.expanduser(jsonconfig['directory'])
			self._password = jsonconfig['password']
			self._hashdir = os.path.join(self._configdirectory,'torrents')
			#self._downloadpaths = jsonconfig['downloadpaths']
			#self._rpcport = c['rpc-port']
		else:
			self._name = ''
			#self._downloadbase = ''
			#self._rpcusername = ''
			self._directory = ''
			self._password = ''
			self._hashdir = ''
			#self._downloadpaths ''
			#self._rpcport = ''
		try:
			tdconfig = json.load(open(os.path.join(os.path.expanduser(self._configdirectory),'settings.json')))
		except:
			print 'No config file present!'
			self._rpcport = ''
			self._rpcusername = ''
		else:
			self._rpcport = tdconfig['rpc-port']
			self._rpcusername = tdconfig['rpc-username']

		self._client = transmissionrpc.Client('localhost',port=self._rpcport,user=self._rpcusername, password=self._password)

	def _get_numtorrents(self):
		#numtorrents = 0
		# for t in self._client.get_torrents():
		# 	numtorrents += 1
		#numtorrents = len(self._client.get_torrents()) or 0
		print len(os.listdir(self._hashdir))
		numtorrents = len(os.listdir(self._hashdir))
		return numtorrents

	def _get_numfiles(self):
		numfiles = 0
		for t in self._client.get_torrents():
			for f in t.files():
				numfiles += 1
		return numfiles

	
	def _calc_freespace(self,inputdir):
		fs_space = self._client.free_space(inputdir)
		#listoftorrents = self._client.get_torrents()
		#remainingdownload = 0
		#for t in listoftorrents:
		#	remainingdownload += (1-t.percentDone)*t.sizeWhenDone
		#print remainingdownload
		return fs_space

	def _calc_remaining(self,inputdir):
		fs_space = self._client.free_space(inputdir)
		listoftorrents = self._client.get_torrents()
		remainingdownload = 0
		for t in listoftorrents:
			if inputdir in t.downloadDir:
				remainingdownload += (1-t.percentDone)*t.sizeWhenDone
		#print remainingdownload
		return remainingdownload

	def _add_torrent(self,torrentfile,torrentdirectory):
		try:
			self._client.add_torrent(torrentfile,download_dir=torrentdirectory)
		except transmissionrpc.TransmissionError as e:
			print e
			with open(os.path.expanduser('~/.config/transmgmt/errors.log'),'a') as f:
				f.write('TransmissionError: '+torrentfile+'\n')

	def hunt(self,inputdir):
		huntlist = []
		for directory, dirnames, filenames in os.walk(os.path.expanduser(inputdir)):
			for fi in filenames:
				huntlist.append(os.path.join(directory,fi))
		print self._name
		print inputdir
		listoftorrents = self._client.get_torrents()
		#listoftorrents = [self._client.get_torrent('e5bae1096a3520f3bcc49ed37c3586707e4c7a71')]
		#57a11c769ed5f3eb48631542abef62472826693d
		for t in listoftorrents:
			#print t.downloadDir
			if t.percentDone < 1 and t.status == 'stopped':
				for f in t.files():
					if t.files()[f]['completed'] < t.files()[f]['size']:
						print t.files()[f]['name']
						print t.files()[f]['size']
						if [s for s in huntlist if t.files()[f]['name'] in s]:
							for ml in [s for s in huntlist if t.files()[f]['name'] in s]:
								if os.path.getsize(ml) == t.files()[f]['size']:
									srcfile = ml
									dstfile = os.path.join(t.downloadDir,torrent.to_unicode(t.files()[f]['name']))
									shutil.copy(srcfile,dstfile)
					#print maybelist

def which_daemon(listofdaemons):
	listofnumberoftorrents = []
	for d in listofdaemons:
		listofnumberoftorrents.append(d._get_numtorrents())
	return listofdaemons[listofnumberoftorrents.index(min(listofnumberoftorrents))]

def which_basedirs_space(listofdaemons,sizeoftorrent,downloadpaths):
	returnbasedirs = []
	for dlp in downloadpaths:
		statvfs = os.statvfs(dlp)
		if sizeoftorrent < (statvfs.f_frsize * statvfs.f_bavail)*1.05: 
			# 5% extra for good measure!
			returnbasedirs.append(dlp)
	return returnbasedirs

def get_basedirs_numtorrents(listofdaemons,downloadpaths):
	numtorrents = {}
	for dlp in downloadpaths:
		numtorrents[dlp] = len(os.listdir(dlp))
	return numtorrents
	

def hash_exists(listofdaemons,hashstring):
	for d in listofdaemons:
		globpattern = os.path.join(d._hashdir,'*'+hashstring.lower()[:16]+'*.torrent')
		if glob.glob(globpattern):
			if d._client.get_torrent(hashstring.lower()):
				return True
			#for t in d._client.get_torrents():
			#	if t.hashString == hashstring.lower():
			
	return False

def startstopped(listofdaemons):
	for d in listofdaemons:
		for t in d._client.get_torrents():
			if t.percentDone == 1 and t.status == 'stopped':
				print t.hashString,t.status
				t.start()

def get_attribute(listofdaemons,attribute,inputhashstring):
	for d in listofdaemons:
		t = d._client.get_torrent(inputhashstring)
		if attribute == 'tracker':
			return urlparse.urlparse(t.trackers[0]['announce']).hostname
	return False

