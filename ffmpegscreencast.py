#!/usr/bin/python

import os
import subprocess
import sys
import tempfile
import re
import time

#TODO: should bother figuring out arg parsing libs
#TODO: --nozenity option
#TODO: switch to encode to webm

def searchpath(forbinary):
    return bool([True for i in os.environ["PATH"].split(":") if os.path.exists(os.path.join(i, forbinary))])

if "--help" in sys.argv or "-h" in sys.argv:
    print "usage:",sys.argv[0],"[--audio|--noaudio] [--display <X display>] [--fps <rate>] [--window|--fullscr] [--output <savelocation>] [--temp <location>]"
    
if not searchpath("ffmpeg"):
    print "could not find ffmpeg, enter your password to install it"
    print "(read the script for security first of course)"
    if subprocess.Popen(["sudo", "apt-get", "install", "ffmpeg"]).wait() != 0:
        print "apt-get says something went wrong!"
        sys.exit(1)

numre=re.compile("([0-9]+)")
if "--window" in sys.argv or ("--screen" not in sys.argv and subprocess.Popen(["zenity", "--question", "--text", "Record a window?"]).wait() == 0):
    x= subprocess.Popen(["xwininfo"], stdout=subprocess.PIPE).communicate()[0]
    #these make assumptions that could go wrong on any system with an abnormal xwininfo
    windowpos = [numre.search(i).group(1) for i in x.split("\n") if "Absolute upper-left " in i]
    windowsize = [numre.search(i).group(1) for i in x.split("\n") if "Width" in i or "Height" in i]
else:
    x= subprocess.Popen(["xwininfo", "-root"], stdout=subprocess.PIPE).communicate()[0]
    windowpos=["0","0"]
    windowsize = [numre.search(i).group(1) for i in x.split("\n") if "Width" in i or "Height" in i]



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

if "--output" in sys.argv:
    output=sys.argv[sys.argv.index("--output")+1]
else:
    output = subprocess.Popen("zenity --file-selection --save --title".split(" ")+["Select final output name prefix"], stdout=subprocess.PIPE).communicate()[0].strip()

if "--temp" in sys.argv:
    tempinp = sys.argv[sys.argv.index("--temp")+1]
    if os.path.exists(tempinp):
        if os.path.isdir(tempinp):
            tmp = os.path.realpath(tempinp+"/temp.mkv")
        else:
            print "provided temp exists as file!! falling back to normal location"
            tmp = tempfile.mktemp()+".mkv"
    elif os.path.exists(os.path.dirname(tempinp)):
        tmp = tempinp
    else:
        print "provided temp does not exist, falling back to default location"
        tmp = tempfile.mktemp()+".mkv"
else:
    tmp = tempfile.mktemp()+".mkv"

tmp = str(tmp)
print tmp

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
time.sleep(1)
ffcmd1 = subprocess.Popen(command, stdin=open("/dev/null")) #pipe from the bitbucket so we can keep control of console input
zenitywaiter = subprocess.Popen(["zenity","--info","--text","Click OK to stop recording."]).wait()
ffcmd1.terminate()
time.sleep(2)
ffcmd1.kill()

#uses example 1 on the reference page
command=["ffmpeg","-i",tmp]
#if audio:
#these appear to be required
command.extend(["-acodec","libfaac","-ab","128k","-ac","2"])
command.extend("-vcodec libx264 -vpre slow -crf 22 -threads 0".split(" "))
command.append(output+".mp4")

ffcmd2 = subprocess.Popen(command, stdin=open("/dev/null")) #pipe from the bitbucket so we can keep control of console input
zenitynotif = subprocess.Popen(["zenity","--notification","--text","Reencoding screencast..."])
ffcmd2.wait()
zenitynotif.terminate()
time.sleep(0.01)
zenitynotif.kill()
os.unlink(tmp)
subprocess.Popen(["nautilus",os.path.dirname(output)])
