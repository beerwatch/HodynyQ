# save your actual configuration in hodynyk_cfg.py file
WL_SSID = 'YOUR WLAN SSID'
WL_PASSWD = 'YOUR WLAN PASSWD'
GAPI_CALID = 'primary'

# read and exec the config for me (CODE INJECTION ??)
from hodynyk_cfg import WL_SSID, WL_PASSWD, GAPI_CALID

# hardware config is in separate module
from HW_cfg import HW

def instant( desc , argv = {} ):
    try:
        d = desc['args'].copy()
        d.update( argv )
        mod = __import__( desc['mod'], None, None, desc['mod'] , 0 )
        return mod.__dict__[desc['mod']]( d )
    except:
        return None

c = { 'calID' : GAPI_CALID , 'WL_SSID' : WL_SSID , 'WL_PASSWD' : WL_PASSWD , 'instant' : instant , 'HW' : HW }
control = instant( HW[ 'Control' ] , c )
control.run( True )

# [ control.UI_mode, control.srdInvocations, time.localtime( control.srdPeriod ) , time.localtime(control.gmt2loc(control.alarms.alarm)) , time.localtime( control.gmt2loc(control.UI_ALM_skip)) , control.UI_ALM_on ]
