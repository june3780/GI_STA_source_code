import os
import sys




def do_printing(wirewire,checking):

    checkinglist=checking
    os.system('python3 printing_path.py '+wirewire+' '+str(1)+' '+checkinglist+' 5 Pass')
    os.system('python3 printing_path.py '+wirewire+' '+str(1)+' '+checkinglist+' 0')

    return 0

if __name__ == "__main__":
    wirewire=sys.argv[1]
    checking1=sys.argv[2]
    do_printing(wirewire,checking1)