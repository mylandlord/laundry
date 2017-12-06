class dummy_serial:
    def readline(self):
        return 'dummy serial input'
    def write(self, s):
        print 'writing ' + s +' to dummy serial'

