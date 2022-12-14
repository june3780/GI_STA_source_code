#!/usr/bin/env python
import sys
import datetime
import operator
import math 
from collections import OrderedDict

def checkversion():
    #refuse the used python version from the beginning
    if (sys.version_info > (3, 0)):
        print('The Program doesnt support Python 3')
        exit(1)

def resistanceCalculation(RPERSQ, L, W):
    return RPERSQ*L/W

def capacitanceCalculation(CPERSQDIST, L, W, EDGECAPACITANCE):
    return CPERSQDIST*L*W+EDGECAPACITANCE*L


#function responsible for the actual parsing and generation of spef
def generateSpef(deffile, leffile, libfile,speffile):
    checkversion()
    cell_pins={}   #dictionary to containg cell name with its associated pins properties (i.e. capacitance or direction)
    flag_inside_pin=0
    #----
    ports_direction={} #dictionary containing the port directions
    flag = False
    components = {}
    nets  = {}
    case = 0
    name_maps_dict = {}
    cnt = 1
    metal_layers = {} # 0: resistance per square, 1: width, 2: capacitance per square, 3: edge capacitance
    flag_inside_layer = 0
    flag_inside_via = 0
    layer_name = ""  
    temp_via_name = ""
    via_resistance = {}
    params = []
    temp_string = ""
    pins_layer = {} #pin: cap
    comp_coordinates={}
    route_cordinates={}
    cell_pin_per_net={}
    pin_coordinates={}
    #---
    with open(leffile,'r') as lef:
        for line in lef:
            try:
                # if key doesnt exist print(metal_layers.get("hi") == None)
                line_split = line.split()
                first_word=line_split[0]
                first_word_uppercase = first_word.upper()
                second_word=line_split[1]
                if(first_word_uppercase == 'LAYER'):
                    flag_inside_layer = 1
                    layer_name = second_word
                elif(first_word_uppercase == 'VIA'):
                    flag_inside_via = 1
                    temp_via_name = second_word
                elif(first_word_uppercase == 'END' and second_word == layer_name):
                    flag_inside_layer = 0
                    flag_inside_via = 0
                    params = []
                if(flag_inside_via):
                    if(first_word_uppercase == 'LAYER' and 'VIA' in second_word.upper()):
                        #print(second_word)
                        if(metal_layers.get(second_word) != None):
                            via_resistance[temp_via_name] = metal_layers[second_word][0]
                elif(flag_inside_layer):
                    #print(layer_name)
                    if(first_word_uppercase == 'WIDTH'):
                        if(metal_layers.get(layer_name) == None):
                            withe = second_word+"e-6"
                            params.insert(1, float(withe))
                    if(first_word_uppercase == 'EDGECAPACITANCE'):
                        withe = float(second_word) 
                        withe = withe * 1e-6
                        params.insert(3, withe)
                    if(first_word_uppercase == 'CAPACITANCE'):
                        params.insert(2, float(line.split()[2]))
                    if(first_word_uppercase == 'RESISTANCE'):
                        if(second_word == "RPERSQ"):
                            params.insert(0, float(line.split()[2]))
                        else:
                            params.insert(0, float(line.split()[1]))
                        metal_layers[layer_name] = params
            except:
                pass

    #read cell_names and save ports names with their direction from lib file
    with open(libfile,'r') as libf:
        for line in libf:
            try:
                first_word=line.split()[0]
                if(flag_inside_pin):
                    #then insied specific pin in the cell
                    if first_word=='direction':
                        try:
                            direction=line.split()[2].lower()   #third word usually
                            if(';'in direction):
                                direction=direction.split(';')[0]
                            if direction=='input':
                                cell_pins[cell_name][pin_name].append('I')
                            else:
                                cell_pins[cell_name][pin_name].append('O')
                        except:
                            pass
                    if first_word=='capacitance':
                        try:
                            capacitance=line.split()[2]   #third word usually
                            if(';'in capacitance):
                                capacitance=capacitance.split(';')[0]
                            cell_pins[cell_name][pin_name].append(capacitance)
                            flag_inside_pin=0
                        except:
                            pass
                #or inside the cell but didnt find the pin yet
                elif('pin' in first_word and '('in line and ')' in line):
                    try:
                        pin_name=line[line.find("(")+1:line.find(")")]
                        cell_pins[cell_name][pin_name]=[] #add new cell into our dictionary
                        flag_inside_pin=1
                    except:
                        print('expected pin (pin_name) inside lib file')
                        exit(1)
                if(first_word=='cell'):
                    #then inside a cell
                    flag_inside_pin=0
                    try:
                        cell_name = line[line.find("(")+1:line.find(")")]
                        cell_pins[cell_name]={} #add new cell into our dictionary
                    except:
                        print('expected cell(cell_name) inside lib file')
                        exit(1)
            except:
                pass

    flag_in_nets_section=0  #used to determine whether the current section is nets section
    flag_inside_connection_net=0  #used to determine wthether we are inside a specific net
    nets_section_string=""  #we shall add this to string_to_write when writing to our beloved file
    flag_routed_section=0
    current_metal_layer=""
    current_route_line=""
    current_route = {}
    nets_routes = {}
    capacitance_per_net = {}
    current_net = ""
    total_cap = 0
    temp_index = 1
    tempPinName=""
    cell_with_pin_per_net={}
    couns=0
    temp_coordinates = {}
    metal_layers_res = []
    #start reading from the def file and get what we need
    with open(deffile, 'r') as df:
        for line in df:
            try:
                #-----------------------
                current_route_line = line.split()               
                if( case == 0 ):
                    try:
                        first = line.split()[0]
                        second = line.split()[1]
                        if( first == "COMPONENTS" ) :
                            case = 1 
                        if ( first == "NETS" ) :
                            case = 2 
                        if ( first == "PINS" ) :
                            case = 3
                    except:
                        pass
                # inside a case
                else:
                    try:
                        first = line.split()[0]
                        second = line.split()[1]
                        if( first == "END"):
                            case = 0 
                            if("COMPONENTS" in second):
                                for key , value in components.items() :
                                    name_maps_dict[key] = cnt
                                    cnt+=1
                            if("NETS" in second):
                                for key , value in nets.items() :
                                    name_maps_dict[key] = cnt
                                    cnt+=1
                        else:
                            if( case == 1 ):
                                couns=couns+1
                                components[second] = "+"
                                current_comp=second
                                x_cord=line.split()[6]
                                y_cord=line.split()[7]
                                comp_coordinates[current_comp]=[]
                                comp_coordinates[current_comp].append(x_cord)
                                comp_coordinates[current_comp].append(y_cord)

                            if( case == 2 and first == '-' ) :
                                nets[second] = "+"
                                current_net = second
                                cell_with_pin_per_net[current_net]={}
                                        
                            if(case == 2 and not flag_routed_section):
                                if(first == "+"):
                                    current_metal_layer = current_route_line[2]
                                    #print current_metal_layer
                                    flag_routed_section = 1
                                elif(first == "("):
                                    if(second != "PIN"):
                                        #print line.split()[1]
                                        try:
                                            dummy=cell_pin_per_net[current_net][0]
                                        except:
                                            cell_pin_per_net[current_net]=[]

                                        cell_pin_per_net[current_net].append(line.split()[1])
                                        cell_with_pin_per_net[current_net][line.split()[1]] = line.split()[2]
                                        total_cap = total_cap + float(cell_pins[second.split('_')[0]][line.split()[2]][1])*1e-12
                                    else:
                                        try:
                                            dummy=cell_pin_per_net[current_net][0]
                                        except:
                                            cell_pin_per_net[current_net]=[]
                                        cell_pin_per_net[current_net].append(line.split()[2])
                                        total_cap = total_cap + capacitanceCalculation(metal_layers[pins_layer[line.split()[2]]][2], 1e-6, 1e-6, metal_layers[pins_layer[line.split()[2]]][3])
                            if(case == 2 and flag_routed_section):
                                if(current_route_line[current_route_line.__len__()-1] == ";" or second == "USE"): 
                                    nets_routes[current_net] = current_route
                                    flag_routed_section = 0

                                #flag routed = 0 when ;
                                if(first.upper() == "NEW"):
                                    current_metal_layer = current_route_line[1]
                                x_1 = ""
                                y_1 = ""
                                x_2 = ""
                                y_2 = ""
                                cur_cap = 0

                                for i, word in enumerate(current_route_line):
                                    if(word == "("):
                                        if(current_route_line[i-1] == current_metal_layer):
                                            x_1 = current_route_line[i+1]
                                            y_1 = current_route_line[i+2]
                                            #if these coordinates match any cell == pin1
                                        elif (current_route_line[i-1] == ")"):
                                            x_2 = x_1 if(current_route_line[i+1] == "*") else current_route_line[i+1]
                                            y_2 = y_1 if(current_route_line[i+2] == "*") else current_route_line[i+2]
                                            try:
                                                dummy=route_cordinates[current_net][0]
                                            except:
                                                route_cordinates[current_net]=[]
                                                temp_coordinates[current_net]=[]
                                            route_cordinates[current_net].append(x_1)
                                            route_cordinates[current_net].append(y_1)
                                            route_cordinates[current_net].append(x_2)
                                            route_cordinates[current_net].append(y_2)
                                            temp_coordinates[current_net].append(x_1)
                                            temp_coordinates[current_net].append(y_1)
                                            temp_coordinates[current_net].append(x_2)
                                            temp_coordinates[current_net].append(y_2)
                                            metal_layers_res.append(current_metal_layer)
                                            #check the pin coordiates for pin 2
                                            dist_x = abs(int(x_1)-int(x_2))*1e-6
                                            dist_y = abs(int(y_1)-int(y_2))*1e-6
                                            wire_len = dist_y if(dist_x==0) else dist_x
                                            wire_len = wire_len + (metal_layers[current_metal_layer][1]/2)
                                            temp = metal_layers[current_metal_layer]
                                            #------------------------- CAPACITANCE ----------------------------------
                                            cur_cap = capacitanceCalculation(temp[2], wire_len, temp[1], temp[3])
                                            total_cap = total_cap + cur_cap
                                            if(current_route.get(current_metal_layer) == None):
                                                current_route[current_metal_layer] = [wire_len]
                                            else:
                                                current_route[current_metal_layer].append(wire_len)

                                            #------------------------- RESISTANCE -----------------------------------
                                if(flag_routed_section == 0):
                                    total_cap = total_cap * (1e+15) #capacitance in p, so p or f??
                                    capacitance_per_net[current_net] = total_cap
                                    total_cap = 0
                                    nets_routes[current_net] = current_route
                                    current_route = {}
                                    
                            if( case == 3 ):
                                if(first == "-"):
                                    tempPinName = second
                                if(first == "+" and second == "LAYER"):
                                    pins_layer[tempPinName] = line.split()[2]
                                if(first == "+" and second == "PLACED"):
                                    pin_coordinates[tempPinName] = [line.split()[3], line.split()[4]]


                    except:
                        pass
                #-------------------

            except:
                pass
    #print cell_pin_per_net['out223']
    currentNet = ""
    with open(deffile, 'r') as df:
        for line in df:
            try:
                first_word= line.split()[0]
                #get design name
                if(first_word=='DESIGN'):
                    try:
                        design_name=line.split()[1]
                    except:
                        pass
                #get DIVIDERCHAR
                if(first_word=='DIVIDERCHAR'):
                    try:
                        DIVIDERCHAR=line.split()[1][1:-1]
                    except:
                        pass
                #get BUSBITCHARS
                if(first_word=='BUSBITCHARS'):
                    try:
                        BUSBITCHAR=line.split()[1][1:-1]
                    except:
                        pass
                #get the nets section here
                if(first_word=='END'):
                    #done with nets section
                    try:
                        second_word=line.split()[1]
                        if(second_word =='NETS'):
                            flag_in_nets_section=0
                            flag_inside_connection_net=0
                    except:
                        pass
                #(TODO: some def files dont have direction in pins section)
                second_word=line.split()[1]
                if (first_word=="PINS"):
                     flag = True
                elif (first_word == "END" and second_word == "PINS"): # the pins section ended
                     flag = False
                #---------------
                if(flag_in_nets_section and flag_inside_connection_net):
                    #we get here to get conenctions for current net
                    try:
                        #know is it a port or internal connection
                        if ';' in line.split():
                            #we are done with this net
                            for k in nets_routes[currentNet]:
                                for v in (nets_routes[currentNet][k]):
                                    nets_section_string+= "*N *" + str(name_maps_dict[currentNet]) + ":"+str(temp_index)+" *C\n"
                                    temp_index = temp_index+1
                            temp_index = 1

                            flag_inside_connection_net=0
                            #--------------- CAPACITANCE -----------------------------------
                            nets_section_string+="\n*CAP\n"
                            index = 1
                            while(temp_string.__len__() > 0):
                                toadd = str(index) + " " + temp_string[0:temp_string.index('\n')+1]
                                nets_section_string+=toadd
                                index = index + 1
                                temp_string = temp_string[temp_string.index('\n')+1:]
                            
                            for k in nets_routes[currentNet]:
                                for v in (nets_routes[currentNet][k]):
                                    temp = capacitanceCalculation(metal_layers[k][2], v, metal_layers[k][1], metal_layers[k][3]) *(1e+15)
                                    nets_section_string+= str(index) + " *" + str(name_maps_dict[currentNet]) + ":"+str(index)+" "+str(temp)+"\n"
                                    index = index+1
                            #--------------- RESISTANCE -----------------------------------
                            #create a difference list for each net
                            #print cell_pin_per_net['in50']
                            for componentindex in cell_pin_per_net[currentNet]:
                                diff=[]
                                iter=0
                                num_of_cordinates=len(route_cordinates[currentNet])
                                if(componentindex in comp_coordinates):
                                    for iter in range(0,num_of_cordinates,2):
                                        diff.append(math.sqrt((float(comp_coordinates[componentindex][0])-\
                                            float(temp_coordinates[currentNet][iter]))**2+\
                                            (float(comp_coordinates[componentindex][1])-\
                                            float(temp_coordinates[currentNet][iter+1]))**2))
                                    mini=min(diff)
                                    for i, x in enumerate(diff):
                                        if x == mini:
                                            temp_coordinates[currentNet][2*int(i)] = '9e9'
                                            temp_coordinates[currentNet][2*int(i)+1] = '9e9'
                                            route_cordinates[currentNet][2*int(i)]=str(comp_coordinates[componentindex][0])
                                            route_cordinates[currentNet][2*int(i)+1]=str(comp_coordinates[componentindex][1])
                                else:
                                    for iter in range(0,num_of_cordinates,2):
                                        diff.append(math.sqrt((float(pin_coordinates[componentindex][0])-\
                                            float(temp_coordinates[currentNet][iter]))**2+\
                                            (float(pin_coordinates[componentindex][1])-\
                                            float(temp_coordinates[currentNet][iter+1]))**2))
                                    mini=min(diff)
                                    #print diff
                                    for i, x in enumerate(diff):
                                        if x == mini:
                                            temp_coordinates[currentNet][2*int(i)] = '9e9'
                                            temp_coordinates[currentNet][2*int(i)+1] = '9e9'
                                            route_cordinates[currentNet][2*int(i)]=str(pin_coordinates[componentindex][0])
                                            route_cordinates[currentNet][2*int(i)+1]=str(pin_coordinates[componentindex][1])

                            wire_coordinates = {}
                            #print(wire_coordinates)
                            index = len(cell_pin_per_net[currentNet])+1
                            for i in range(0,len(temp_coordinates[currentNet]),2):
                                x = temp_coordinates[currentNet][i]
                                y = temp_coordinates[currentNet][i+1]
                                if(x != "9e9" and wire_coordinates.get(x) == None):
                                    wire_coordinates[x] = {}
                                    wire_coordinates[x][y] = str(index)
                                    index = index + 1
                                elif(x != "9e9" and wire_coordinates[x].get(y) == None):
                                    wire_coordinates[x] = {}
                                    wire_coordinates[x][y] = str(index)
                                    index = index + 1
                            #--------------- RESISTANCE -----------------------------------

                            nets_section_string+="\n*RES\n"
                            index = 1
                            z = 0
                            for i in route_cordinates[currentNet]:
                                x_1 = ""
                                y_1 = ""
                                x_2 = ""
                                y_2 = ""
                                pin_1= []
                                pin_2= []
                                x_1 = route_cordinates[currentNet][z]
                                y_1 = route_cordinates[currentNet][z+1]
                                x_2 = route_cordinates[currentNet][z+2]
                                y_2 = route_cordinates[currentNet][z+3]
                                
                                if(wire_coordinates.get(x_1) != None):
                                    if(wire_coordinates[x_1].get(y_1) != None):
                                        wire_1 = wire_coordinates[x_1][y_1]
                                if(wire_coordinates.get(x_2) != None):
                                    if(wire_coordinates[x_2].get(y_2) != None):
                                        wire_2 = wire_coordinates[x_2][y_2]
        
                                for m in cell_pin_per_net[currentNet]:
                                    if(comp_coordinates.get(m) != None):
                                        if(comp_coordinates[m][0] == x_1 and comp_coordinates[m][1] == y_1):
                                            pin_1 = [m, 1]
                                        elif(comp_coordinates[m][0] == x_2 and comp_coordinates[m][1] == y_2):
                                            pin_2 = [m, 1]
                                    if(pin_coordinates.get(m) != None):
                                        if(pin_coordinates[m][0] == x_1 and pin_coordinates[m][1] == y_1):
                                            pin_1 = [m, 0]
                                        elif(pin_coordinates[m][0] == x_2 and pin_coordinates[m][1] == y_2):
                                            pin_2 = [m, 0]

                                dist_x = abs(int(x_1)-int(x_2))*1e-6
                                dist_y = abs(int(y_1)-int(y_2))*1e-6
                                wire_len = dist_y if(dist_x==0) else dist_x
                                z_4 = z-4
                                z = z+4
                                if(wire_len != 0):
                                    wire_len = wire_len + (metal_layers[metal_layers_res[z_4]][1]/2)
                                    res = resistanceCalculation(metal_layers[metal_layers_res[z_4]][0], wire_len, metal_layers[metal_layers_res[z_4]][1])
                                    #loop over components per net
                                    if(pin_1.__len__() > 0 and pin_2.__len__() > 0):
                                        if(pin_1[1] == 1 and pin_2[1] == 1):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) + ":"+str(cell_with_pin_per_net[currentNet][pin_1[0]])
                                            nets_section_string+= " *" + str(name_maps_dict[pin_2[0]]) + ":"+str(cell_with_pin_per_net[currentNet][pin_2[0]])
                                            nets_section_string+=" " + str(res) +"\n"
                                        if(pin_1[1] == 1 and pin_2[1] == 0):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) + ":"+cell_with_pin_per_net[currentNet][pin_1[0]]+\
                                                " *" + str(name_maps_dict[pin_2[0]]) + " " + str(res) +"\n"
                                        if(pin_1[1] == 0 and pin_2[1] == 1):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) +" *" +\
                                                 str(name_maps_dict[pin_2[0]]) + ":"+str(cell_with_pin_per_net[currentNet][pin_2[0]])+\
                                                    " " + str(res) +"\n"
                                        if(pin_1[1] == 0 and pin_2[1] == 0):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) + " *" +\
                                                 str(name_maps_dict[pin_2[0]]) + " " + str(res) +"\n"

                                    elif(pin_1.__len__() > 0):
                                        if(pin_1[1] == 1):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) + ":"+cell_with_pin_per_net[currentNet][pin_1[0]]+\
                                                " *" + str(name_maps_dict[currentNet]) + ":"+ str(wire_2) +\
                                                    " " + str(res) +"\n"
                                        if(pin_1[1] == 0):
                                            nets_section_string+= str(index) + " *" + str(name_maps_dict[pin_1[0]]) +" *" +\
                                                 str(name_maps_dict[currentNet]) + ":"+str(wire_2)+ " " + str(res) +"\n"
                                    elif(pin_2.__len__() > 0):
                                        if(pin_2[1] == 1):
                                            nets_section_string+= str(index) +  " *" + str(name_maps_dict[currentNet]) + ":"+ str(wire_1) +\
                                                " *" + str(name_maps_dict[pin_2[0]]) + ":"+cell_with_pin_per_net[currentNet][pin_2[0]]+\
                                                 " " + str(res) +"\n"
                                        if(pin_2[1] == 0):
                                            nets_section_string+= str(index) +  " *" + str(name_maps_dict[currentNet]) + ":"+ str(wire_1) +\
                                                " *" + str(name_maps_dict[currentNet])+\
                                                    " " + str(res) +"\n"
                                    else:
                                        nets_section_string+= str(index) +  " *" + str(name_maps_dict[currentNet]) + ":"+ str(wire_1) +\
                                                " *" + str(name_maps_dict[currentNet]) + ":"+str(wire_2)+\
                                                    " " + str(res) +"\n"
                                    index = index+1


                        if 'PIN' in line.split():
                            cell_name_index=line.split().index('PIN')
                            pin_name=line.split()[cell_name_index+1]
                            temp_index = temp_index+1
                            nets_section_string+="*P *"+str(name_maps_dict[pin_name])+" "+\
                                ports_direction[pin_name]+"\n"
                            temp_string+="*"+str(name_maps_dict[pin_name])+ " "+\
                                        str(capacitanceCalculation(metal_layers[pins_layer[pin_name]][2], 1e-6, 1e-6, metal_layers[pins_layer[pin_name]][3])*1e+15)+"\n"
                        elif '(' in line.split():
                            #get the location of '(' if it exists
                            cell_name=line.split()[line.split().index('(')+1]
                            pin_name= line.split()[line.split().index('(')+2]
                            nets_section_string+="*I *"+str(name_maps_dict[cell_name])+":"+pin_name+" "
                            temp_string+= "*"+str(name_maps_dict[cell_name])+":"+pin_name + " " + str(float(cell_pins[cell_name.split('_')[0]][pin_name][1])*1e+3)+"\n"
                            direction=cell_pins[cell_name.split('_')[0]][pin_name][0]
                            if direction== 'I':
                                #then get capacitance of input pin
                                temp_index = temp_index+1
                                capacitance=float(cell_pins[cell_name.split('_')[0]][pin_name][1])*1e+3
                                #capacitance=cell_pins[cell_name.split('_')[0]][pin_name][1]
                                nets_section_string+=direction+" *L "+str(capacitance)+"\n"
                            else:
                                #get the name only
                                #we add the TYPE not the actual name mapping after *D
                                nets_section_string+=direction+" *D "+ str(cell_name.split('_')[0])+"\n"
                                temp_index = temp_index+1
                                #nets_section_string+=direction+" *D *"+ str(name_maps_dict[cell_name])+"\n"
                    except:
                        pass
                elif(flag_in_nets_section and not flag_inside_connection_net):
                    #we get here only to get the current net name
                    try:
                        second_word=line.split()[1]
                        if(first_word == "-"):
                            currentNet = second_word #netname
                            nets_section_string+="\n*END\n\n"
                            nets_section_string+="*D_NET *"+str(name_maps_dict[currentNet])+" "+str(capacitance_per_net[currentNet])+\
                                "\n\n*CONN\n"
                            flag_inside_connection_net=1
                    except:
                        pass                                

                if(first_word=='NETS'):
                    flag_in_nets_section=1
                    flag_inside_connection_net=0

                #(TODO: the ones written in the ports section in spef is the top level ports only so metal4 only?)
                if flag: # while we are in the pins section
                    if "NET" in line.split():
                        for word in line.split():
                            if "-" in word:
                                try:
                                    dash_index = line.split().index('-')
                                    portword=line.split()[dash_index+1]  #to save the whole port name
                                except:
                                    pass
                            word = word.upper()
                            if "IN" in word or "OUT" in word: #common direction indicator
                                try:
                                    savchar2=word[0] # SAVE DIRECTION
                                    ports_direction[portword]=savchar2
                                except:
                                    pass
                            if "GND" in word or "VDD" in word: #special ports that don't specify direction (external)
                                try:
                                    savchar2= 'I' # SAVE DIRECTION
                                    ports_direction[portword]=savchar2
                                except:
                                    pass

                #-----------------------------------------
            except:
                pass

    #print cell_pins
    #write to the SPEF file
    #we first prepare a list with all the lines we want to inset then we open the file and insert all at once
    all_words=[]
    #print route_cordinates['in17']
    #print cell_pin_per_net['in17']

    #print nets_routes['_0_']
    #print metal_layers
    #Header Section : header_def
    currenttime= datetime.datetime.now()
    string_to_write='*SPEF "IEEE 1481-2009"\n*DESIGN "'+design_name+'"\n*DATE "'+str(currenttime)+'"\n*VENDOR "AUC_STUDENTS"'+\
        '\n*PROGRAM "Def2Spef_Converter"\n*VERSION "0.0"\n*DESIGN_FLOW "PROJECT2_FLOW"\n*DIVIDER '+DIVIDERCHAR+'\n*DELIMITER :\n*BUS_DELIMITER'+\
                    ' '+BUSBITCHAR+'\n*T_UNIT 1 PS\n*C_UNIT 1 FF\n*R_UNIT 1 KOHM\n*L_UNIT 1 UH\n'
    all_words.append(string_to_write)


    #Name map definition : [name_map]
    string_to_write="*NAME_MAP\n"
    all_words.append(string_to_write)
    sorted_names = OrderedDict(sorted(name_maps_dict.items(), key=lambda x: x[1]))
    for key, value in sorted_names.items():
        string_to_write = "*"+str(value) + " "+ key
        all_words.append(string_to_write)

    #Power & Ground Nets definition : [power_def]

    #External definition : [external_def]
    string_to_write="\n*PORTS"
    all_words.append(string_to_write)
    count = 1
    for portnames in ports_direction.keys():
        #string_to_write="*"+str(portnames)+" "+ports_direction[portnames]
        string_to_write="*"+str(count)+" "+ports_direction[portnames]
        all_words.append(string_to_write)
        count+=1
    all_words.append('')    #just to add newline


    #Internal definition : internal_def
    string_to_write=nets_section_string
    all_words.append(string_to_write)

    #write everything here
    with open(speffile, 'w') as f:
        for i in all_words:
            f.write(i+'\n')

def main():

    #get the argumnents from CLI
    if len(sys.argv) <5 and len(sys.argv)>=1:
        if(len(sys.argv) ==1):
            print('usage is python def2spef [deffile] [libraryfile] [leffile] [speffile]\ndef2spef -help for additional options')
            exit(1)
        elif(sys.argv[1]=='-help'):
            print('usage is python def2spef [deffile] [libraryfile] [leffile] [speffile]')
            exit(0)
        else:
            print('usage is python def2spef [deffile] [libraryfile] [leffile] [speffile]\ndef2spef -help for additional options')
            exit(1)

    deffile=sys.argv[1]
    libfile=sys.argv[2]
    leffile=sys.argv[3]
    speffile=sys.argv[4]
    generateSpef(deffile,leffile,libfile,speffile)


if __name__== "__main__":
    main()