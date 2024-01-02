from array import array
from machine import Pin,mem32
from rp2 import PIO, StateMachine, asm_pio

F7SEG = (
        0x77 , 	0x11 , 	0x6B , 	0x3B , 	0x1D , 	0x3E , 	0x7E , 	0x13 , 	0x7F , 	0x3F , 	0x5F , 	0x7C , 	0x68 , 	0x79 , 	0x6E , 	0x4E , # 0-9AbcdEF
        0xF7 , 	0x91 , 	0xEB , 	0xBB , 	0x9D , 	0xBE , 	0xFE , 	0x93 , 	0xFF , 	0xBF , 	0xDF , 	0xFC , 	0xE6 , 	0xF9 , 	0xEE , 	0xCE , # ditto w/ dot
        0x00 , 	0x90 , 	0x09 , 	0x08 , 	0x08 , 	0x08 , 	0x08 , 	0x01 , 	0x67 , 	0x37 , 	0x08 , 	0x08 , 	0x10 , 	0x08 , 	0x80 , 	0x49 , 
        0x77 , 	0x11 , 	0x6B , 	0x3B , 	0x1D , 	0x3E , 	0x7E , 	0x13 , 	0x7F , 	0x3F , 	0x40 , 	0xC0 , 	0x0E , 	0x28 , 	0x0B , 	0xCB , 
        0x7B , 	0x5F , 	0x7C , 	0x68 , 	0x79 , 	0x6E , 	0x4E , 	0x76 , 	0x5C , 	0x10 , 	0x31 , 	0x5E , 	0x64 , 	0x5A , 	0x58 , 	0x78 , 
        0x4F , 	0x1F , 	0x48 , 	0x1E , 	0x6C , 	0x75 , 	0x4D , 	0x6D , 	0x5D , 	0x3D , 	0x1B , 	0x66 , 	0x1C , 	0x33 , 	0x07 , 	0x20 , 
        0x0C , 	0x5F , 	0x7C , 	0x68 , 	0x79 , 	0x6E , 	0x4E , 	0x76 , 	0x5C , 	0x10 , 	0x31 , 	0x5E , 	0x64 , 	0x5A , 	0x58 , 	0x78 , 
        0x4F , 	0x1F , 	0x48 , 	0x1E , 	0x6C , 	0x75 , 	0x4D , 	0x6D , 	0x5D , 	0x3D , 	0x1B , 	0x06 , 	0x44 , 	0x30 , 	0x03 , 	0x00 , 
        )

DAYS = ( 'Po', 'Ut', 'St', 'Ct', 'Pa', 'So', 'Ne', '__' )

#now for the display buffer DMA
DMA_BASE       = 0x50000000

DMA_CH0_NUM    = const(5)
DMA_CH0_BASE   = DMA_BASE + (0x040 * DMA_CH0_NUM)
CH0_READ_ADDR  = DMA_CH0_BASE+0x000
CH0_READ_ADDR_TRIG = DMA_CH0_BASE+0x03c
CH0_WRITE_ADDR = DMA_CH0_BASE+0x004
CH0_TRANS_COUNT= DMA_CH0_BASE+0x008
CH0_CTRL_TRIG  = DMA_CH0_BASE+0x00c
CH0_AL1_CTRL   = DMA_CH0_BASE+0x010

DMA_CH1_NUM    = const(6)
DMA_CH1_BASE   = DMA_BASE + (0x040 * DMA_CH1_NUM)
CH1_READ_ADDR  = DMA_CH1_BASE+0x000
CH1_READ_ADDR_TRIG = DMA_CH1_BASE+0x03c
CH1_WRITE_ADDR = DMA_CH1_BASE+0x004
CH1_TRANS_COUNT= DMA_CH1_BASE+0x008
CH1_CTRL_TRIG  = DMA_CH1_BASE+0x00c
CH1_AL1_CTRL   = DMA_CH1_BASE+0x010

PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE+0x10

