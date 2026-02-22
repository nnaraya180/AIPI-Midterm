"""
flex_mcp3008.py
---------------
Small MCP3008 + flex helper functions (class-style).
One job: read an analog channel (flex sensor via voltage divider).
"""

# Globals (created once)
_spi = None
_cs = None
_mcp = None
_ch0 = None


def setup_mcp3008(cs_pin="D8"):
    """
    Setup MCP3008 once.
    Default CS is CE0 (board.D8).
    """
    global _spi, _cs, _mcp, _ch0
    
    if _mcp is not None:
        return

    import board
    import busio
    import digitalio
    import adafruit_mcp3xxx.mcp3008 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn

    _spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # CS pin: "D8" (CE0) or "D7" (CE1)
    cs_board_pin = getattr(board, cs_pin)
    _cs = digitalio.DigitalInOut(cs_board_pin)

    _mcp = MCP.MCP3008(_spi, _cs)
    _ch0 = AnalogIn(_mcp, MCP.P0)  # CH0


def read_flex_raw():
    """
    Read raw ADC value (0..65535-ish scaling from library).
    """
    setup_mcp3008()
    return int(_ch0.value)


def read_flex_voltage():
    """
    Read flex voltage in Volts (0.0..~3.3).
    """
    setup_mcp3008()
    return float(_ch0.voltage)
