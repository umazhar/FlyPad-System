from pyftdi.serialext import serial_for_url
import time

# Device URL and serial parameters
device_url = 'ftdi://0x0403:0x6015:FTWCKS5Q/1'  
baudrate = 9600

# Constants from C++ 
NUM_DATAVALS_PER_ARENA = 4
NUM_ARENAS = 16
NUM_DATAFRAME_VALUES = 64
NUM_HISTORIC_VALUES = 30
MAX_CAPDAC_VALUE = 4095
BYTES_PER_ARENA = 20
FULL_PACKET_SIZE = 320
INVALID_DEVICE_DATA = 0x3F  # 63 in decimal
LED_GRAPHICAL_SCALE = 2000
NUM_ARENAS_PER_GUI_ROW = 6

def send_start_command(ftdi_serial):
    start_command = b'G'  # Start command is 'G'
    ftdi_serial.write(start_command)
    print("Start command sent to the device.")

def send_stop_command(ftdi_serial):
    stop_command = b'S'  # Stop command is 'S'
    ftdi_serial.write(stop_command)
    print("Stop command sent to the device.")

def test_serial_read():
    try:
        # Open the FTDI device
        ftdi_serial = serial_for_url(device_url, baudrate=baudrate, timeout=1)
        print("FTDI serial port opened successfully.")
        ftdi_obj = ftdi_serial.ftdi
        ftdi_obj.reset()
        print("FTDI device reset.")
        send_start_command(ftdi_serial)

        while True:
            # Read the full packet size
            packet = ftdi_serial.read(FULL_PACKET_SIZE)
            if packet:
                if len(packet) == FULL_PACKET_SIZE:
                    # Parse and display the received data
                    data_values = parse_data_packet(packet)
                    print(f"Parsed Data: {data_values}")
                else:
                    print(f"Incomplete packet received: expected {FULL_PACKET_SIZE} bytes, got {len(packet)} bytes.")
            else:
                print("No data received.")
            time.sleep(0.1) 
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Send the stop command and close the serial connection
        if 'ftdi_serial' in locals() and ftdi_serial:
            send_stop_command(ftdi_serial)
            ftdi_serial.close()
            print("FTDI serial port closed.")

def parse_data_packet(packet):
    data_values = []
    packet_size = len(packet)

    for i in range(0, packet_size, BYTES_PER_ARENA):
        # Check index bounds
        if i + BYTES_PER_ARENA > packet_size:
            print("Incomplete arena data received.")
            print(f"Bytes per arena is: {BYTES_PER_ARENA}")
            print(f"Packet size is: {packet_size}")

            break

        if packet[i + 18] != INVALID_DEVICE_DATA:
            value0 = ((packet[i + 1] << 8) | packet[i + 2]) >> 4
            value1 = ((packet[i + 3] << 8) | packet[i + 4]) >> 4
            value2 = (packet[i + 5] & 0b00000001) * LED_GRAPHICAL_SCALE
            value3 = ((packet[i + 5] & 0b00000010) >> 1) * LED_GRAPHICAL_SCALE
        else:
            value0 = value1 = value2 = value3 = -1
        data_values.extend([value0, value1, value2, value3])

    return data_values

if __name__ == "__main__":
    test_serial_read()
