#!/usr/bin/env python3

"""
STROBE - Data acquisition module
"""

import time
import threading
import numpy as np
import serial
import serial.tools.list_ports
import platform
import sys

from constants import *

try:
    import ftd2xx as ftd
    FTDIRECT_AVAILABLE = True
except ImportError:
    FTDIRECT_AVAILABLE = False

class FTDIConnection:    
    @staticmethod
    def scan_ports():
        ftdi_ports = []
        all_ports = []
        
        # First try direct FTDI detection using ftd2xx if available
        if FTDIRECT_AVAILABLE:
            try:
                print("DEBUG - Scanning for FTDI devices using D2XX API...")
                device_count = ftd.createDeviceInfoList()
                print(f"Found {device_count} D2XX devices")
                
                for i in range(device_count):
                    try:
                        dev_info = ftd.getDeviceInfoDetail(i)
                        print(f"D2XX Device {i}: {dev_info}")
                        
                        # Format the info like we do with serial ports
                        device_name = f"FTDI:{i}"
                        description = dev_info['description'].decode('utf-8', errors='replace')
                        serial_num = dev_info['serial'].decode('utf-8', errors='replace')
                        
                        port_info = {
                            "device": device_name,
                            "description": description,
                            "display": f"{device_name} - {description} ({serial_num})",
                            "d2xx_index": i,
                            "is_d2xx": True
                        }
                        
                        # Add to both lists - this is an FTDI device by definition when using ftd2xx
                        ftdi_ports.append(port_info)
                        all_ports.append(port_info)
                        
                        print(f"Added D2XX device: {port_info['display']}")
                    except Exception as e:
                        print(f"Error getting D2XX device info for index {i}: {e}")
            except Exception as e:
                print(f"Error scanning D2XX devices: {e}")
        
        # Also scan for virtual COM ports using PySerial
        try:
            print(f"DEBUG - Scanning serial ports on {platform.system()}...")
            available_ports = list(serial.tools.list_ports.comports())
            print(f"Found {len(available_ports)} serial ports")
            
            # Common FTDI identifiers and the specific model we're looking for
            ftdi_identifiers = ["FTDI", "FT", "USB SERIAL"]
            ftdi_vendors = ['0403']  # FTDI's vendor ID is 0403
            specific_model = "UMFT240XA"  # The specific model used in the original code
            
            for port in available_ports:
                # Create port info for all ports
                port_info = {
                    "device": port.device,
                    "description": port.description,
                    "display": f"{port.device} - {port.description}",
                    "hwid": port.hwid,
                    "is_d2xx": False
                }
                
                print(f"Serial Port: {port.device}, Desc: {port.description}, HWID: {port.hwid}")
                all_ports.append(port_info)
                
                # Check multiple possible identifiers for FTDI devices
                is_ftdi = False
                
                # Check for the specific model first (highest priority)
                if specific_model in port.description:
                    is_ftdi = True
                    print(f"Detected specific FTDI model '{specific_model}': {port.device}")
                
                # Check description for any FTDI identifiers
                elif any(id_str in port.description.upper() for id_str in ftdi_identifiers):
                    is_ftdi = True
                    print(f"Detected FTDI by description: {port.device}")
                    
                # Check hardware ID for FTDI vendor ID
                elif any(vid in port.hwid.upper() for vid in ftdi_vendors):
                    is_ftdi = True
                    print(f"Detected FTDI by vendor ID: {port.device}")
                
                if is_ftdi:
                    ftdi_ports.append(port_info)
        except Exception as e:
            print(f"Error scanning serial ports: {e}")
        
        # If we didn't find any FTDI ports but there are ports available
        if not ftdi_ports and all_ports:
            print("WARNING: No FTDI devices detected. Displaying all available ports.")
        elif not all_ports:
            print("WARNING: No ports detected at all. Check device connection and drivers.")
        
        return ftdi_ports, all_ports
    
    @staticmethod
    def setup_device(port_info):
        # Check if this is a D2XX device or a serial port
        if isinstance(port_info, str):
            port_name = port_info
            if " - " in port_name: # Legacy support, assume its a string if we get -
                port_name = port_name.split(" - ")[0].strip()
            
            return FTDIConnection._setup_serial_device(port_name)
        elif isinstance(port_info, dict) and port_info.get("is_d2xx", False):
            # It's a D2XX device
            return FTDIConnection._setup_d2xx_device(port_info["d2xx_index"])
        else:
            # It's a serial port
            device = port_info["device"]
            return FTDIConnection._setup_serial_device(device)
    
    @staticmethod
    def _setup_d2xx_device(device_index):
        if not FTDIRECT_AVAILABLE:
            print("ERROR: ftd2xx library not available but trying to use D2XX device")
            return False, None
        
        try:
            print(f"Opening D2XX device at index {device_index}")
            device = ftd.open(device_index)
            device.resetDevice()
            device.setBitMode(0, 0)  # Reset to normal UART mode
            device.setTimeouts(FTDI_READ_TIMEOUT, FTDI_WRITE_TIMEOUT)
            device.setLatencyTimer(D2XX_LATENCY) 
            device.setBaudRate(9600)
            device.setDataCharacteristics(8, 0, 0)  # 8 bits, no parity, 1 stop bit
            
            print(f"Connected to D2XX device at index {device_index}")
            
            return True, device
            
        except Exception as e:
            print(f"D2XX Device Error: {str(e)}")
            return False, None
    
    @staticmethod
    def _setup_serial_device(port_name):
        try:
            print(f"Attempting to connect to serial port: {port_name}")
            
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
            
            print(f"Connected to serial port: {port_name}, Baud: {serial_port.baudrate}")
            
            return True, serial_port
            
        except Exception as e:
            print(f"Serial Port Error: {str(e)}")
            return False, None

