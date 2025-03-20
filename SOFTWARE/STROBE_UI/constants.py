#!/usr/bin/env python3

"""
STROBE - Constants
"""

# Arena settings
NUM_ARENAS = 16
NUM_DATAVALS_PER_ARENA = 4
NUM_DATAFRAME_VALUES = NUM_ARENAS * NUM_DATAVALS_PER_ARENA
NUM_HISTORIC_VALUES = 100 # hw sends data at 10Hz, 100 readings/10Hz = 10s of data
MAX_CAPDAC_VALUE = 4095
LED_GRAPHICAL_SCALE = 2000

# FTDI stuff
BYTES_PER_ARENA = 20
FULL_PACKET_SIZE = BYTES_PER_ARENA * NUM_ARENAS
INVALID_DEVICE_DATA = 0x3F
FTDI_READ_TIMEOUT = 5000
FTDI_WRITE_TIMEOUT = 1000

# Sip thresholds
LEFT_SIP_THRESHOLD = 1300
RIGHT_SIP_THRESHOLD = 1300

"""
Sip Detection Constants

at 10z, 1 = 100 ms 
"""
MIN_THRESHOLD = 30 # Y change to trigger a potential sip
MIN_SIP_TIME = 5
COOLDOWN_TIME = 10


'''
Arena Descriptions
--------------------------------
  Arena    Year   Baseline
 Arena 1   2020      2000
 Arena 2   2020      2050
 Arena 3   2021      2060
 Arena 4   2021      2070
 Arena 5   2022      2050
 Arena 6   2022      2050
 Arena 7   2023      1300
 Arena 8   2023      1250
 Arena 9   2024      1000
 Arena 10  2024      1000
 Arena 11  2025      1000
 Arena 12  2025      1000
 Arena 13  2026      1000
 Arena 14  2026      1000
 Arena 15  2027      1000
 Arena 16  2027      1000
--------------------------------
'''