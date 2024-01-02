import time

class TZ_CET:
    def __init__( self , argv ):
        setattr( argv[ 'control' ] , 'gmt2loc' , self.cettime )

    def cettime( self, t ):
        # z https://github.com/orgs/micropython/discussions/11173#discussioncomment-6073759
        year = time.localtime( t )[0]	#get year
        dstBeginUTC = time.mktime((year, 3,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) # last Sunday of March 01:00Z begins CEST
        dstEndUTC   = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) # last Sunday of October 01:00Z returns CET
        if t < dstBeginUTC:		# before begin
            return t + 3600		# CET:  UTC+1H
        elif t < dstEndUTC:		# before end
            return t + 7200		# CEST: UTC+2H
        else:					# after end
            return t + 3600		# CET:  UTC+1H

