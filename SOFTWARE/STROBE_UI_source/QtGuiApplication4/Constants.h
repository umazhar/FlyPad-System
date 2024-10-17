#pragma once

// error codes
const int NO_FTDI_ERROR_CODE = 5;
const int CANNOT_OPEN_FTDI_DEVICE_ERROR_CODE = 6;
const int FTDI_RESET_ERROR_CODE = 7;
const int FTDI_WRITE_IO_ERROR_CODE = 8;
const int FTDI_READ_IO_ERROR_CODE = 9;

// FTDI constants
const int FTDI_READ_TIMEOUT = 5000;
const int FTDI_WRITE_TIMEOUT = 1000;

// system-specific constants
const int NUM_DATAVALS_PER_ARENA = 4;
const int NUM_ARENAS = 16;
const int NUM_DATAFRAME_VALUES = 64;
const int NUM_HISTORIC_VALUES = 30;
const int MAX_CAPDAC_VALUE = 4095;
const int BYTES_PER_ARENA = 20;
const int FULL_PACKET_SIZE = 320;
const int INVALID_DEVICE_DATA = 0x3F;

// GUI constants
const int LED_GRAPHICAL_SCALE = 2000;
const int NUM_ARENAS_PER_GUI_ROW = 6;