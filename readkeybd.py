import os
import sys
import termios
import tty
import process_one
import signal

def getKey():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
	new[6][termios.VMIN] = 1
	new[6][termios.VTIME] = 0
	termios.tcsetattr(fd, termios.TCSANOW, new)
	key = None
	try:
		key = os.read(fd, 3)
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, old)
	return key

#signals, to prevent early termination by tenant
# SIGKILL - cant avoid
# SIGTERM - can hook, but dont need to
# SIGINT - from keyboard, ctrl-C, should ignore
# SIGQUIT - from keyboard, ctrl-backslash, should ignore
# SIGTSTP - from keyboard, ctrl-Z, should ignore
# SIGHUP - from keyboard, ctrl-d, not sure

signal.signal(signal.SIGINT, signal.SIG_IGN) # ctrl-C
signal.signal(signal.SIGQUIT, signal.SIG_IGN) # ctrl-backslash - not on windows
signal.signal(signal.SIGTSTP, signal.SIG_IGN) # ctrl-Z, SIGSTP not on pi
	
while 1:
    process_one.sink_char(str(getKey()))
    
