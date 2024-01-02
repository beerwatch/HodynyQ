from time import sleep
from machine import Pin, PWM, Timer

BEAT = 0.4

liten_mus = [ ['d5', BEAT / 2], ['d#5', BEAT / 2], ['f5', BEAT], ['d6', BEAT], ['a#5', BEAT], ['d5', BEAT],  
              ['f5', BEAT], ['d#5', BEAT], ['d#5', BEAT], ['c5', BEAT / 2],['d5', BEAT / 2], ['d#5', BEAT], 
              ['c6', BEAT], ['a5', BEAT], ['d5', BEAT], ['g5', BEAT], ['f5', BEAT], ['f5', BEAT], ['d5', BEAT / 2],
              ['d#5', BEAT / 2], ['f5', BEAT], ['g5', BEAT], ['a5', BEAT], ['a#5', BEAT], ['a5', BEAT], ['g5', BEAT],
              ['g5', BEAT], ['', BEAT / 2], ['a#5', BEAT / 2], ['c6', BEAT / 2], ['d6', BEAT / 2], ['c6', BEAT / 2],
              ['a#5', BEAT / 2], ['a5', BEAT / 2], ['g5', BEAT / 2], ['a5', BEAT / 2], ['a#5', BEAT / 2], ['c6', BEAT],
              ['f5', BEAT], ['f5', BEAT], ['f5', BEAT / 2], ['d#5', BEAT / 2], ['d5', BEAT], ['f5', BEAT], ['d6', BEAT],
              ['d6', BEAT / 2], ['c6', BEAT / 2], ['b5', BEAT], ['g5', BEAT], ['g5', BEAT], ['c6', BEAT / 2],
              ['a#5', BEAT / 2], ['a5', BEAT], ['f5', BEAT], ['d6', BEAT], ['a5', BEAT], ['a#5', BEAT * 1.5] ]

BEAT = 0.35

liten_mus = [ ["e5", BEAT ], ["g5", BEAT ],                   ["a5", BEAT * 2], ["P", BEAT / 2 ],
              ["e5", BEAT ], ["g5", BEAT ], ["b5", BEAT / 2], ["a5", BEAT * 2], ["P", BEAT / 2 ],
              ["e5", BEAT ], ["g5", BEAT ],                   ["a5", BEAT * 2], ["P", BEAT / 2 ],
                             ["g5", BEAT ],
              ["e5", BEAT * 2]
              ]

NOTES = {
    'P' : 0,  'p' : 0, '' : 0,
    'b0': 31,
    'c1': 33, 'c#1': 35, 'd1': 37, 'd#1': 39, 'e1': 41, 'f1': 44, 'f#1': 46, 'g1': 49,'g#1': 52, 'a1': 55, 'a#1': 58, 'b1': 62,
    'c2': 65, 'c#2': 69, 'd2': 73, 'd#2': 78, 'e2': 82, 'f2': 87, 'f#2': 93, 'g2': 98, 'g#2': 104, 'a2': 110, 'a#2': 117, 'b2': 123,
    'c3': 131, 'c#3': 139, 'd3': 147, 'd#3': 156, 'e3': 165, 'f3': 175, 'f#3': 185, 'g3': 196, 'g#3': 208, 'a3': 220, 'a#3': 233, 'b3': 247,
    'c4': 262, 'c#4': 277, 'd4': 294, 'd#4': 311, 'e4': 330, 'f4': 349, 'f#4': 370, 'g4': 392, 'g#4': 415, 'a4': 440, 'a#4': 466, 'b4': 494,
    'c5': 523, 'c#5': 554, 'd5': 587, 'd#5': 622, 'e5': 659, 'f5': 698, 'f#5': 740, 'g5': 784, 'g#5': 831, 'a5': 880, 'a#5': 932, 'b5': 988,
    'c6': 1047, 'c#6': 1109, 'd6': 1175, 'd#6': 1245, 'e6': 1319, 'f6': 1397, 'f#6': 1480, 'g6': 1568, 'g#6': 1661, 'a6': 1760, 'a#6': 1865, 'b6': 1976,
    'c7': 2093, 'c#7': 2217, 'd7': 2349, 'd#7': 2489, 'e7': 2637, 'f7': 2794, 'f#7': 2960, 'g7': 3136, 'g#7': 3322, 'a7': 3520, 'a#7': 3729, 'b7': 3951,
    'c8': 4186, 'c#8': 4435, 'd8': 4699, 'd#8': 4978 
    }

VOLUMES = [ 16, 32, 64, 128, 256, 1024, 4096, 16384 ]

class SND_PWMbuzzer:
    def __init__(self, argv):
        self.aPOWER = Pin( argv[ 'P_APOWER' ], Pin.OUT, value=1 )
        self.pOUT = Pin( argv[ 'P_AOUT' ], Pin.OUT, value=0 )
        self.p = PWM( self.pOUT, duty_u16 = 0 )
        self.t = Timer()
        self.stop()

    def _power( self, x ):
        self.aPOWER.value( not x)

    def stop( self ):
        self.t.deinit()
        self.p.deinit()
        self.bStop = True
        self.pOUT.off()
        self._power( False )

    def asyncplay( self , bRepeat = False , u16Volume = 8192 ):
        self.bStop = False
        self.u16Volume = u16Volume
        self.bRepeat = bRepeat
        if bRepeat:
            self.volumes = iter( VOLUMES )
            self.u16Volume = next( self.volumes )
        self._power( True )
        self.notes = iter( liten_mus )
        self.t.init( mode=Timer.ONE_SHOT, period=150, callback=self._asy_note )

    def _asy_note(self, t):
        try:
            note = next( self.notes )
            ts = 0.1
            frq = 0
            try:
                frq = NOTES[ note[0] ]
                ts = note[1]
            finally:
                if frq != 0:
                    self.p.init( freq = frq, duty_u16 = self.u16Volume )
                self.t.init( mode=Timer.ONE_SHOT, period=int(1000*ts - 300*BEAT), callback=self._asy_fade )
        except StopIteration:
            if self.bRepeat:
                self.notes = iter( liten_mus )
                self.t.init( mode=Timer.ONE_SHOT, period=1500, callback=self._asy_note )
                self.u16Volume = 8192
                try:
                    self.u16Volume = next( self.volumes )
                except StopIteration:
                    self.volumes = iter( VOLUMES )
                    self.u16Volume = next( self.volumes )
                finally:
                    pass
            else:
                self.stop()
        except:
            self.stop()
        
    def _asy_fade(self, t):
        self.t.init( mode=Timer.ONE_SHOT, period=int(300*BEAT), callback=self._asy_note )
        self.p.deinit()
