
from nmigen import *

HEX_VALS = [
    #   MSB-LSB
    #   abcdefg
    C(0b1111110, unsigned(7)), # 0
    C(0b0110000, unsigned(7)), # 1
    C(0b1101101, unsigned(7)), # 2
    C(0b1111001, unsigned(7)), # 3
    C(0b0110011, unsigned(7)), # 4
    C(0b1011011, unsigned(7)), # 5
    C(0b1011111, unsigned(7)), # 6
    C(0b1110000, unsigned(7)), # 7
    C(0b1111111, unsigned(7)), # 8
    C(0b1111011, unsigned(7)), # 9
    C(0b1110111, unsigned(7)), # A
    C(0b0011111, unsigned(7)), # b
    C(0b1001110, unsigned(7)), # C
    C(0b0111101, unsigned(7)), # d
    C(0b1001111, unsigned(7)), # E
    C(0b1000111, unsigned(7)), # F
]

class SevenSegHex(Elaboratable):

    def __init__(self, res_7seg):

        # Expects to be Display7SegResource requested at top level
        self.res_7seg = res_7seg

        # Signals
        self.val = Signal(4)
        self.oe = Signal()

        self.ports = [
            self.val,
            self.oe,
        ]

    def elaborate(self, platform):
        m = Module()

        with m.If(self.oe):
            with m.Switch(self.val):
                for value, decoded in enumerate(HEX_VALS):
                    with m.Case(value):
                        m.d.comb += [
                            self.res_7seg.a.eq(decoded[6]),
                            self.res_7seg.b.eq(decoded[5]),
                            self.res_7seg.c.eq(decoded[4]),
                            self.res_7seg.d.eq(decoded[3]),
                            self.res_7seg.e.eq(decoded[2]),
                            self.res_7seg.f.eq(decoded[1]),
                            self.res_7seg.g.eq(decoded[0]),
                        ]
        with m.Else():
            m.d.comb += [
                self.res_7seg.a.eq(0),
                self.res_7seg.b.eq(0),
                self.res_7seg.c.eq(0),
                self.res_7seg.d.eq(0),
                self.res_7seg.e.eq(0),
                self.res_7seg.f.eq(0),
                self.res_7seg.g.eq(0),
            ]

        return m