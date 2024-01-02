HW = {
        'Display' : { 'mod' : 'DISP_Matrix8x8_max7219' , 'args' : { 'P_CS' : 17 , 'P_CLK' : 18 , 'P_MOSI' : 19 , 'BRIGHT' : 1 } } ,
#        'Display' : { 'mod' : 'DISP_mux8x7seg_DMAPIO' , 'args' : { 'P_MUX' : 6 , 'BRIGHT' : 1 } } ,
#        'Display' : { 'mod' : 'DISP_mux8x7seg_DMAPIO' , 'args' : { 'P_MUX' : 0 , 'BRIGHT' : 1 } } ,
#        'Display' : { 'mod' : 'DISP_SevenSeg_max7219' , 'args' : { 'P_CS' : 17 , 'P_CLK' : 18 , 'P_MOSI' : 19 , 'BRIGHT' : 1 } } ,
        'Sound' : { 'mod' : 'SND_PWMbuzzer' , 'args' : { 'P_APOWER' : 3, 'P_AOUT' : 4 } } ,
        'Enviro' : { 'mod' : 'ENV_DHT' , 'args' : { 'DHT_GPIO' : 5 } } ,
#        'Sound' : { 'mod' : 'SND_PWMbuzzer' , 'args' : { 'P_APOWER' : 22, 'P_AOUT' : 21 } } ,
#        'Enviro' : { 'mod' : 'ENV_DHT' , 'args' : { 'DHT_GPIO' : 20 } } ,
        'HID' : { 'mod' : 'HID_SingleButton' , 'args' : { 'pins' : [ 26 ] } } ,

        'Wlan' : { 'mod' : 'NET_WLAN' , 'args' : { } } ,

        'Alarms' : { 'mod' : 'ALM_GAPI' , 'args' : { 'calID' : 'primary' } } ,
        'View' : { 'mod' : 'VIEW_HodynyQ' , 'args' : { } } ,
        'Control' : { 'mod' : 'CON_HodynyQ' , 'args' : { 'daytime' : { 450:1, 1230:0 }, 'brightness' : [ 6, 0, 1, 15 ], 'almlimit' : 1800, 'almdefault' : True } } ,
        'Timezone' : { 'mod' : 'TZ_CET' , 'args' : {  } } ,

        '' : { 'mod' : '' , 'args' : { } }
    }
