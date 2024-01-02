from machine import Timer, Pin

class btn:
    def __init__(self, nPin, hndlr):
        self.pin = Pin( nPin, Pin.IN, Pin.PULL_UP )
        self.int = self.pin.irq( self._irqh, Pin.IRQ_FALLING | Pin.IRQ_RISING )
        self.val = self.pin.value()
        self.dbt = Timer()
        self.hnd = hndlr

    def _irqh( self, p ):
        self.dbt.init( period=5, mode=Timer.ONE_SHOT, callback=self._dbth )

    def _dbth( self, t ):
        v = self.pin.value()
        if self.val == v:
            self._irqh( None )
        else:
            self.val = v
            self.dbt.deinit()
            self.hnd(not v)
