#!/usr/bin/env python3

"""
STROBE - Data acquisition module
"""

import time
import threading
import numpy as np
import serial
import serial.tools.list_ports

from constants import *

class FTDIConnection:
    """Handles FTDI device connection"""
    
    @staticmethod
    def scan_ports():
        """Find available FTDI devices"""
        available_ports = list(serial.tools.list_ports.comports())
        
        ftdi_ports = []
        all_ports = []
        
        for port in available_ports:
            port_info = {
                "device": port.device,
                "description": port.description,
                "display": f"{port.device} - {port.description}"
            }
            all_ports.append(port_info)
            
            if "FTDI" in port.description or "FT" in port.description:
                ftdi_ports.append(port_info)
        
        return ftdi_ports, all_ports
    
    @staticmethod
    def setup_device(port_name):
        """Connect to device"""
        try:
            if " - " in port_name:
                port_name = port_name.split(" - ")[0].strip()
            
            serial_port = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=FTDI_READ_TIMEOUT/1000,
                write_timeout=FTDI_WRITE_TIMEOUT/1000
            )
            
            serial_port.reset_input_buffer()
            serial_port.reset_output_buffer()
            
            print(f"Connected: {port_name}, Baud: {serial_port.baudrate}")
            
            return True, serial_port
            
        except Exception as e:
            print(f"FTDI Error: {str(e)}")
            return False, None

class DataReaderThread(threading.Thread):
    """Base class for readers"""
    
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue
        self.is_running = True
        self.daemon = True
    
    def stop(self):
        self.is_running = False

class FTDIDataReader(DataReaderThread):
    """Reads from actual hardware"""
    
    def __init__(self, data_queue, serial_port):
        super().__init__(data_queue)
        self.serial_port = serial_port
    
    def run(self):
        """Read data from device"""
        try:
            # Start command
            START_COMMAND = b"G"
            self.serial_port.write(START_COMMAND)
            self.serial_port.flush()
            time.sleep(0.1)
            
            while self.is_running:
                try:
                    packet = self.serial_port.read(FULL_PACKET_SIZE)
                    
                    if len(packet) != FULL_PACKET_SIZE:
                        print(f"Bad packet: {len(packet)} bytes")
                        continue
                    
                    arena_values_left = []
                    arena_values_right = []
                    
                    for i in range(0, BYTES_PER_ARENA * NUM_ARENAS, BYTES_PER_ARENA):
                        arena_index = i // BYTES_PER_ARENA
                        
                        if packet[i + 18] != INVALID_DEVICE_DATA:
                            capdac1 = int(((packet[i + 1] << 8) | packet[i + 2]) >> 4)
                            capdac2 = int(((packet[i + 3] << 8) | packet[i + 4]) >> 4)
                            
                            arena_values_left.append(capdac1)
                            arena_values_right.append(capdac2)
                        else:
                            arena_values_left.append(0)
                            arena_values_right.append(0)
                    
                    self.data_queue.put((arena_values_left, arena_values_right))
                    
                except Exception as e:
                    print(f"Serial error: {e}")
                    time.sleep(0.1)
            
            # Send stop
            STOP_COMMAND = b"S"
            self.serial_port.write(STOP_COMMAND)
            self.serial_port.flush()
            
        except Exception as e:
            print(f"Thread error: {e}")
        finally:
            if self.serial_port:
                try:
                    self.serial_port.close()
                except:
                    pass

class SimulatedDataReader(DataReaderThread):
    """Generates fake data for testing"""
    
    def run(self):
        """Generate simulated data"""
        try:
            while self.is_running:
                left_values = []
                right_values = []
                
                for _ in range(NUM_ARENAS):
                    r = np.random.random()
                    left_val = 0
                    right_val = 0
                    
                    if r < 0.50:
                        # No sip
                        left_val = np.random.uniform(50, 200)
                        right_val = np.random.uniform(50, 200)
                    elif r < 0.75:
                        # Left sip
                        left_val = np.random.uniform(50, 200)
                        right_val = np.random.uniform(LEFT_SIP_THRESHOLD+50, LEFT_SIP_THRESHOLD+500)
                    else:
                        # Right sip
                        left_val = np.random.uniform(RIGHT_SIP_THRESHOLD+50, RIGHT_SIP_THRESHOLD+500)
                        right_val = np.random.uniform(50, 200)
                    
                    left_values.append(left_val)
                    right_values.append(right_val)
                
                self.data_queue.put((left_values, right_values))
                time.sleep(0.1)
        except Exception as e:
            print(f"Sim error: {e}")