class DataReaderThread(threading.Thread):    
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue
        self.is_running = True
        self.daemon = True
    
    def stop(self):
        self.is_running = False

class FTDIDataReader(DataReaderThread):    
    def __init__(self, data_queue, device):
        super().__init__(data_queue)
        self.device = device
        self.is_d2xx = hasattr(device, 'read') and hasattr(device, 'write') and not hasattr(device, 'in_waiting')
        self.error_count = 0
        self.max_errors = 5  # Maximum consecutive errors before trying to reconnect
        
        if self.is_d2xx:
            self.device_name = "D2XX Device"
        else:
            self.device_name = device.port
    
    def run(self):
        try:
            # Start command
            START_COMMAND = b"G"
            if self.is_d2xx:
                self.device.write(START_COMMAND)
            else:
                self.device.write(START_COMMAND)
                self.device.flush()
            
            time.sleep(0.1)
            
            while self.is_running:
                try:
                    if self.is_d2xx:
                        packet = self.device.read(FULL_PACKET_SIZE)
                    else:
                        packet = self.device.read(FULL_PACKET_SIZE)
                    
                    if len(packet) != FULL_PACKET_SIZE:
                        print(f"Bad packet: {len(packet)} bytes")
                        self.error_count += 1
                        if self.error_count >= self.max_errors:
                            print(f"Too many errors, resetting device...")
                            if self.is_d2xx:
                                self.device.resetDevice()
                                time.sleep(0.5)
                            self.error_count = 0
                        continue
                    self.error_count = 0
                    
                    arena_values_left = []
                    arena_values_right = []
                    
                    for i in range(0, BYTES_PER_ARENA * NUM_ARENAS, BYTES_PER_ARENA):
                        arena_index = i // BYTES_PER_ARENA
                        # CAPDAC Black magic
                        # From old C++ code, i have no idea how this works tbh but it works so not going to touch it :D
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
                    print(f"Device read error: {e}")
                    self.error_count += 1
                    # If too many errors, try to reset
                    if self.error_count >= self.max_errors:
                        print(f"Too many errors, resetting device...")
                        if self.is_d2xx:
                            self.device.resetDevice()
                            time.sleep(0.5)
                        self.error_count = 0
                    
                    time.sleep(0.5)  # Longer delay when error occurs
            
            # Send stop
            try:
                STOP_COMMAND = b"S"
                if self.is_d2xx:
                    self.device.write(STOP_COMMAND)
                else:
                    self.device.write(STOP_COMMAND)
                    self.device.flush()
            except:
                pass  # Ignore errors when stopping
            
        except Exception as e:
            print(f"Thread error: {e}")
        finally:
            if self.device:
                try:
                    if self.is_d2xx:
                        self.device.close()
                    else:
                        self.device.close()
                except:
                    pass

class SimulatedDataReader(DataReaderThread):
    
    def run(self):
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