#/usr/bin/env python2.7
import os
import sys
import bencode
import hashlib
import urlparse
import shutil
from pprint import pprint

class torrent(object):
	def __init__(self,filename=None):
		if filename:
			self._torrentfilepath = filename
			self._metainfo = bencode.bdecode(open(os.path.expanduser(filename),'rb').read())
			#_info = metainfo['info']
			self._info_hash = hashlib.sha1(bencode.bencode(self._metainfo['info'])).hexdigest().upper()
			self._tracker = self._metainfo['announce']
			self._shorttracker = urlparse.urlparse(self._tracker).hostname
			try:
				tempfiles = self._metainfo['info']['files']
				self._files = []
				self._size = 0
				for tf in tempfiles:
					self._files.append({'filename':'/'.join(tf['path']),'filesize':tf['length']})
					self._size += tf['length']
			except KeyError as e:
				self._files = [{'filename':self._metainfo['info']['name'],'filesize':self._metainfo['info']['length']}]
				self._size = self._metainfo['info']['length']

			self._name = self._metainfo['info']['name']
			self._numfiles = 0
			for f in self._files:
				self._numfiles += 1
		else:
			self._torrentfilepath = ""
			self._metainfo = ""
			#_info = metainfo['info']
			self._info_hash = ""
			self._tracker = ""
			self._files = ""
			self._size = ""
			self._name = ""
			self._numfiles = ""


	def print_torrent(self):
		pprint (vars(self))


	def check(self,torrentdirectory,pretend=False):
		errors = []
		for f in self._files:
			if not os.path.isfile(os.path.join(torrentdirectory,'/'.join(f['path']))):
				errors.append(os.path.join(torrentdirectory,'/'.join(f['path'])))
			elif not f['length'] == os.path.getsize(os.path.join(torrentdirectory,'/'.join(f['path']))):
				errors.append(os.path.join(torrentdirectory,'/'.join(f['path'])))
		if len(errors) > 0:
			return errors
		else:
			return True

	def copy(self,inputdirectory,outputdirectory,copy=True,dircreate=False,pretend=False):
		################
		# Copies matched torrent files from input directory to output directory
		#
		# self = torrent object
		# inputdirectory = searched directory
		# outputdirectory = hashpath
		################
		inputdirectory = to_unicode(inputdirectory)
		outputdirectory = to_unicode(outputdirectory)
		miss = []
		huntlist = False
		#pprint (vars(self))
		#print self._files[0]['filename']
		if self._numfiles > 1:
			destpath = os.path.join(outputdirectory,to_unicode(self._name))
		elif self._numfiles == 1 and self._files[0]['filename'] != self._name:
			#print self._files[0]['filename'],self._name
			destpath = os.path.join(outputdirectory,to_unicode(self._name))
		else:
			destpath = outputdirectory
		#print 'destpath '+destpath
		for f in self._files:
			in_filename = to_unicode(f['filename']).lstrip(os.path.sep)
			print in_filename
			in_filesize = f['filesize']
			srcfile = None
			dstfile = None
			#if self._numfiles == 1 and os.path.isfile(os.path.join(inputdirectory,f['filename'])) and f['filesize'] == os.path.getsize(os.path.join(inputdirectory,f['filename'])):
			if self._numfiles == 1:
				#print 'single file torrent'
				try: 
					# Single file in input folder
					filesize =  os.path.getsize(os.path.join(inputdirectory,in_filename))
				except OSError:
					pass
				else:
					if in_filesize == os.path.getsize(os.path.join(inputdirectory,in_filename)):
						#print 'Single file in input folder'
						srcfile = os.path.join(inputdirectory,in_filename)
						#dstfile = os.path.join(os.path.expanduser(outputdirectory),in_filename)
				try: 
					# Single file, direct link
					filesize = os.path.getsize(inputdirectory)
				except OSError:
					pass
				else:
					if in_filesize == os.path.getsize(inputdirectory):
						#print 'Single file, direct link'
						srcfile = os.path.join(inputdirectory)
						#dstfile = os.path.join(os.path.expanduser(outputdirectory),in_filename)
				try:
					# single file in torrentname folder
					filesize =  os.path.getsize(os.path.join(inputdirectory,to_unicode(self._name),in_filename))
				except OSError:
					pass
				else:
					if in_filesize == os.path.getsize(os.path.join(inputdirectory,to_unicode(self._name),in_filename)):
						#print 'single file in torrentname folder'
						srcfile = os.path.join(inputdirectory,to_unicode(self._name),in_filename)
			elif self._numfiles > 1:
				#print 'multi-file torrent'
				try: 
					# Multi-file, folder containing torrent named folder
					filesize = os.path.getsize(os.path.join(inputdirectory,to_unicode(self._name),in_filename))
				except OSError:
					pass
				else:
					if in_filesize == os.path.getsize(os.path.join(inputdirectory,to_unicode(self._name),in_filename)):
						#print 'Multi-file, folder containing torrent name'
						srcfile = os.path.join(inputdirectory,to_unicode(self._name),in_filename)
						#dstfile = os.path.join(os.path.expanduser(outputdirectory),in_filename)
				try: 
					# Multi-file, path to actual folder
					filesize = os.path.getsize(os.path.join(inputdirectory,in_filename))
				except OSError:
					pass
				else:
					if in_filesize == os.path.getsize(os.path.join(inputdirectory,in_filename)):
						#print 'Multi-file, path to actual folder'
						srcfile = os.path.join(inputdirectory,in_filename)
						#dstfile = os.path.join(os.path.expanduser(outputdirectory),in_filename)

			# else hunt for a filename and size match.
			if not srcfile:
				if not huntlist:
					huntlist = []
					try:
						for directory, dirnames, filenames in os.walk(os.path.expanduser(inputdirectory)):
							for fi in filenames:
								huntlist.append(os.path.join(directory,fi))
					except UnicodeDecodeError as e:
						print e
						print os.path.join(directory,fi)

				for infile in huntlist:
					if os.path.basename(in_filename) == os.path.basename(infile) and in_filesize == os.path.getsize(infile):
						srcfile = infile
						#dstfile = os.path.join(os.path.expanduser(outputdirectory),in_filename)
						break

			if srcfile:
				#print 'srcfile: '+srcfile
				dstfile = os.path.join(os.path.expanduser(destpath),to_unicode(in_filename))
				#print 'in_filename: '+to_unicode(in_filename)
				#print 'destpath: '+destpath
				#print 'dstfile: '+dstfile
				if dircreate and not pretend:
					try:
						os.stat(os.path.dirname(dstfile))
					except:
						os.makedirs(os.path.dirname(dstfile))
				if dircreate and pretend:
					try:
						os.stat(os.path.dirname(os.path.realpath(dstfile)))
					except:
						print 'Create directory: %s' % (os.path.dirname(os.path.realpath(dstfile)))
				if copy and pretend:
					print '%s copied to %s' % (srcfile,dstfile)
				if copy and not pretend:
					print '%s copied to %s' % (srcfile,dstfile)
					shutil.copy(srcfile,dstfile)
				if not copy and pretend:
					print '%s moved to %s' % (srcfile,dstfile)
				if not copy and not pretend:
					print '%s moved to %s' % (srcfile,dstfile)
					shutil.move(srcfile,dstfile)
			else:
				miss.append(in_filename)
		#print miss
		# if miss:
		# 	with open('/home/lift/miss.txt', 'a') as f:
		# 		f.write(self._shorttracker.encode('utf8')+' '+to_unicode(self._name).encode('utf8')+'\n')
		# else:
		# 	with open('/home/lift/found.txt', 'a') as f:
		# 		f.write(self._shorttracker.encode('utf8')+' '+to_unicode(self._name).encode('utf8')+'\n')
		return 'thats all folks'

	def move(self,inputdirectory,outputdirectory,copy=False,dircreate=False,pretend=False):
		self.copy(inputdirectory,outputdirectory,copy=copy,pretend=pretend)

	# 
	def sort(self,inputdirectory,torrentbasedir,dircreate=False,copy=False,pretend=False):
		###########################
		# Sorts to hash id directory
		#
		# self = torrent object
		# inputdirectory = directory to search
		# torrentbasedir = download directory WITHOUT hash ID. ex: /media/sda1/torrents
		# returns download directory WITH hash ID ex: /media/sda1/torrents/ABCDEFG1234567890
		###########################
		hashpath = os.path.join(os.path.expanduser(torrentbasedir),self._info_hash) #urlparse.urlparse(self._tracker).hostname,
		# if self._numfiles > 1:
		# 	destpath = os.path.join(hashpath,to_unicode(self._name))
		# else:
		# 	destpath = hashpath
		destpath = hashpath
		if inputdirectory is not None and pretend:
			self.copy(inputdirectory,destpath,dircreate=dircreate,pretend=pretend,copy=copy)
			print '%s copied to %s' % (self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
		elif inputdirectory is None and pretend:
			print 'No data copied - new torrent'
			print 'Torrent file copied to %s' % (os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
		elif inputdirectory is not None and not pretend:
			self.copy(inputdirectory,destpath,dircreate=dircreate,pretend=pretend,copy=copy)
			print '%s copied to %s' % (self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
			try:
				os.stat(os.path.dirname(os.path.join(hashpath,to_unicode(self._name)+'.torrent')))
			except:
				os.makedirs(os.path.dirname(os.path.join(hashpath,to_unicode(self._name)+'.torrent')))
			shutil.copy(self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
		else: #inputdirectory is None, and not pretend
			try:
				shutil.copy(self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
				print '%s copied to %s' % (self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
			except IOError:
				if dircreate:
					os.makedirs(hashpath)
					shutil.copy(self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
					print '%s copied to %s' % (self._torrentfilepath,os.path.join(hashpath,to_unicode(self._name)+'.torrent'))
				else:
					print 'Target directory does not exist, use -d to create.  Exiting...'
					sys.exit(1)
		return hashpath

	def find_hash(self,downloadpaths):
		for dlp in downloadpaths:
			if os.path.isdir(os.path.join(dlp,self._info_hash)):
				return dlp
		return False


def to_unicode(text): 
	""" Return a decoded unicode string.  
		False values are returned untouched. 
	"""  
	if not text or isinstance(text, unicode): 
		return text 
	
	try: 
		# Try UTF-8 first 
		return text.decode("UTF-8") 
	except UnicodeError: 
		try: 
			# Then Windows Latin-1 
			return text.decode("CP1252") 
		except UnicodeError: 
			# Give up, return byte string in the hope things work out 
			return text 
