# uppper HID - model
from btn import btn
from machine import Timer
import time

class HID_SingleButton:
    def __init__( self , args ):
        self.tmLongPush = Timer()		# long push timer
        self.control = args[ 'control' ]
        self.B1 = btn( args[ 'pins' ][ 0 ], self._B1handler )

    def _toggleALM( self, tmr ):
        self.control.UI_ALM_on = not self.control.UI_ALM_on
        self._B1handler( True )
        
    def _chg2Day( self, tmr ):
        self.control.UI_mode = self.control.UI_DAY
        self._B1handler( True )

    def _B1handler( self, pushed ):
        if pushed:
            self.control.stop()
            if self.control.UI_mode == self.control.UI_NIGHT:
                self.control.view.viewTime()
                self.tmLongPush.init( period=3000, mode=Timer.ONE_SHOT, callback=self._chg2Day )
            elif self.control.UI_mode == self.control.UI_DAY:
                self.control.view.viewAlarm()
                self.tmLongPush.init( period=3000, mode=Timer.ONE_SHOT, callback=self._toggleALM )
            else:
                self.control.endAlarm()
        else:
            self.tmLongPush.deinit()
            self.control.run(True)

