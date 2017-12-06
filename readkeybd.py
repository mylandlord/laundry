import os
import sys
import termios
import tty
import process_one

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

	
while 1:
    process_one.sink_char(str(getKey()))
    
