import os
import sys




def do_printing(wirewire):
    os.system('python3 printing_path.py '+wirewire+' 3 Rbank Rbank2 random3 5 Pass')
    os.system('python3 printing_path.py '+wirewire+' 3 Rbank Rbank2 random3 0')
    return 0

if __name__ == "__main__":
    wirewire=sys.argv[1]
    do_printing(wirewire)