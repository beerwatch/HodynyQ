from micropython import const
import framebuf
from utime import sleep

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Matrix8x8:
    def __init__(self, spi, cs, num, orientation=0):
        """
        CS = Pin(5, Pin.OUT) # GPIO5 pin 7
        CLK = Pin(6) # GPIO6 pin 9
        DIN = Pin(7) # GPIO7 pin 10
        BRIGHTNESS = 3 # from 0 to 15
        
        text = "Hello World!"
        # CLK = GPIO6 and MOSI (DIN) = GPIO7 are the default pins of SPI0 so you can omit it
        spi = SPI(0, baudrate= 10_000_000,  sck=CLK, mosi=DIN)
        display = Matrix8x8(spi, CS, 1, orientation=1)
        display.brightness(BRIGHTNESS)
        display.invert = False
        """
        ORIENTATION_CONST = [framebuf.MONO_VLSB, # Vertical
                             framebuf.MONO_HLSB, # Horizontal
                             framebuf.MONO_HMSB] # Horizontal Mirror
        
        self.orientation = ORIENTATION_CONST[orientation]
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.buffer = bytearray(8 * num)
        self.num = num
        fb = framebuf.FrameBuffer(self.buffer, 8 * num, 8, self.orientation)
        self.framebuf = fb
        # Provide methods for accessing FrameBuffer graphics primitives. This is a workround
        # because inheritance from a native class is currently unsupported.
        # http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
        self.fill = fb.fill  # (col)
        self.pixel = fb.pixel # (x, y[, c])
        self.hline = fb.hline  # (x, y, w, col)
        self.vline = fb.vline  # (x, y, h, col)
        self.line = fb.line  # (x1, y1, x2, y2, col)
        self.rect = fb.rect  # (x, y, w, h, col)
        self.fill_rect = fb.fill_rect  # (x, y, w, h, col)
        self.text = fb.text  # (string, x, y, col=1)
        self.scroll = fb.scroll  # (dx, dy)
        self.blit = fb.blit  # (fbuf, x, y[, key])
        self.invert = False
        self.init()

    def _write(self, command, data):
        self.cs(0)
        for m in range(self.num):
            self.spi.write(bytearray([command, data]))
        self.cs(1)

    def init(self):
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    def show(self):
        for y in range(8):
            self.cs(0)
            for m in range(self.num):
                self.spi.write(bytearray([_DIGIT0 + 7-y, self.buffer[((7 - y ) * self.num) + self.num - 1 - m]]))
            self.cs(1)

    def text_scroll(self, text, delay=0.1):

        text_lenght = len(text) * 8
        for pixel_position in range(text_lenght):
            self.text(text, -pixel_position, 0, 1)
            self.show()
            sleep(delay)
            self.fill(self.invert)
            self.show()

    def one_char_a_time(self, text, delay=0.2):
        # show a string one character at a time

        for char in text:
            self.fill(self.invert)
            self.text(char, 0, 0, 1)
            self.show()
            sleep(delay)
            
        # scroll the last character off the display          
        for i in range(8):
            self.scroll(-1, 0)
            self.show()
            sleep(delay)
        
SEG_7219_STD = [
0x7E,	0x30,	0x6D,	0x79,	0x33,	0x5B,	0x5F,	0x70,	0x7F,	0x7B,	0x77,	0x1F,	0x0D,	0x3D,	0x4F,	0x47,
0xFE,	0xB0,	0xED,	0xF9,	0xB3,	0xDB,	0xDF,	0xF0,	0xFF,	0xFB,	0xF7,	0x9F,	0xCE,	0xBD,	0xCF,	0xC7,
0x00,	0x90,	0x21,	0x01,	0x01,	0x01,	0x01,	0x20,	0x6E,	0x7A,	0x01,	0x01,	0x10,	0x01,	0x80,	0x25,
0x7E,	0x30,	0x6D,	0x79,	0x33,	0x5B,	0x5F,	0x70,	0x7F,	0x7B,	0x04,	0x84,	0x43,	0x09,	0x61,	0xE5,
0x7D,	0x77,	0x1F,	0x0D,	0x3D,	0x4F,	0x47,	0x5E,	0x17,	0x10,	0x38,	0x57,	0x0E,	0x55,	0x15,	0x1D,
0x67,	0x73,	0x05,	0x53,	0x0F,	0x3E,	0x27,	0x2F,	0x37,	0x3B,	0x71,	0x4E,	0x13,	0x78,	0x62,	0x08,
0x03,	0x77,	0x1F,	0x0D,	0x3D,	0x4F,	0x47,	0x5E,	0x17,	0x10,	0x38,	0x57,	0x0E,	0x55,	0x15,	0x1D,
0x67,	0x73,	0x05,	0x53,	0x0F,	0x3E,	0x27,	0x2F,	0x37,	0x3B,	0x71,	0x42,	0x06,	0x18,	0x60,	0x71
]

class SevenSegment:
    def __init__(self, spi, cs, num, ):
        """
        from machine import SPI
        from max7219 import SevenSegment
        CS = Pin(17, Pin.OUT)
        CLK = Pin(18)
        MOSI = Pin(19)
        spi = SPI(0, baudrate= 1_000_000,  sck=CLK, mosi=MOSI)
        display = SevenSegment(spi, CS, 4)
        display.init()
        display.brightness(BRIGHTNESS)
        display.buffer=[1,0x82,3,5]
        display.show()
        """
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.buffer = bytearray(num)
        self.num = num

    def _write(self, command, data):
        self.cs(0)
        self.spi.write(bytearray([command, data]))
        self.cs(1)

    def init(self, decodeBits = 0x0f):
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7 ), # self.num - 1 ),
            (_DECODEMODE, decodeBits),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    def show(self):
        for m in range(self.num):
            self.cs(0)
            self.spi.write(bytearray([_DIGIT0 + m, self.buffer[m] ]))
            self.cs(1)

