#!/usr/bin/python

import os
import subprocess
import sys
import tempfile
import re

#TODO: should bother figuring out arg parsing libs
#TODO: --nozenity option

def searchpath(forbinary):
    return bool([True for i in os.environ["PATH"].split(":") if os.path.exists(os.path.join(i, forbinary))])

if "--help" in sys.argv or "-h" in sys.argv:
    print "usage:",sys.argv[0],"[--audio|--noaudio] [--display <X display>] [--fps <rate>] [--window] [--output <savelocation>]"
    
if not searchpath("ffmpeg"):
    print "could not find ffmpeg, enter your password to install it"
    print "(read the script for security first of course)"
    if subprocess.Popen(["sudo", "apt-get", "install", "ffmpeg"]).wait() != 0:
        print "apt-get says something went wrong!"
        sys.exit(1)

numre=re.compile("([0-9]+)")
if "--window" in sys.argv:
    x= subprocess.Popen(["xwininfo"], stdout=subprocess.PIPE).communicate()[0]
    #these make assumptions that could go wrong on any system with an abnormal xwininfo
    windowpos = [numre.search(i).group(1) for i in x.split("\n") if "Absolute upper-left " in i]
    windowsize = [numre.search(i).group(1) for i in x.split("\n") if "Width" in i or "Height" in i]
else:
    x= subprocess.Popen(["xwininfo", "-root"], stdout=subprocess.PIPE).communicate()[0]
    windowpos=["0","0"]
    windowsize = [numre.search(i).group(1) for i in x.split("\n") if "Width" in i or "Height" in i]

tmp = tempfile.mkstemp()
os.fdopen(tmp[0]).close()
tmp=tmp[1]

command = ["ffmpeg"]

if "--audio" in sys.argv or \
      (not "--noaudio" in sys.argv \
        and subprocess.Popen(["zenity", "--question", "--text", "Record Audio?"]).wait() == 0):
    #audio
    audio = True
else:
    audio = False

if audio:
    command.extend("-f alsa -ac 2 -i pulse".split(" "))

command.extend("-f x11grab".split(" "))

fps = 30
if "--fps" in sys.argv:
    fps=int(sys.argv[sys.argv.index("--fps")+1])

command.extend(["-r", str(fps)])

command.extend(["-s", "x".join(windowsize)])

display=":0.0"
if "--display" in sys.argv:
    display=sys.argv[sys.argv.index("--display")+1]

command.extend(["-i", display+"+"+(",".join(windowpos))])

if audio:
    command.extend(["-acodec", "pcm_s16le"])
command.extend("-vcodec libx264 -vpre lossless_ultrafast -threads 0".split(" "))

command.append(tmp)

ffcmd1 = subprocess.Popen(command, stdin=open("/dev/null")) #pipe from the bitbucket so we can keep control of console input
zenitywaiter = subprocess.Popen(["zenity","--info","--text","Click OK to stop recording."]).wait()
ffcmd1.terminate()
time.sleep(2)
ffcmd1.kill()


