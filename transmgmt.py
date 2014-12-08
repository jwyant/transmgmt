#!/usr/bin/env python2.7

# standard
import os
import sys
import json
import argparse
from pprint import pprint
import glob
import shutil
import subprocess

# transmgmt
import torrent
import daemon
import config



def main(sysargv):
	parser = argparse.ArgumentParser(prog='transmgmt', usage='%(prog)s [OPTIONS] [ACTION] [ARGS...]', description='Multi-Server Transmission Management!', epilog='Seed! \n\n')
	parser.add_argument('action', help='action for transmgmt to run')
	parser.add_argument('args', help='depends on action: files, directories, or sites', nargs='*')
	parser.add_argument('-v','--verbose', help='increase transmgmt verbosity', action='store_true')
	parser.add_argument('-p','--pretend', help='pretend actions, don\'t actually run them', default=False, action='store_true')
	parser.add_argument('-d','--dircreate', help='create directories if they do not exist', default=False, action='store_true')
	parser.add_argument('-c','--copy', help='*Always* copy, even if you say move', default=False, action='store_true')
	parser.add_argument('-s','--start', help='start torrent upon add/import', default=False,action='store_true')
	args = parser.parse_args()
	if len(sysargv) < 1:
		parser.print_help()
		sys.exit(0)

	if args.verbose:
		print "reading action: %s..." % args.action
		print "reading args: %s..." % args.args
		print "verbose: %s" % args.verbose
		print "pretend: %s" % args.pretend
		print "dircreate: %s" % args.dircreate
		print "copy: %s" % args.copy
		print "start: %s" % args.start

	inputlist = args.args

	#Action Handling
	if args.action.lower() == 'test':
		test(inputlist)

	if args.action.lower() == 'check':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt check [torrentfile] [torrentdirectory]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
			torrentdirectory = os.path.expanduser(inputlist[1])
		except:
			print 'usage: transmgmt check [torrentfile] [torrentdirectory]'
			sys.exit(1)
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Not a valid torrent file'
			sys.exit(1)
		print t.check(torrentdirectory,pretend=args.pretend)

	if args.action.lower() == 'copy':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt copy [torrentfile] [sourcedir] [targetdir]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
			sourcedir = os.path.expanduser(inputlist[1])
			targetdir = os.path.expanduser(inputlist[2])
		except IndexError as e:
			print 'usage: transmgmt copy [torrentfile] [sourcedir] [targetdir]'
			sys.exit(1)
		if not os.path.isdir(sourcedir):
			print 'Source directory does not exist'
			sys.exit(1)
		if not os.path.isdir(targetdir) and not args.dircreate:
			print "Target directory does not exist, use -d to force create"
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Torrent file does not exist!'
			sys.exit(1)
		print t.copy(sourcedir,targetdir,copy=True,pretend=args.pretend,dircreate=args.dircreate)

	if args.action.lower() == 'move':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt copy [torrentfile] [sourcedir] [targetdir]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
			sourcedir = os.path.expanduser(inputlist[1])
			targetdir = os.path.expanduser(inputlist[2])
		except IndexError as e:
			print 'usage: transmgmt copy [torrentfile] [sourcedir] [targetdir]'
			sys.exit(1)
		if not os.path.isdir(sourcedir):
			print 'Source directory does not exist'
			sys.exit(1)
		if not os.path.isdir(targetdir) and not args.dircreate:
			print "Target directory does not exist, use -c to force create"
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Torrent file does not exist!'
			sys.exit(1)
		print t.copy(sourcedir,targetdir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)

	if args.action.lower() == 'sort':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt sort [torrentfile] [sourcedir] [torrentbasedir]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
			sourcedir = os.path.expanduser(inputlist[1])
			torrentbasedir = os.path.expanduser(inputlist[2])
		except:
			print 'usage: transmgmt sort [torrentfile] [sourcedir] [torrentbasedir]'
			sys.exit(1)
		if not os.path.exists(sourcedir):
			print 'Source directory does not exist'
			sys.exit(1)
		if not os.path.isdir(torrentbasedir) and not args.dircreate:
			print "Torrent base directory does not exist, use -c to force create"
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Torrent file does not exist!'
			sys.exit(1)
		print t.sort(sourcedir,torrentbasedir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)



	if args.action.lower() == 'addtodaemon':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt addtodaemon [torrentfile] [sourcedir] [daemonname]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
			sourcedir = os.path.expanduser(inputlist[1])
			daemonname = inputlist[2]
		except:
			print 'usage: transmgmt addtodaemon [torrentfile] [sourcedir] [daemonname]'
			sys.exit(1)
		for d in config.jsonconfig['daemons']:
			#print c
			if d['name'] == daemonname:
				td = daemon.daemon(d)
		try:
			pprint (vars(td))
		except UnboundLocalError as e:
			print 'Did not find torrent client named: %s' % (daemonname)
			sys.exit(1)
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Torrent file does not exist!'
			sys.exit(1)
		print addtodaemon(t,td,sourcedir,basedir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)
			#print addtodaemon(inputlist[0],inputlist[1],inputlist[2],copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)

	if args.action.lower() == 'add':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt add [torrentfile]'
			sys.exit(1)
		try:
			torrentfile = os.path.expanduser(inputlist[0])
		except:
			print 'usage: transmgmt add [torrentfile] [optional:sourcedir]'
			sys.exit(1)
		try:
			sourcedir = os.path.expanduser(inputlist[1])
		except IndexError:
			sourcedir = None
		try:
			t = torrent.torrent(filename=torrentfile)
		except IOError as e:
			print 'Torrent file does not exist!'
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))
		addtorrent(t,listofdaemons,sourcedir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate,startflag=args.start)

	if args.action.lower() == 'import':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt import [dottorrentfolder] [optional: torrentdatafolder]'
			sys.exit(1)
		if os.path.isdir(inputlist[0]):
			dottorrentfolder = os.path.expanduser(inputlist[0])
		try:
			torrentdatafolder = os.path.expanduser(inputlist[1])
		except IndexError:
			torrentdatafolder = None
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))
		torrentimport(dottorrentfolder,listofdaemons,torrentdatafolder,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)

	if args.action.lower() == 'hunt':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt look [hunt folder]'
			sys.exit(1)
		#infohash = inputlist[0]
		inputdirectory = os.path.expanduser(inputlist[0])
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))
		for d in listofdaemons:
			for tdt in d._client.get_torrents():
				if tdt.percentDone < 1 and tdt.status == 'stopped':
					print tdt.name
					t = torrent.torrent(filename=tdt.torrentFile)
					downloaddir = tdt.downloadDir
					print downloaddir
					t.copy(inputdirectory,downloaddir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)
					#tdt = d._client.get_torrent(infohash)

	if args.action.lower() == 'look':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt look [hash] [look folder]'
			sys.exit(1)
		infohash = inputlist[0]
		inputdirectory = os.path.expanduser(inputlist[1])
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))
		for d in listofdaemons:
			try:
				tdt = d._client.get_torrent(infohash)
			except KeyError as e:
				print e
			else:
				t = torrent.torrent(filename=tdt.torrentFile)
				downloaddir = tdt.downloadDir
				print downloaddir
				t.copy(inputdirectory,downloaddir,copy=args.copy,pretend=args.pretend,dircreate=args.dircreate)


