
from nmigen import *
from nmigen.build import *

__all__ = ["MIPS_EJTAGResource"]

# On the DE2-115, JP4 is a 14-pin connector used with a particular 
# JTAG pinout, noted by Terasic to be for MIPS:
#
#    1    2
# TRST  GND
#  TDI  GND
#  TDO  GND
#  TMS  GND
#  TCK  GND
#  RST  GND/KEY
# DINT  VRef 
#   13   14
#
# On actual connectors, pin 12 is supposed to be a key pin.
# On the DE2-115, this is GND.
#
def MIPS_EJTAGResource():

    conn = ("ex_io", 0)
    return Resource("mips_ejtag", 0, # FIXME dir on pins
        Subsignal("trst", PinsN( "1", dir="i", conn=conn)),
        Subsignal("tdi",  Pins(  "3", dir="i", conn=conn)),
        Subsignal("tdo",  Pins(  "5", dir="o", conn=conn)),
        Subsignal("tms",  Pins(  "7", dir="i", conn=conn)),
        Subsignal("tck",  Pins(  "9", dir="i", conn=conn)),
        Subsignal("rst",  PinsN("11", dir="i", conn=conn)),
        Subsignal("dint", Pins( "13", dir="i", conn=conn)),
        Attrs(io_standard="3.3-V LVTTL"))
