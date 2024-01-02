from machine import Pin, SPI, Timer
from max7219 import Matrix8x8

DAYS = ( 'Po', 'Ut', 'St', 'Ct', 'Pa', 'So', 'Ne', '__' )

class DISP_Matrix8x8_max7219:
    def __init__( self , argv ):
        CS = Pin(   argv['P_CS']  , Pin.OUT)
        CLK = Pin(  argv['P_CLK'] )
        MOSI = Pin( argv['P_MOSI'] )
        spi = SPI(0, baudrate=500000,  sck = CLK, mosi = MOSI)
        self.display = Matrix8x8(spi, CS, 7, orientation=1)
        self.display.invert = False
        self.display.fill(False)
        self.display.text('HodynyQ', 0, 0, 1)
        self.display.show()
        self.dimmer = Timer()
        self.setBright( argv[ 'BRIGHT' ] , -1 )

    def setBright( self, toBright, fromBright=None, transTime=0, repeat=False ):
        self.dimmer.deinit()
        if fromBright == None: fromBright = self.currBright
        self.delta = toBright - fromBright
        if self.delta == 0: return

        self.stepTime = 20
        if transTime < self.stepTime:
            self.currBright = toBright
            self.toBright = toBright
            self.delta = 0
        else:
            if abs(self.delta) * self.stepTime < transTime:
                self.stepTime = transTime // abs(self.delta)
            steps = transTime // self.stepTime
            self.delta = ( self.delta + 1 ) // ( steps if steps > 1 else 1 )
            if abs(self.delta) < 1:
                self.delta = 1 if toBright > fromBright else -1
            self.toBright   = toBright
            self.fromBright = fromBright
            self.repeat     = repeat
            self.currBright = fromBright + self.delta // 2
            self.dimmer.init( period = self.stepTime , mode=Timer.PERIODIC, callback=self._dimstep )
        self.display.brightness( self.currBright )

    def _dimstep( self, dimmer ):
        if abs( self.toBright - self.currBright ) > abs( self.delta ):
            self.currBright = self.currBright + self.delta
        else:
            self.currBright = self.toBright
            if self.repeat:
                self.delta, self.fromBright, self.toBright = -self.delta, self.toBright, self.fromBright
            else:
                self.dimmer.deinit()
        self.display.brightness( self.currBright )

    def showConnect( self, num ):
        self.display.fill(False)
        self.display.text('Wlan {:d}'.format( num ), 0, 0, 1)
        self.display.show()

    def showNTPGet( self ):
        self.display.fill(False)
        self.display.text('Get NTP', 0, 0, 1)
        self.display.show()

    def showTime( self, t_struct, ddots ):
        self.display.fill(False)
        tt='{:2d}:{:02d}:{:02d}'.format(t_struct[3], t_struct[4], t_struct[5])
        dp = ':' if ddots & 2 else '.'
        if ddots & 4:
            if ddots & 1:
                self.display.text(dp, 34, -2, 1)
            else:
                self.display.text(dp, 14, -2, 1)
        else:
            self.display.text(tt[0:2], 0, 0, 1)
            self.display.text(tt[3:5], 20, 0, 1)
            self.display.text(tt[6:8], 40, 0, 1)
            if ddots & 1:
                self.display.text(dp, 14, 0, 1)
                self.display.text(dp, 34, 0, 1)
        self.display.show()

    def showAlmTime( self, tA_struct , tN_struct, td, ddots ):
        self.display.fill(False)
        dD = td//84600
        if dD < 0:
            tt='-- -- --'
        elif dD > 99:
            tt='++  > 99'
        elif dD > 9:
            tt='{:2d} {:02d} {:02d}'.format(dD, tA_struct[3], tA_struct[4])
        else:
            tt='{:+2d} {:02d} {:02d}'.format(dD, tA_struct[3], tA_struct[4])
        self.display.text(tt[0:2], 0, 0, 1)
        self.display.text(tt[3:5], 20, 0, 1)
        self.display.text(tt[6:8], 40, 0, 1)
        self.display.text(':' if ddots & 2 else '.', 34, 0, 1)
        self.display.show()

    def showDate( self, t_struct, ddots ):
        dy = DAYS[ t_struct[6] ]
        tt = '{:02d}{:02d}{:4d}'.format( t_struct[2], t_struct[1], t_struct[0] )
        self.display.fill(False)
        self.display.text(dy[0], -1, 0, 1)
        self.display.text(dy[1],  7, 0, 1)
        self.display.text(tt[0], 14, 0, 1)
        self.display.text(tt[1], 21, 0, 1)
        self.display.text(tt[2], 28, 0, 1)
        self.display.text(tt[3], 35, 0, 1)
        self.display.text(tt[6], 42, 0, 1)
        self.display.text(tt[7], 49, 0, 1)
        if ddots & 1:
            self.display.pixel(  14, 6, 1)
            self.display.pixel(  28, 6, 1)
            self.display.pixel(  42, 6, 1)
        self.display.show()

    def showDateWide( self, t_struct, ddots ):
        dy = DAYS[ t_struct[6] ]
        tt = '{:2d}{:2d}'.format( t_struct[2], t_struct[1] )
        self.display.fill(False)
        self.display.text(dy[0]   , -1, 0, 1)
        self.display.text(dy[1]   , 7, 0, 1)
        if ddots:
            self.display.text(',' , 12, 0, 1)
        self.display.text(tt[0]   , 20, 0, 1)
        self.display.text(tt[1]   , 27, 0, 1)
        self.display.text('.'     , 32, 0, 1)
        self.display.text(tt[2]   , 39, 0, 1)
        self.display.text(tt[3]   , 46, 0, 1)
        self.display.text('.'     , 51, 0, 1)
        self.display.show()

    def showEnv( self, ddots , sensData ):
        dd = '{:2d}C {:2d}%'.format( sensData[0], sensData[1] )
        self.display.fill(False)
        self.display.text(dd[0:2], 0, 0, 1)
        self.display.text('.', 13, -5, 1)
        self.display.text(dd[2:3], 18, 0, 1)
        self.display.text(dd[4:], 32, 0, 1)
        if ddots:
            self.display.text('.', 25, 0, 1)
        self.display.show()
