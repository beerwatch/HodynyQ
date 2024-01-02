from binascii import hexlify
import time, network, ntptime

class NET_WLAN:
    def __init__( self , args ):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        network.hostname('PiCow-' + str(hexlify(self.wlan.config('mac')))[8:-1] )
        self.control = args[ 'control' ]

        self.wl_ssid = args[ 'WL_SSID' ]
        self.wl_pass = args[ 'WL_PASSWD' ]
        self.wlan.connect( self.wl_ssid , self.wl_pass )
        i=0
        while not self.wlan.isconnected():
            i = i+1
            self.control.display.showConnect( i )
            time.sleep(1)
        self.control.display.showNTPGet( )
        ntptime.settime()
