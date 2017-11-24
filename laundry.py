# Author: William Morel, 2017

import sys
import os
import threading
import time
from ftplib import FTP
from cStringIO import StringIO
import cred

POLLSECONDS=10

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

#todo:
# no revocation yet 
# limit polling hours to 6am to 11pm
# merge with relay usb board commands

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
            server_tokens.append( line.split(";")[4][1:]) 
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
    local_tokens = [x for x in os.listdir('.') if x.endswith(".tok")]
    print 'local_unused'
    print local_tokens
    local_used = [x for x in os.listdir('UsedTokens') if x.endswith(".tok")]
    print 'local_used'
    print local_used
    return local_tokens, local_used
    
def keyboard_loop():
    global quitnow
    global startupdir
    print 'keyboard loop started ...'
    a = ''
    while (a != 'quit'):
        a=raw_input('enter the 2abcdef')
        a=filter(str.isalnum, a)
        print a
        if len(a)==7:
            m=a[0:1]
            t=a[1:7].lower()+'.tok'
            try:
                os.rename(startupdir+'/'+t,startupdir+'/UsedTokens/'+t)
                print 'switched'
            except:
                print 'not switched'
        else:
            print 'invalid'
    quitnow=1
            
def transfertokens(ftp, st,su,lt,lu):
    print 'transfertokens'
    for s in st:
        if not (s in lt) and not (s in lu) and not (s in su):
            print 'create ' + s + ' in local tokens'
            f= open(s,"w+")
            f.close()
    for l in lu:
        print 'delete ' + l + ' in server tokens'
        try:
            ftp.delete(l)
        except:
            pass
        print 'create ' + l + ' in server used'
        f=open('UsedTokens/'+l,'r') # could be any small file
        try:
            ftp.storlines('STOR UsedTokens/' + l,f)
        finally:
            f.close()
        print 'delete ' + l + ' in local used'
        os.remove('UsedTokens/'+l)
        
t=threading.Thread(target=keyboard_loop)
t.start()
startupdir=os.getcwd()
print startupdir
while quitnow==0:
    try:
        ftp = FTP(cred.SERVER)
        try:
            ftp.login(cred.USER, cred.PASSWORD)
            st,su=readserver(ftp)
            lt,lu=readlocal()
            transfertokens(ftp,st,su,lt,lu)
        except:
            print 'ExceptioN caught ', sys.exc_info()
        finally:
            ftp.quit()
    except:
        print 'Exception caught ', sys.exc_info()
    time.sleep(POLLSECONDS)
    
