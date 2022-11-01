import os
import sys
import time 
# #Replace in a folder 
LEFfile = sys.argv[1]
folder_def = sys.argv[2]

if ".def" in folder_def: # single DEF file
    output = "hpwl_result_random0"
    def_file = folder_def
    script = "read_lef " + LEFfile +"\n\n"
    script = script + "read_def " + def_file +"\n\n"
    script = script + "global_placement -skip_initial_place \n\n"
    script = script + "detailed_placement\n\n"
    new_def_file = def_file.replace(".def", "_detailed.def \n\n").strip()
    script = script + "write_def " + new_def_file +" \n\n"
    script = script + "exit"
    file = open("input", "w")
    file.write(script)
    file.close()
    os.system("/data1/OpenROAD/build/src/openroad < input")
    txt_file = new_def_file.replace("_detailed.def", "_detailed.txt").strip()
    os.system("python3 /data1/PNR/util/convert_def_to_txt.py "+ new_def_file + " "+ txt_file)
    problem_file = "/data1/GI-chip/data/problem_7809.json"
    os.system("/data1/GI-chip/build/bin/HPWL " + problem_file + " " + txt_file + " > " + output)
    outputfile = open(output, "r")
    newfile = ""
    for line in outputfile:
        new_line = txt_file.split("/")[-1].strip() + " " + line
        newfile = newfile + new_line
        break
    outputfile.close()
    file = open(output+".txt", "w")
    file.write(newfile)


else:
    output = "hpwl_result_a1_bank"  
    def_file_list = [file for file in os.listdir(folder_def) if ".def" in file]
    for file in def_file_list:
        txt_file = file.replace(".def", "_convert.txt")
        os.system("python3 convert_def_to_txt.py "+ folder_def+"/" + file + " "+ folder_def+"/" + txt_file)
        problem_file = "/home/june/Documents/GI-chip/data/problem_7809.json"
        print("/home/june/Documents/GI-chip/build/bin/HPWL " + problem_file + " " + folder_def+"/"+ txt_file + " > " + output)
        os.system("/home/june/Documents/GI-chip/build/bin/HPWL " + problem_file + " " + folder_def+"/"+ txt_file + " > " + output)
        outputfile = open(output, "r")
        newfile = ""
        for line in outputfile:
            new_line = txt_file.strip() + " " + line
            newfile = newfile + new_line
            print(newfile)
            break
        outputfile.close()
        file = open(output+".txt", "a")
        file.write(newfile)
        file.close()

    


 

