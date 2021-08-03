
from nmigen import *

HEX_VALS = [
    # MSB-LSB
    # abcdefg
    0b1111110, # 0
    0b0110000, # 1
    0b1101101, # 2
    0b1111001, # 3
    0b0110011, # 4
    0b1011011, # 5
    0b1011111, # 6
    0b1110000, # 7
    0b1111111, # 8
    0b1111011, # 9
    0b1110111, # A
    0b0011111, # b
    0b1001110, # C
    0b0111101, # d
    0b1001111, # E
    0b1000111, # F
]

Memory

class SevenSegHex(Elaboratable):

    def __init__(self, disp_7seg):

        # Expects to be Display7SegResource requested at top level
        self.disp = disp_7seg

        # Signals
        self.val = Signal(4)
        self.oe = Signal(reset=1)

        self.ports = [
            self.val,
            self.oe,
        ]

    def elaborate(self, platform):
        m = Module()

        mem = Memory(width=7, depth=16, init=HEX_VALS, name='Hex7Seg')
        mem_rd = mem.read_port(domain="comb")
        m.submodules += mem_rd

        segs = Cat(self.disp.g, self.disp.f, self.disp.e, self.disp.d, self.disp.c, self.disp.b, self.disp.a)

        m.d.comb += mem_rd.addr.eq(self.val)

        with m.If(self.oe):
            m.d.comb += segs.eq(mem_rd.data)
        with m.Else():
            m.d.comb += segs.eq(0)

        return m