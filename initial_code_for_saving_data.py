import os
import sys




def do_printing(wirewire):

    checkinglist="Rbank Rbank2 random3 Random"
    
    number=len(checkinglist.split(' '))
    os.system('python3 printing_path.py '+wirewire+' '+str(number)+' '+checkinglist+' 5 Pass')
    os.system('python3 printing_path.py '+wirewire+' '+str(number)+' '+checkinglist+' 0')

    return 0

if __name__ == "__main__":
    wirewire=sys.argv[1]
    do_printing(wirewire)