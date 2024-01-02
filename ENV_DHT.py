import dht

class ENV_DHT:
    def __init__( self , args ):
        try:
            self.sen = dht.DHT11( args[ 'DHT_GPIO' ] )
            self.sen.measure()
        except:
            self.sen = None
            raise AssertionError( 'Unrecognized sensor' )

    def measure( self ):
        self.sen.measure()

    def humidity( self ):
        return self.sen.humidity()

    def temperature( self ):
        return self.sen.temperature()

