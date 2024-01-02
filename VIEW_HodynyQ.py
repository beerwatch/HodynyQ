# lower UI (view)
from machine import Timer
import time

class VIEW_HodynyQ():
    def __init__( self , args ):
        self.tmRef = Timer()		# refresh display
        self.tmDot = Timer()		# dot change
        self.control = args[ 'control']
        self.ddotFirst = 0

    def _dayUpdate( self , ddots ):
        t = time.localtime( self.control.gmt2loc( time.time() ) )
        if self.control.enviro is not None:
            if t[5] > 35 and t[5] < 41:
                self.control.display.showEnv( ddots , [ self.control.enviro.temperature(), self.control.enviro.humidity() ] )
                return
        if t[5] > 15 and t[5] < 21:
            self.control.display.showDate( t , ddots | ( 2 if self.control.UI_ALM_on else 0 ) )
        else: 
            self.control.display.showTime( t , ddots | ( 2 if self.control.UI_ALM_on else 0 ) )
        if self.control.enviro is not None and t[5] == 35:
            self.control.enviro.measure()

    def _dayUpdate0( self, timer ):
        self._dayUpdate( 0 )
        self.tmDot.init(period=500, mode=Timer.ONE_SHOT, callback=self._dayUpdate1 )

    def _dayUpdate1( self, timer ):
        self._dayUpdate( 1 )

    def _nightUpdate( self, timer ):
        t = time.localtime( self.control.gmt2loc( time.time() ) )
        self.control.display.showTime( t , self.ddotFirst | ( 2 if self.control.UI_ALM_on else 0 ) | 4 )
        self.ddotFirst = 1 - self.ddotFirst

    def startNightView( self ):
        self.control.display.setBright( self.control.UI_BRIGHTNESS[1] )
        self.tmRef.init(period=1000, mode=Timer.PERIODIC, callback=self._nightUpdate )
        self._nightUpdate( 0 )
        
    def startDayView( self , bright = None ):
        self.control.display.setBright(bright and bright or self.control.UI_BRIGHTNESS[0], None, 330)
        self._start_dayUpdate()
        
    def startAlarmView( self ):
        self.control.display.setBright(self.control.UI_BRIGHTNESS[3], self.control.UI_BRIGHTNESS[2], 1500, True)
        self._start_dayUpdate()
        
    def _start_dayUpdate( self ):
        self.tmRef.init(period=1000, mode=Timer.PERIODIC, callback=self._dayUpdate0 )
        self._dayUpdate0( True )
        
    def stopView( self ):
        self.tmDot.deinit()
        self.tmRef.deinit()
        
    def viewTime( self ):
        t = time.localtime( self.control.gmt2loc( time.time() ) )
        self.control.display.showTime( t , 1 | ( 2 if self.control.UI_ALM_on else 0 ) )

    def viewAlarm( self ):
        tA = time.localtime( self.control.gmt2loc( self.control.alarms.alarm ) )
        t = time.time()
        td = self.control.alarms.alarm - t
        t = time.localtime( self.control.gmt2loc( t ) )
        self.control.display.showAlmTime( tA , t , td, 2 if self.control.UI_ALM_on else 0 )
