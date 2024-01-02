from machine import Pin, SPI, Timer
from max7219 import SevenSegment, SEG_7219_STD

DAYS = ( 'Po', 'Ut', 'St', 'Ct', 'Pa', 'So', 'Ne', '__' )

class DISP_SevenSeg_max7219:
    def __init__( self , argv ):
        CS = Pin(   argv['P_CS']  , Pin.OUT)
        CLK = Pin(  argv['P_CLK'] )
        MOSI = Pin( argv['P_MOSI'] )
        spi = SPI(0, baudrate=500000,  sck = CLK, mosi = MOSI)
        self.display = SevenSegment(spi, CS, 4)
        self.display.init(0)
        self.display.buffer=[0,0,0,0]
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
        self.display.buffer = [ SEG_7219_STD[ord('C')], SEG_7219_STD[ord('o')], SEG_7219_STD[ ord('n') + num // 10], SEG_7219_STD[num % 10] ]
        self.display.show()

    def showNTPGet( self ):
        self.display.buffer = [ SEG_7219_STD[ord('N')], SEG_7219_STD[ord('t')], SEG_7219_STD[ord('p')], 0 ]
        self.display.show()

    def showTime( self, t_struct, ddots ):
        if ddots & 4:
            self.display.buffer = [ 0, 0, 0, 0 ]
            if ddots & 1:
                self.display.buffer[ 0 if ddots & 2 else 1 ] |= 0x80
            else:
                self.display.buffer[ 2 ] |= 0x80
        else:
            self.display.buffer = [ SEG_7219_STD[t_struct[3] // 10], SEG_7219_STD[t_struct[3] % 10], SEG_7219_STD[t_struct[4] // 10], SEG_7219_STD[t_struct[4] % 10] ]
            if ddots & 1:
                self.display.buffer[ 0 if ddots & 2 else 1 ] |= 0x80
                self.display.buffer[ 2 ] |= 0x80
        self.display.show()

    def showAlmTime( self, tA_struct , tN_struct, td, ddots ):
        self.display.buffer = [ SEG_7219_STD[tA_struct[3] // 10], SEG_7219_STD[tA_struct[3] % 10], SEG_7219_STD[tA_struct[4] // 10], SEG_7219_STD[tA_struct[4] % 10] ]
        self.display.buffer[ 0 if ddots & 2 else 1 ] |= 0x80
        self.display.show()

    def showDate( self, t_struct, ddots ):
        dy = DAYS[ t_struct[6] ]
        tt = '{:02d}{:2d}{:4d}'.format( t_struct[2], t_struct[1], t_struct[0] )
        self.display.buffer = [ SEG_7219_STD[t_struct[2] // 10], SEG_7219_STD[t_struct[2] % 10], SEG_7219_STD[t_struct[1] // 10], SEG_7219_STD[t_struct[1] % 10] ]
        self.display.buffer[ 0 if ddots & 2 else 1 ] |= 0x80
        self.display.show()

    def showEnv( self, ddots , sensData ):
        dd = '{:2d}C {:2d}%'.format( sensData[0], sensData[1] )
        self.display.buffer = [ SEG_7219_STD[sensData[0] // 10] , SEG_7219_STD[sensData[0] % 10] , 0x63, SEG_7219_STD[ord('[')] ]
        self.display.show()