# 	if args.action.lower() == 'startstopped':
# 		if inputlist[0] == 'help':
# 			print 'usage: transmgmt startstopped'
# 			sys.exit(1)
# 		listofdaemons = []
# 		for d in config.jsonconfig['daemons']:
# 			listofdaemons.append(daemon.daemon(d))
# 		daemon.startstopped(listofdaemons)

	if args.action.lower() == 'get':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt import [attribute] [hash]'
			sys.exit(1)
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))
		try:
			attribute = inputlist[0]
		except IndexError:
			print 'usage: transmgmt import [attribute] [hash]'
			sys.exit(1)
		try:
			hashstring = inputlist[1].lower()
		except:
			print 'usage: transmgmt import [attribute] [hash]'
			sys.exit(1)
		print daemon.get_attribute(listofdaemons,attribute,hashstring)
		sys.exit(1)

	if args.action.lower() == 'remove':

		# build list of daemons
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))

		# build list of hashes loaded into the daemons
		tdhash = []
		for d in listofdaemons:
			for t in d._client.get_torrents():
				tdhash.append(t.hashString.upper())

		# build list of hashes in download directories
		dlphashlist = []
		for d in config.jsonconfig['downloadpaths']:
			dlphashlist.extend(os.listdir(d))

		# find directories that do not have hashes loaded into transmission-daemon
		missing = list(set(dlphashlist) - set(tdhash))
		print missing
		for d in config.jsonconfig['downloadpaths']:
			for m in missing:
				if os.path.isdir(os.path.join(d,m)):
					src = os.path.join(d,m)
					dst = os.path.join(os.path.dirname(d),config.jsonconfig['removedpath'],m)
					print '%s moved to %s' % (src,dst)
					if not args.pretend:
						try:
							shutil.move(src,dst)
						except UnicodeDecodeError as e:
							print 'filename error, manually run: mv %s %s' % (src,dst)

	if args.action.lower() == 'backup':
		if len(inputlist) == 0 or inputlist[0] == 'help':
			print 'usage: transmgmt backup [optional: hash]'
			sys.exit(1)
		try:
			infohash = inputlist[0]
		except IndexError as e:
			print e
			infohash = False

		# build list of daemons
		listofdaemons = []
		for d in config.jsonconfig['daemons']:
			listofdaemons.append(daemon.daemon(d))

		# build list of existing hashes in backup
		if config.jsonconfig['remoteuser']:
			remoteconnection = config.jsonconfig['remoteuser']+'@'+config.jsonconfig['remotehost']
		else:
			remoteconnection = config.jsonconfig['remotehost']
		remotepath = config.jsonconfig['remotepath']
		ls = subprocess.Popen(['ssh',remoteconnection,'ls',remotepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		remotehashes, err =  ls.communicate()
		#print remotehashes

		if infohash != 'all':
			# check if info has exists and is complete
			t = None
			for d in listofdaemons:
				try:
					t = d._client.get_torrent(infohash.lower())
				except KeyError as e:
					pass
			if t is not None and t.percentDone == 1 and t.hashString.upper() not in remotehashes:
				#print t.downloadDir
				processargs = ['rsync','-avhSP','--whole-file',t.downloadDir,remoteconnection+':'+remotepath]
				print ' '.join(processargs)
				if not args.pretend:
					subprocess.call(processargs)
			elif t is not None and t.percentDone == 1 and t.hashString.upper() in remotehashes:
				print '%s already backed up' % infohash
			elif t is not None and t.percentDone < 1:
				print '%s is not complete' % infohash
			else:
				print '%s does not exist' % infohash
		elif infohash == 'all':
			print 'full backup scan'
			for d in listofdaemons:
				listoftorrents = d._client.get_torrents()
				for t in listoftorrents:
					if t.percentDone == 1 and t.hashString.upper() not in remotehashes:
						#print t.downloadDir
						processargs = ['rsync','-avhSP','--whole-file',t.downloadDir,remoteconnection+':'+remotepath]
						print ' '.join(processargs)
						if not args.pretend:
							subprocess.call(processargs)
		else:
			print 'not sure what\'s going on here...'
			sys.exit(1)

	if args.action.lower() == 'getfilehash':
		inputfile = ' '.join(inputlist)
		t = torrent.torrent(inputfile)
		print t._info_hash.lower()
		sys.exit(0)

def addtodaemon(t,td,sourcedir,basedir,copy=False,pretend=False,dircreate=False,startflag=False):
	targetdir = t.sort(sourcedir,basedir,copy=copy,pretend=pretend,dircreate=dircreate)
	print 'targetdir: '+targetdir
	if not pretend:
		td._add_torrent(t._torrentfilepath,targetdir,startflag)
	else:
		print 'pretend add torrentfile: %s torrentdirectory: %s' % (t._torrentfilepath,targetdir)

def addtorrent(t,listofdaemons,sourcedir,copy=False,pretend=False,dircreate=False,startflag=False):
	if daemon.hash_exists(listofdaemons,t._info_hash):
		print 'Torrent already exists: %s' % (t._info_hash)
	elif t._shorttracker == 'gaia.feralhosting.com':
		print 'Self Tracker: %s' % (t._info_hash)
	elif t.find_hash(config.jsonconfig['downloadpaths']):
		basedir = t.find_hash(config.jsonconfig['downloadpaths'])
		td = daemon.which_daemon(listofdaemons)
		print 'found hash: '+basedir
		addtodaemon(t,td,sourcedir,basedir,copy=copy,pretend=pretend,dircreate=dircreate,startflag=startflag)
	else:
		td = daemon.which_daemon(listofdaemons)
		basedirs = daemon.which_basedirs_space(listofdaemons,t._size,config.jsonconfig['downloadpaths'])
		basedir_torrents = daemon.get_basedirs_numtorrents(listofdaemons,config.jsonconfig['downloadpaths'])
		for key, value in list(basedir_torrents.items()):
			if key not in basedirs:
				del basedir_torrents[key]
		basedir = min(basedir_torrents, key=basedir_torrents.get)
		addtodaemon(t,td,sourcedir,basedir,copy=copy,pretend=pretend,dircreate=dircreate,startflag=startflag)

def torrentimport(dottorrentfolder,listofdaemons,torrentdatafolder=None,copy=False,pretend=False,dircreate=False):
	torrentfiles = []
	for directory, dirnames, filenames in os.walk(os.path.expanduser(dottorrentfolder)):
		for fi in filenames:
			if fi.endswith('.torrent'):
				torrentfiles.append(os.path.join(directory,fi))
	print torrentfiles
	for tf in torrentfiles:
		t = torrent.torrent(filename=tf)
		#if torrentdatafolder is None:
		temptorrentdatafolder = torrentdatafolder or os.path.dirname(t._torrentfilepath)
		#print temptorrentdatafolder
		addtorrent(t,listofdaemons,temptorrentdatafolder,copy=copy,pretend=pretend,dircreate=dircreate)

def test(sysargv):
	t = torrent.torrent(filename=sysargv[0])
	pprint (vars(t))

if __name__ == "__main__":
	main(sys.argv)
