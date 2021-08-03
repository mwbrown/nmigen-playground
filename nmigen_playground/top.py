
from nmigen import *
from .boards.de2_115 import DE2_115Platform
from .display.seven_seg import *

__all__ = ['DE2_115Top']

class DE2_115Top(Elaboratable):

    NUM_SWITCHES = 18

    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        # Request switches and red LEDs

        sws  = [platform.request('switch', i) for i in range(self.NUM_SWITCHES)]
        led_r = platform.request('led_r')
        led_g = platform.request('led_g')
        seg0 = platform.request('display_7seg', 0)

        seg0_hex = SevenSegHex(seg0)
        m.submodules += seg0_hex

        m.d.comb += [
            seg0_hex.val.eq(Cat(sws[0], sws[1], sws[2], sws[3])),
            seg0_hex.oe.eq(sws[4]),
        ]

        return m

if __name__ == '__main__':
    module = DE2_115Top()
    plat = DE2_115Platform()

    plat.build(module, do_program=True)