_p_ar=array('I',[0])				# global 1-element array 
@micropython.viper
def dispDmaStart(ar,nword):
    mem32[CH1_AL1_CTRL]=0
    mem32[CH0_AL1_CTRL]=0
    p=ptr32(ar)

    # control (reload) channel setup
    _p_ar[0]=p
    mem32[CH1_READ_ADDR]=ptr(_p_ar)
    mem32[CH1_WRITE_ADDR]=CH0_READ_ADDR
    mem32[CH1_TRANS_COUNT]=1
    IRQ_QUIET=0x1					# do not generate interrupt
    TREQ_SEL=0x3f					# no pacing (full speed / memory to memory)
    CHAIN_TO=DMA_CH0_NUM			# start data channel when done
    RING_SEL=0
    RING_SIZE=0						# no wrapping
    INCR_WRITE=0					# write to port
    INCR_READ=0						# read the same value
    DATA_SIZE=2						# 32-bit word transfer
    HIGH_PRIORITY=0
    EN=1
    CTRL1=(IRQ_QUIET<<21)|(TREQ_SEL<<15)|(CHAIN_TO<<11)|(RING_SEL<<10)|(RING_SIZE<<9)|(INCR_WRITE<<5)|(INCR_READ<<4)|(DATA_SIZE<<2)|(HIGH_PRIORITY<<1)|(EN<<0)
    mem32[CH1_AL1_CTRL]=CTRL1		# do not activate

    # data channel setup
    mem32[CH0_READ_ADDR]=p
    mem32[CH0_WRITE_ADDR]=PIO0_BASE_TXF0
    mem32[CH0_TRANS_COUNT]=nword
    IRQ_QUIET=0x1					# do not generate interrupt
    TREQ_SEL=0x00					# wait for PIO0_TX0
    CHAIN_TO=DMA_CH1_NUM			# start reload channel when done
    RING_SEL=0
    RING_SIZE=0						# no wrapping
    INCR_WRITE=0					# write to port
    INCR_READ=1						# read from array
    DATA_SIZE=2						# 32-bit word transfer
    HIGH_PRIORITY=0
    EN=1
    CTRL0=(IRQ_QUIET<<21)|(TREQ_SEL<<15)|(CHAIN_TO<<11)|(RING_SEL<<10)|(RING_SIZE<<9)|(INCR_WRITE<<5)|(INCR_READ<<4)|(DATA_SIZE<<2)|(HIGH_PRIORITY<<1)|(EN<<0)
    mem32[CH0_CTRL_TRIG]=CTRL0		# activate

# now for the display parallel 8*8 multiplex interface
@asm_pio(
    out_init= [PIO.OUT_LOW] * 16
    , out_shiftdir=PIO.SHIFT_LEFT
    , autopull=True, pull_thresh=32
    )
def disp_pio():
    out(pins,16)


