#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import getopt
import threading
import time
from omxplayer import OMXPlayer

#Global modes
shutdown = False
verboseMode = 1
playFile = "/home/pi/skyhigh/movie/MerAnEnBro.mp4"
player = None

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

	initOMX()

	t = threading.Thread(target=threadPlayLoop, args=())
	t.start()

	#Cause the process to sleep until a signal is received
	signal.pause()

	unloadOMX()

	if verboseMode > 2:
		print("Thread is closed, terminating process.")
	sys.exit(0)

def initOMX():
	global player
	if verboseMode > 1:
		print("OMX Init")
	player = OMXPlayer(playFile, args=['--no-osd', '--no-keys', '-b'])

def unloadOMX():
	if verboseMode > 1:
		print("OMX Unload")
	player.quit()

def threadPlayLoop():
	while not shutdown :
		checkPlayerDuration()
		time.sleep(0.5)

def checkPlayerDuration():
	if player.is_playing():
		dur = player.duration()
		pos = player.position()
		delta = dur-pos
		if verboseMode > 2:
			print("Duration: {}".format(delta))
		if delta < 1:
			if verboseMode > 1:
				print("Less than a second left. Pause OMX.")
			player.pause()

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

