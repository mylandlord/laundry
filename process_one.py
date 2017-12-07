# event handler sink_char will call try_move when a token and machine selection is made
# ESC will clear input
# try_move will be called finally when all of a machine number or six chars are entered.
# token will rotate as new input comes in if longer than 6

import sys
import time
import os
import serial

def sink_char(ch):
    global token
    global machine
    global last_time
    
    print 'sink_char '+ ch + ' elapsed: ' + str(time.time()-last_time)
    
    if ch=='\x27' or ch=='*':
        token=''
        machine=''
    else:
        if time.time()-last_time > 30:
            token=''
            machine=''
            print "cleared token and machine"
        if ch=='\bs':
            if len(token) >= 1:
                token=token[:-1]
        elif ch=='1' or ch=='2':
            machine=ch
        elif ch.isalpha():
            if len(token)==6 and len(machine)==0:
                token=token[1:6]+ch
                print 'shift token :' + token
            else:
                token=token+ch
        if len(machine)==1 and len(token)==6:
            print "process_one calling try_move" + machine + token
            if token=="wpmwpm":
                sys.exit()
            try_move((machine+token).lower())
            token=''
            machine=''
    last_time=time.time()

def toggle_relay(m):
    ser.write(b"REL"+m+".ON"+chr(13)+chr(10))
    print ser.readline()
    print ser.readline()
    print ser.readline()
    print ser.readline()
    ser.write(b"REL"+m+".OFF"+chr(13)+chr(10))
    print ser.readline()
    print ser.readline()
    print ser.readline()
    print ser.readline()
    print 'switched'
    
# assume alpha numeric only, lower case only, first char is digit, following six are alpha
def try_move(a):
    global startupdir
    m=a[0:1]
    t=a[1:7]+'.tok'
    try:
        os.rename(startupdir+'/UnusedTokens/'+t,startupdir+'/UsedTokens/'+t)
        f=open(startupdir+'/UsedTokens/'+t,'a+')
        f.write(',' + time.strftime("%Y_%m_%d_%H_%M_%S"))
        f.close()
        try:
            toggle_relay(m)
        except:
            print "Reopen"
            ser.close()
            s="0"
            try:
                ser=serial.Serial("/dev/ttyACM"+s,timeout=1)
            except:
                s="1"
                ser=serial.Serial("/dev/ttyACM"+s,timeout=1)
    except:
        print 'not switched'


machine=''
token=''
last_time=time.time()
startupdir=os.getcwd()
s='0'
try:
    ser=serial.Serial("/dev/ttyACM"+s,timeout=1)
except:
    s="1"
    ser=serial.Serial("/dev/ttyACM"+s,timeout=1)

if __name__=='__main__':
    def try_move(s):
        if s=="2ghijkl":
            print "PASSED1"
        elif s=="1bcdefg":
            print "PASSED2"
        elif s=="3asdfgh":
            print "PASSED3"
        else:
            print "FAILED"
        
    sink_char('\bs')
    sink_char('a')
    sink_char('1')
    sink_char('b')
    sink_char('\x27')
    sink_char('g')
    sink_char('2')
    sink_char('h')
    sink_char('I')
    sink_char('\bs')
    sink_char('i')
    sink_char('j')
    sink_char('k')
    sink_char('l')

    sink_char('a')
    sink_char('b')
    sink_char('c')
    sink_char('d')
    sink_char('e')
    sink_char('f')
    sink_char('g')
    sink_char('1')
    
    sink_char('q')
    sink_char('w')
    
    time.sleep(31)
    sink_char('a')
    sink_char('s')
    sink_char('d')
    sink_char('f')
    sink_char('3')
    sink_char('g')
    sink_char('h')
    
