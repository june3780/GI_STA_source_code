import json


wire_load='wire_load'
capacitance='capacitance'
resistance='resistance'
slope='slope'
fanout_length1='fanout_length1'
fanout_length2='fanout_length2'
fanout_length3='fanout_length3'
fanout_length4='fanout_length4'
fanout_length5='fanout_length5'
fanout_length6='fanout_length6'
fanout_length7='fanout_length7'
fanout_length8='fanout_length8'
fanout_length9='fanout_length9'
fanout_length10='fanout_length10'
fanout_length11='fanout_length11'




wire_load_model=[{'wire_load':"1K_hvratio_1_4", \
'capacitance':1.774000e-01,   \
'resistance':3.571429e-03,    \
'slope':5.000000,    \
'fanout_length1':1.3207,    \
'fanout_length2':2.9813,    \
'fanout_length3':5.1135,    \
'fanout_length4':7.6639,    \
'fanout_length5':10.0334,    \
'fanout_length6':12.2296,    \
'fanout_length8':19.3185    \
}, {wire_load:"1K_hvratio_1_2",
capacitance : 1.774000e-01,
resistance : 3.571429e-03,
slope : 5.000000,
fanout_length1:1.3216,
fanout_length2:2.8855,
fanout_length3:4.6810,
fanout_length4:6.7976,
fanout_length5:9.4037,
fanout_length6:13.0170,
fanout_length8:24.1720
}, {wire_load:"1K_hvratio_1_1",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 6.283688,
    fanout_length1:1.3446,
    fanout_length2:2.8263,
    fanout_length3:4.7581,
    fanout_length4:7.4080,
    fanout_length5:10.9381,
    fanout_length6:15.7314,
    fanout_length8:29.7891
  },  {wire_load:"3K_hvratio_1_4",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1:1.8234,
    fanout_length2:4.5256,
    fanout_length3:7.5342,
    fanout_length4:10.6237,
    fanout_length5:13.5401,
    fanout_length6:16.3750,
    fanout_length7:18.6686,
    fanout_length8:19.4348,
    fanout_length10:20.9672
  }, {wire_load:"3K_hvratio_1_2",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1:1.6615,
    fanout_length2:3.9827,
    fanout_length3:6.6386,
    fanout_length4:9.6287,
    fanout_length5:12.8485,
    fanout_length6:16.4145,
    fanout_length7:20.0747,
    fanout_length8:22.6325,
    fanout_length10:21.7173
  }, {wire_load:"3K_hvratio_1_1",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1:1.5771,
    fanout_length2:3.9330,
    fanout_length3:6.6217,
    fanout_length4:9.7638,
    fanout_length5:13.5526,
    fanout_length6:18.1322,
    fanout_length7:22.5871,
    fanout_length8:25.1074,
    fanout_length10: 30.1480
  }, {wire_load:"5K_hvratio_1_4",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1: 2.0449,
    fanout_length2: 4.4094,
    fanout_length3: 7.2134,
    fanout_length4: 10.4927,
    fanout_length5: 13.9420,
    fanout_length6: 18.0039,
    fanout_length7: 23.9278,
    fanout_length8: 30.8475,
    fanout_length9: 34.9441,
    fanout_length11: 43.1373
  }, {wire_load:"5K_hvratio_1_2",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1: 1.6706,
    fanout_length2: 3.7951,
    fanout_length3: 6.2856,
    fanout_length4: 9.1309,
    fanout_length5: 12.1420,
    fanout_length6: 15.6918,
    fanout_length7: 20.1043,
    fanout_length8: 24.2827,
    fanout_length9: 27.3445,
    fanout_length11: 35.3421
  }, {wire_load:"default_wire_load : 5K_hvratio_1_1",
    capacitance : 1.774000e-01,
    resistance : 3.571429e-03,
    slope : 5.000000,
    fanout_length1: 1.7460,
    fanout_length2: 3.9394,
    fanout_length3: 6.4626,
    fanout_length4: 9.2201,
    fanout_length5: 11.9123,
    fanout_length6: 14.8358,
    fanout_length7: 18.6155,
    fanout_length8: 22.6727,
    fanout_length9: 25.4842,
    fanout_length11: 27.0320
  }



]

print(json.dumps(wire_load_model,indent=4))

with open ('../data/OPENSTA/wire_load_model_openSTA.json','w') as f:
    json.dump(wire_load_model,f ,indent=4)



