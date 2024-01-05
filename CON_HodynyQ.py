# controller & upper UI
from machine import Timer
import time

class CON_HodynyQ:
    UI_DAY = const(1)
    UI_NIGHT = const(2)
    UI_PREALARM = const(3)
    UI_ALARM = const(4)

    def __init__( self , argv ):
        self.tmChg = Timer()		# mode switch timer
        self.gmt2loc = lambda t: t	# updated by Timezone constructor

        # parameters, power on defaults
        self.UI_DAYTIME = 'daytime' in argv and argv[ 'daytime' ] or { 330:1, 1290:0 }
        self.UI_BRIGHTNESS = 'brightness' in argv and argv[ 'brightness' ] or [ 6, 0, 1, 15 ]
        self.UI_ALMLIMIT = 'almlimit' in argv and argv[ 'almlimit' ] or 1800
        self.UI_ALM_on = 'almdefault' in argv and argv[ 'almdefault' ] or False

        # current status
        self.UI_mode = self.UI_DAY
        self.UI_ALM_skip = 0
        self.srdInvocations = 0 	# statistics
        self.srdPeriod = 0

        # factor the system
        HW = argv['HW']
        instant = argv['instant']
        del argv['instant'], argv['HW']
        argv[ 'control' ] = self
        for k in 'Timezone', 'Sound', 'Display', 'View', 'Wlan', 'Alarms', 'Enviro', 'HID':
            setattr( self , k.lower() , instant( HW[ k ] , argv ) )

    def _dayPlan( self, d, t ):
        p = None
        b = None
        e = t[3] * 60 + t[4]
        for k,v in sorted(d.items()):
            if b is None:
                b = k
            if k <= e:
                p = v
                b = None
        return [ p if p != None else v , 60 * ( b if b != None else 0 ) ]

    def _reRun( self, t ):
        self.run( False )

    def run( self , updateAlarms = False ):
        self.srdInvocations += 1
        oldUIMode = self.UI_mode
        t = self.gmt2loc( time.time() )
        tt = self._dayPlan( self.UI_DAYTIME, time.localtime( t ) )
        newMode = tt[ 0 ] > 0 and self.UI_DAY or self.UI_NIGHT
        tc = t - t % 86400 + tt[ 1 ]

        if self.alarms.alarm != 0 and self.UI_ALM_on:
            if self.UI_ALM_skip != self.alarms.alarm:
                tr = self.gmt2loc( self.alarms.remind )
                ta = self.gmt2loc( self.alarms.alarm )
                te = ta + self.UI_ALMLIMIT
                if t < te:
                    if t >= ta:
                        newMode = self.UI_ALARM
                        tc = te
                    elif t >= tr:
                        newMode = self.UI_PREALARM
                        tc = ta
                    elif tr < tc:
                        tc = tr
                else:
                    self.endAlarm()
            else:
                ta = self.gmt2loc( self.alarms.alarm )
                if t >= ta:
                    self.UI_ALM_skip = 0
                    updateAlarms = True
                elif tc > ta:
                    tc = ta

        while tc < t:
            tc = tc + 86400

        self.srdPeriod = tc
        self.suspend()
        self.tmChg.init(period=(tc-t)*1000, mode=Timer.ONE_SHOT, callback=self._reRun )

        if self.UI_ALM_on and ( updateAlarms or self.UI_mode == self.UI_ALARM ):
            self.alarms.enableUpdate()

        self.UI_mode = newMode
        if self.UI_mode == self.UI_NIGHT:
            self.view.startNightView()
        elif self.UI_mode == self.UI_DAY:
            self.view.startDayView( tt[0] - 1 )
        else:
            self.view.startAlarmView()
            if self.UI_mode == self.UI_ALARM:
                self.alarms.disableUpdate()
                self.sound.asyncplay( True )

    def endAlarm( self ):
        self.UI_ALM_skip = self.alarms.alarm
        if self.UI_mode == self.UI_ALARM:
            self.sound.stop()

    def suspend( self ):
        self.tmChg.deinit()
        self.view.stopView()

    def stop( self ):
        self.alarms.disableUpdate()
        self.suspend()
