import os
import sys




def do_printing(wirewire):

    checkinglist="a1_bank a1_rbank a2_bank a2_rbank bank rbank random Rbank random3 Rbank2 Random Random2"
    number=len(checkinglist.split(' '))
    os.system('python3 printing_path.py '+wirewire+' '+str(number)+' '+checkinglist+' 5 Pass')
    os.system('python3 printing_path.py '+wirewire+' '+str(number)+' '+checkinglist+' 0')
    print(number)

    return 0

if __name__ == "__main__":
    wirewire=sys.argv[1]
    do_printing(wirewire)