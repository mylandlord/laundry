# puts up a dialog to allow token input
# send chars one at a time to process_one

import ui
import process_one
import transfer_agent
import threading

class MyDelegate (object):
    def __init__(object):
        object.length=0
    def textview_did_change(self, textview):
        print self.length
        if (self.length > len(textview.text)):
            process_one.sink_char('\bs')
        else:
            process_one.sink_char(textview.text[-1:])
        self.length=len(textview.text)

if __name__=="__main__":
    textview = ui.TextView()
    textview.delegate = MyDelegate()
    textview.present('sheet')
    
        
    t=threading.Thread(target=transfer_agent.transfer_thread)
    t.start()

