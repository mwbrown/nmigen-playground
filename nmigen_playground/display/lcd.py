from nmigen import *

__all__ = ["LcdHD44780"]

DATA_WIDTH = 8

SETUP_CLOCKS  = 5
HOLD_CLOCKS   = 20
MAX_DELAY     = 50 * 1000 * 5 # Five milliseconds

# Comb decoder to turn a data or command into however many clocks the write should take
class LcdDelayDecoder(Elaboratable):

    def __init__(self):

        self.data = Signal(DATA_WIDTH)
        self.rs = Signal()

        self.delay_clks = Signal(range(MAX_DELAY))

        self.ports = [
            self.data,
            self.rs,
            self.delay_clks,
        ]

    def elaborate(self, platform):

        m = Module()

        # TODO: decode different delays depending on datasheet values
        m.d.comb += self.delay_clks.eq(MAX_DELAY)

        return m


class LcdController(Elaboratable):

    def __init__(self):
        pass

        # 8 bit data + RS signal (1=char, 0=cmd)
        self.data = Signal(DATA_WIDTH + 1)
        self.start = Signal()
        self.ready = Signal()

        self.lcd_data = Signal(DATA_WIDTH)
        self.lcd_en   = Signal()
        self.lcd_rs   = Signal()

        self.ports = [
            self.data,
            self.start,
            self.ready,

            self.lcd_data,
            self.lcd_en,
            self.lcd_rs,
        ]

        # Internal State

        self.delay_ctr = Signal(range(MAX_DELAY * 4)) # TODO: figure out clock rate

    def elaborate(self, platform):
        m = Module()

        # Split out the RS/DATA signals.
        lcd_data   = self.data[:DATA_WIDTH]
        lcd_rs     = self.data[DATA_WIDTH]
        delay_done = self.delay_ctr == 0

        # Instantiate the delay decoder.
        delay_decoder = LcdDelayDecoder()
        m.submodules += delay_decoder
        m.d.comb += [
            delay_decoder.data.eq(lcd_data),
            delay_decoder.rs.eq(lcd_rs),
        ]

        # Default signal assignments unless overridden in the FSM.
        m.d.comb += self.ready.eq(0)

        # If delay line is non-zero, decrement it.
        # This is used to advance to the next state
        with m.If(self.delay_ctr > 0):
            m.d.sync += self.delay_ctr.eq(self.delay_ctr - 1)

        with m.FSM():
            with m.State('IDLE'):
                m.d.comb += self.ready.eq(delay_done & ~self.start)
                with m.If(self.start & delay_done):
                    # Set up a new transaction. En isn't pulsed until the next
                    m.next = 'SETUP'
                    m.d.sync += [
                        self.delay_ctr.eq(SETUP_CLOCKS),
                        self.lcd_data.eq(lcd_data),
                        self.lcd_rs.eq(lcd_rs),
                    ]

            with m.State('SETUP'):
                with m.If(delay_done):
                    m.next = 'HOLD'
                    m.d.sync += [
                        self.delay_ctr.eq(HOLD_CLOCKS),
                        self.lcd_en.eq(1),
                    ]

            with m.State('HOLD'):
                with m.If(delay_done):
                    m.next = 'IDLE'
                    m.d.sync += [
                        self.delay_ctr.eq(delay_decoder.delay_clks),
                        self.lcd_en.eq(0),
                    ]

        return m


class LcdHD44780(Elaboratable):

    def __init__(self, *, print_test_text=False):

        self.lcd_data = Signal(DATA_WIDTH)
        self.lcd_en   = Signal()
        self.lcd_rs   = Signal()

        self.ports = [

            # TODO user ports.

            # Hardware ports.
            self.lcd_data,
            self.lcd_en,
            self.lcd_rs,
        ]

        self.LCD_INIT = [
            0x038, # Function set (8-bit, 2 lines, 5x8)
            0x00C, # Display On, cursor off, blinking off
            0x001, # Clear display
            0x006, # Cursor increment, no shift

            0x080, # Set DDRAM to 0x00 (start of first line)
        ]

        if print_test_text:
            from nmigen import __version__ as nmigen_version_str

            def enc_str(s):
                chars = [0x100 + ord(c) for c in s]

                if len(chars) > 16:
                    print('Warning: truncating enc_str()')

                return chars[:16]

            version_split = nmigen_version_str.split('+')
            nm_version = version_split[0]
            nm_gitrev  = version_split[1]

            self.LCD_INIT.extend([
                #0x080,
                *enc_str('nMigen {}'.format(nm_gitrev)),

                0x0C0,
                *enc_str(nm_version)
            ])

        self.init = Signal()
        self.init_idx = Signal(range(len(self.LCD_INIT)))

    def elaborate(self, platform):
        m = Module()

        # Instantiate the low-level LCD controller.
        cont = LcdController()
        m.submodules += cont

        # Static connections to low-level controller.
        m.d.comb += [
            self.lcd_en.eq(cont.lcd_en),
            self.lcd_data.eq(cont.lcd_data),
            self.lcd_rs.eq(cont.lcd_rs),
        ]

        # Instantiate the initialization code ROM.
        init_rom = Memory(width=DATA_WIDTH+1, depth=len(self.LCD_INIT), init=self.LCD_INIT).read_port(domain='comb')
        m.submodules += init_rom

        m.d.comb += init_rom.addr.eq(self.init_idx)
        m.d.comb += self.init.eq(self.init_idx < len(self.LCD_INIT))

        # Default value for start at every clock cycle.
        m.d.sync += cont.start.eq(0)

        with m.If(self.init):
            # Handle the initialization process.

            # Are we ready for the next transaction?
            with m.If(cont.ready):
                m.d.sync += [
                    cont.data.eq(init_rom.data),
                    cont.start.eq(1),
                    self.init_idx.eq(self.init_idx + 1),
                ]

        with m.Else():
            pass # TODO accept user input

        return m

if __name__ == '__main__':
    # Do an initialization simulation.
    from nmigen.sim import *

    # Override the MAX_DELAY to something more reasonable...
    MAX_DELAY = 100

    dut = LcdHD44780()

    def process():

        # Give us enough cycles to complete the initialization.
        MAX_CYCLES = (len(dut.LCD_INIT) * (SETUP_CLOCKS+HOLD_CLOCKS+MAX_DELAY)) + 1000

        for _ in range(MAX_CYCLES):
            yield

    sim = Simulator(dut)
    sim.add_clock(1/50.E6) # Add 50 MHz clock.
    sim.add_sync_process(process)

    with sim.write_vcd('lcd.vcd'):
        sim.run()