class DISP_mux8x7seg_DMAPIO:
    def __init__( self , argv ):
        # create he display buffer, fill initial values
        self.ndisp=8								# number of digits
        self.bdisp=array("B",[0]*self.ndisp*2)		# two bytes per digit: value and position
        for i in range(self.ndisp):				# me no cares about output digit order when collating halfwords into words as position is put out too
            self.bdisp[ i * 2 ] = F7SEG[ ord( '-' ) ]			# '-' segment driver lines
            self.bdisp[ i * 2 + 1 ] = (0x1 << i)	# digit driver line for the digit position

        self.cposi = 0

        # now start the display refresh
        dispDmaStart(self.bdisp,self.ndisp//2)	# configure infinite DMA bdisp wodrs buffer transfer
        self.sm=StateMachine(0,disp_pio,out_base=Pin(6),freq=2000)		# construct the PIO driver
        self.sm.active(1)						# activate
        self.sm.put(0)							# kick SM DREQ stall after soft reboot

        self.setBright( argv[ 'BRIGHT' ] )

    def setBright( self, toBright, fromBright=None, transTime=0, repeat=False ):
        self.currBright = toBright

    def showConnect( self, num ):
        self.bdisp[ ( ( num - 1 ) & 7 ) * 2 ] ^= ( F7SEG[ ord( '[' ) ] | F7SEG[ ord( '-' ) ] )			# 'C-'
        self.cposi = num  & 7

    def showNTPGet( self ):
        self.bdisp[ self.cposi * 2 ] = F7SEG[ ord( 't' ) ]				# 't'
        self.cposi = 0
        
    def showTime( self, t_struct, ddots ):
        self.bdisp[ 0] = F7SEG[ t_struct[3] // 10 ]
        self.bdisp[ 2] = F7SEG[ t_struct[3] % 10 ]
        self.bdisp[ 6] = F7SEG[ t_struct[4] // 10 ]
        self.bdisp[ 8] = F7SEG[ t_struct[4] % 10 ]
        if self.currBright > 0:
            self.bdisp[12] = F7SEG[ t_struct[5] // 10 ]
            self.bdisp[14] = F7SEG[ t_struct[5] % 10 ]
            if ddots & 1:
                self.bdisp[ 4] = 0x80
                self.bdisp[10] = 0x80
            else:
                self.bdisp[ 4] = 0x0
                self.bdisp[10] = 0x0
        else:
            self.bdisp[12] = 0x0
            self.bdisp[14] = 0x0
            if ddots & 1:
                self.bdisp[ 4] = 0x0
                self.bdisp[10] = 0x80
            else:
                self.bdisp[ 4] = 0x80
                self.bdisp[10] = 0x0

    def showAlmTime( self, tA_struct , tN_struct, td, ddots ):
        self.display.fill(False)
        dD = td // 84600
        if dD < 0:
            tt='-- -- --'
        elif dD > 99:
            tt='++  > 99'
        elif dD > 9:
            dd='{:2d} {:02d}:{:02d}'.format(dD, tA_struct[3], tA_struct[4])
        else:
            dd='{:+2d} {:02d}:{:02d}'.format(dD, tA_struct[3], tA_struct[4])
        self.bdisp[ 0] = F7SEG[ ord( dd[0] ) ]
        self.bdisp[ 2] = F7SEG[ ord( dd[1] ) ]
        self.bdisp[ 4] = F7SEG[ ord( dd[2] ) ]
        self.bdisp[ 6] = F7SEG[ ord( dd[3] ) ]
        self.bdisp[ 8] = F7SEG[ ord( dd[4] ) ]
        self.bdisp[10] = F7SEG[ ord( dd[5] ) ]
        self.bdisp[12] = F7SEG[ ord( dd[6] ) ]
        self.bdisp[14] = F7SEG[ ord( dd[7] ) ]

    def showDate( self, t_struct, ddots ):
        dy = DAYS[ t_struct[6] ]
        self.bdisp[0] = F7SEG[ ord( dy[0] ) ]
        self.bdisp[2] = F7SEG[ ord( dy[1] ) ]
        dd = '{:2d}{:2d}{:4d}'.format( t_struct[2], t_struct[1], t_struct[0] )
        self.bdisp[ 4] = F7SEG[ ord( dd[0] ) ]
        self.bdisp[ 6] = F7SEG[ ord( dd[1] ) ] | ((ddots & 1) and 0x80 or 0)
        self.bdisp[ 8] = F7SEG[ ord( dd[2] ) ]
        self.bdisp[10] = F7SEG[ ord( dd[3] ) ] | ((ddots & 1) and 0x80 or 0)
        #self.bdisp[8] = F7SEG[ ord( dd[4] ) ]
        #self.bdisp[10] = F7SEG[ ord( dd[5] ) ]
        self.bdisp[12] = F7SEG[ ord( dd[6] ) ]
        self.bdisp[14] = F7SEG[ ord( dd[7] ) ]

    def showEnv( self, ddots , sensData ):
        dd = '{:2d}{:2d}'.format( sensData[0], sensData[1] )
        self.bdisp[ 0] = F7SEG[ ord( dd[0] ) ]
        self.bdisp[ 2] = F7SEG[ ord( dd[1] ) ]
        self.bdisp[ 4] = 0x0f														# °
        self.bdisp[ 6] = F7SEG[ ord( '[' ) ] | ( 0x0 if not ddots else 0x80 )		# C
        self.bdisp[ 8] = F7SEG[ ord( dd[2] ) ]
        self.bdisp[10] = F7SEG[ ord( dd[3] ) ]
        self.bdisp[12] = F7SEG[ ord( 'P' ) ]
        self.bdisp[14] = F7SEG[ ord( 'c' ) ]
