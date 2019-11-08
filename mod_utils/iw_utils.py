import os
import sys

def isCron():
    if len(sys.argv) == 2:
        if(sys.argv[1] == '--cron'):
            return True
    return False

def getCWD():
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    return path  

# Custom Error handler. This function will display the error message
# on the e-ink display and exit. 
def HandleError(msg):
    print "ERROR IN PROGRAM ======================================"
    print "Program requires user input. Please run from console"
    print "ERR: " + msg
    print "END ERROR ============================================="
    quit()