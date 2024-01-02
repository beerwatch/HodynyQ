# Google Calendar API alarms manager

from SGApi import SGApi
from machine import Timer
import ntptime

class ALM_GAPI:
    def __init__( self, args ):
        self.control = args[ 'control' ]
        self.remind = 0
        self.alarm = 0
        self.detail = {}
        self.GAPI = SGApi( args[ 'calID' ] )
        self.tmCal = Timer()

    def _updateNextAlarm(self, timer):
        ntptime.settime()
        Curr = self.GAPI.GAPI_getUpdateNextAlarm()
        if Curr != None:
            self.remind, self.alarm, self.detail = Curr
            if timer is not None:
                self.control.run()
            per = 9000000
        else:
            per = 900000
        if timer is not None:
            self.enableUpdate( per )

    def enableUpdate( self, per = 14500 ):
        self.tmCal.init( period=per, mode=Timer.ONE_SHOT, callback=self._updateNextAlarm )

    def disableUpdate(self):
        self.tmCal.deinit()
