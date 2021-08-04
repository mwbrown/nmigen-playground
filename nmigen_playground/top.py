
from nmigen import *
from .boards.de2_115 import DE2_115Platform
from .display.seven_seg import *
from .extensions.mips_ejtag import *

__all__ = ['DE2_115Top']

class DE2_115Top(Elaboratable):

    NUM_SWITCHES = 18
    NUM_7SEG = 8

    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        # Request switches and red LEDs

        sws  = [platform.request('switch', i) for i in range(self.NUM_SWITCHES)]
        led_r = platform.request('led_r')
        led_g = platform.request('led_g')

        ejtag = platform.request('mips_ejtag')

        segs_hex = [SevenSegHex(platform.request('display_7seg', i)) for i in range(self.NUM_7SEG)]
        m.submodules += segs_hex

        # Default unused displays are off
        m.d.comb += [segs_hex[i].oe.eq(0) for i in range(self.NUM_7SEG)]

        # Assign the first eight switches to the 7seg displays
        m.d.comb += [
            segs_hex[0].val.eq(Cat(sws[0:0+4])),
            segs_hex[1].val.eq(Cat(sws[4:4+4])),

            segs_hex[0].oe.eq(1),
            segs_hex[1].oe.eq(1),
        ]

        return m

if __name__ == '__main__':
    module = DE2_115Top()
    plat = DE2_115Platform()
    plat.add_resources([MIPS_EJTAGResource()])

    plat.build(module, do_program=True)
