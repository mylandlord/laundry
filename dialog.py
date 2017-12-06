# puts up a dialog to allow token input
# send chars one at a time to process_one

#You basically just have to create an instance of your delegate class and then assign that to the delegate attribute of your text view. Here's an #example without using the UI editor:

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
    
        
    t=threading.Thread(target=laundry.transfer_thread)
    t.start()

