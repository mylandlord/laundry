# Author: William Morel, 2017

import sys
import os
import threading
import time
from ftplib import FTP
from cStringIO import StringIO
import serial
import cred
import signal

POLLSECONDS=600

# Python 2.7 because thats on my Raspberry Pi
# this is the embedded client
# intended for auto execution on raspberry pi boot
# run in directory that has the unused tokens
# manually create a UsedTokens subdir
# non git cred.py needed for SERVER,USER,PASSWORD
# will move tokens to UsedTokens subdirectory when a token is entered by user via keyboard
# tokens are files with names ending in .tok that have 6 chars in filename, eg abcdef.tok
# uses a thread for keyboard input of tokens (first char selects machine, following six are token)
# if the token is used, a relay is turned on and off for 1 second
# the relay can energize a washer or dryer by just replacing the switch in the coon slider mechanism with circuit wired to relay
# the server, upon payment, will create token files that are replicated to the client via simple ftp commands
# replication is a simple polling process every 10 minutes (about 30MB per month, which can be had for about $10/month)
# when I tried push using Goodsync mediator, the data usage to keep connection alive was nearly 2GB per month. Polling can tear down connection after just a few milliseconds and this uses only 30MB per month.
# if the token file exists on server but not client, it is created in the client (directory above UsedTokens), thus available to a tenant to type in and activate laundry machine
# if the token file has been moved to UsedTokens, actions are repeatedly taken to inform the server of the token use until successful
#
#signals, to prevent early termination by tenant
# SIGKILL - cant avoid
# SIGTERM - can hook, but dont need to
# SIGINT - from keyboard, ctrl-C, should ignore
# SIGQUIT - from keyboard, ctrl-backslash, should ignore
# SIGTSTP - from keyboard, ctrl-Z, should ignore
# SIGHUP - from keyboard, ctrl-d, not sure

#exception EOFError
# Raised when one of the built-in functions (input() or raw_input()) hits an 
# end-of-file condition (EOF) without reading any data. (N.B.: the file.read() and file.readline() methods return an empty string when they hit EOF.)


#todo:
# no revocation yet 
# limit polling hours to 6am to 11pm

startupdir=''
quitnow=0

with open("laundry.py") as fp:
    for i, line in enumerate(fp):
        if "\xe2" in line:
            print i, repr(line)
    
def readserver(ftp):
    
    tokens = []
    ftp.retrlines('MLSD',tokens.append)
    server_tokens = []
    for line in tokens:
        if (line.split(";")[0]=="Type=file"):
            fn = line.split(";")[4][1:]
            if fn.endswith(".tok"):
                server_tokens.append( fn )
    ftp.cwd("UsedTokens")
    tokens=[]
    try:
        ftp.retrlines('MLSD', tokens.append)
    finally:
        ftp.cwd('..')
    server_used_tokens=[]
    for line in tokens:
        if (line.split(";")[0]=="Type=file"):
            server_used_tokens.append(line.split(";")[4][1:])
    
    print 'server_tokens:'
    print server_tokens
    print 'server_used_tokens'
    print server_used_tokens
    
    return server_tokens, server_used_tokens


def readlocal():
    print os.getcwd()
    local_tokens = [x for x in os.listdir('UnusedTokens') if x.endswith(".tok")]
    print 'local_unused'
    print local_tokens
    local_used = [x for x in os.listdir('UsedTokens') if x.endswith(".tok")]
    print 'local_used'
    print local_used
    return local_tokens, local_used
    
def transfertokens(ftp, st,su,lt,lu):
    print 'transfertokens ' + os.getcwd()
    for s in st:
        if not (s in lt) and not (s in lu) and not (s in su):
            print 'before create '+ s + ' in local unused '
            f= open('UnusedTokens/'+s,"w+")
            f.write(' ')
            f.close()
    for l in lu:
        print 'delete ' + l + ' in server tokens'
        try:
            ftp.delete(l)
        except:
            pass
        print 'create ' + l + ' in server used'
        f=open('UsedTokens/' + l,'r') # could be any small file
        try:
            ftp.storlines('STOR UsedTokens/' + l,f)
        finally:
            f.close()
        print 'delete ' + l + ' in local used'
        os.remove('UsedTokens/'+l)

def transfer_thread():
    global quitnow
    while quitnow==0:
        try:
            print "ftp connect"
            ftp = FTP(cred.SERVER)
            try:
                print "attempt login"
                ftp.login(cred.USER, cred.PASSWORD)
                print "logged in"
                st,su=readserver(ftp)
                print "readserver success"
                lt,lu=readlocal()
                print "readlocal succdss"
                transfertokens(ftp,st,su,lt,lu)
                print "transfer success"
            except:
                print 'ExceptioN caught ', sys.exc_info()
            finally:
                ftp.quit()
        except:
            print 'Exception caught ', sys.exc_info()

        for i in range(0,POLLSECONDS/5):
            print '*',
            time.sleep(5)
            if quitnow!=0:
                break
        
if __name__=="__main__":
    startupdir=os.getcwd()
    print startupdir

    signal.signal(signal.SIGINT,signal.SIG_IGN)
    signal.signal(signal.SIGQUIT,signal.SIG_IGN)

    transfer_thread()

