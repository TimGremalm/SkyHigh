#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import getopt
import threading
import time
import vlc

#Global modes
shutdown = False
verboseMode = 1
playFile = ""

def about():
	print("SkyHigh")
	print("=======")
	print("Plays a clip when an PIR-sensor triggers a GPIO on a Raspberry Pi.")
	print("By Tim Gremalm, tim@gremalm.se, http://tim.gremalm.se")

def main():
	if verboseMode > 1:
		print("Starting SkyHigh")

	#Start listening for SIGINT (Ctrl+C)
	signal.signal(signal.SIGINT, signal_handler)

	initVLC()

	t = threading.Thread(target=threadPlayLoop, args=())
	t.start()

	#Cause the process to sleep until a signal is received
	signal.pause()

	unloadVLC()

	if verboseMode > 2:
		print("Thread is closed, terminating process.")
	sys.exit(0)

class Player():
	def __init__(self):
		# creating a basic vlc instance
		self.instance = vlc.Instance('--fullscreen', '--mouse-hide-timeout=0')
		# creating an empty vlc media player
		self.mediaplayer = self.instance.media_player_new()
		self.isPaused = False

	def PlayPause(self):
		if self.mediaplayer.is_playing():
			self.mediaplayer.pause()
			self.isPaused = True
		else:
			if self.mediaplayer.play() == -1:
				self.OpenFile()
				return
			self.mediaplayer.play()
			self.isPaused = False

	def Stop(self):
		self.mediaplayer.stop()
		self.playbutton.setText("Play")

	def OpenFile(self, filename=None):
		if not filename:
			return
		if sys.version < '3':
			filename = unicode(filename)
		self.media = self.instance.media_new(filename)
		self.mediaplayer.set_media(self.media)

		# parse the metadata of the file
		self.media.parse()
		self.PlayPause()

	def setVolume(self, Volume):
		self.mediaplayer.audio_set_volume(Volume)

	def setPosition(self, position):
		self.mediaplayer.set_position(position)
		# the vlc MediaPlayer needs a float value between 0 and 1

def initVLC():
	player = Player()
	player.OpenFile(playFile)
	if verboseMode > 1:
		print("VLC Init")

def unloadVLC():
	if verboseMode > 1:
		print("VLC Unload")

def threadPlayLoop():
	while not shutdown :
		if verboseMode > 1:
			print("play loop")
		time.sleep(1)

def aboutAndUsage():
	about()
	usage()

def usage():
	print ("--file : filename to be played")
	print ("--help : shows this help")
	print ("--debug : shows all events")
	print ("--silent : keeps quiet")

def signal_handler(signal, frame):
	if verboseMode > 0:
		print(' SIGINT detected. Prepareing to shut down.')
	global shutdown
	shutdown = True

def parseArgs():
	try:
		opts, args = getopt.getopt(sys.argv[1:],"f:hdsv",["file=","help", "debug", "silent", "verbose"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(1)

	for o, a in opts:
		global verboseMode
		if o in ("-h", "--help"):
			aboutAndUsage()
			sys.exit(0)
		elif o in ("-s", "--silent"):
			verboseMode = 0
		elif o in ("-d", "--debug"):
			verboseMode = 2
		elif o in ("-v", "--verbose"):
			verboseMode = 3
		elif o in ("-f", "--file"):
			global playFile
			playFile = a
		else:
			raise Exception("Unhandled option %s." % o)

if __name__ == '__main__':
	#Parse Arguments
	parseArgs()

	#Call Main-function
	main()

