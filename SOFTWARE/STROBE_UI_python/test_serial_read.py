import tkinter as tk
from pyftdi.serialext import serial_for_url
import time

# --------------------------
# Configuration
# --------------------------
DEVICE_URL = 'ftdi://0x0403:0x6015:FTWCKS5Q/1'
BAUDRATE = 9600
TIMEOUT = 1.0

NUM_ARENAS = 16
BYTES_PER_ARENA = 20
FULL_PACKET_SIZE = 320
INVALID_DEVICE_DATA = 0x3F
LED_GRAPHICAL_SCALE = 2000

# --------------------------
# Parse Packet Function
# --------------------------
def parse_data_packet(packet):
    """Parses one 320-byte packet into a list of 16 arenas, each with 4 values."""
    data_values = []
    if len(packet) < FULL_PACKET_SIZE:
        # Return a list of 16 arenas, each = [-1, -1, -1, -1] if incomplete
        return [[-1, -1, -1, -1] for _ in range(NUM_ARENAS)]
    
    # Each arena is 20 bytes
    for i in range(0, FULL_PACKET_SIZE, BYTES_PER_ARENA):
        # If the device marks it invalid
        if packet[i + 18] == INVALID_DEVICE_DATA:
            data_values.append([-1, -1, -1, -1])
        else:
            # Example from your parse_data_packet in the snippet:
            value0 = ((packet[i + 1] << 8) | packet[i + 2]) >> 4
            value1 = ((packet[i + 3] << 8) | packet[i + 4]) >> 4
            value2 = (packet[i + 5] & 0b00000001) * LED_GRAPHICAL_SCALE
            value3 = ((packet[i + 5] & 0b00000010) >> 1) * LED_GRAPHICAL_SCALE
            data_values.append([value0, value1, value2, value3])

    return data_values

# --------------------------
# FTDI Device Handling
# --------------------------
def send_start_command(ftdi_serial):
    try:
        ftdi_serial.write(b'G')  # 'G' for Start
    except Exception as e:
        print(f"Error sending start command: {e}")

def send_stop_command(ftdi_serial):
    try:
        ftdi_serial.write(b'S')  # 'S' for Stop
    except Exception as e:
        print(f"Error sending stop command: {e}")

# --------------------------
# Main GUI Application
# --------------------------
class FlypadViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flypad Viewer")
        
        # Frame to hold all arena panels
        self.arena_frames = []
        self.arena_labels = []  # Will hold lists of 4 labels each
        
        # Create a 4x4 or other layout so 16 arenas can be shown
        # (You can adapt the layout as needed)
        rows = 4
        cols = 4
        
        for r in range(rows):
            for c in range(cols):
                arena_index = r * cols + c
                frame = tk.LabelFrame(root, text=f"Arena {arena_index}", padx=5, pady=5)
                frame.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
                
                # Create 4 labels inside each arena frame
                label_list = []
                for i in range(4):
                    lbl = tk.Label(frame, text="ValueX", width=12)
                    lbl.pack(anchor=tk.W)
                    label_list.append(lbl)
                
                self.arena_frames.append(frame)
                self.arena_labels.append(label_list)
        
        # Attempt to open FTDI
        self.ftdi_serial = None
        try:
            self.ftdi_serial = serial_for_url(DEVICE_URL, baudrate=BAUDRATE, timeout=TIMEOUT)
            print("FTDI serial port opened successfully.")
            # Reset the device once
            self.ftdi_serial.ftdi.reset()
            time.sleep(0.1)
            send_start_command(self.ftdi_serial)
        except Exception as e:
            print(f"Could not open FTDI device: {e}")
        
        # Start polling for data
        # We'll poll every 100 ms (0.1 s)
        self.poll_data()
    
    def poll_data(self):
        """Periodic function that reads from FTDI and updates the GUI."""
        if self.ftdi_serial is not None:
            try:
                packet = self.ftdi_serial.read(FULL_PACKET_SIZE)
                if packet:
                    arenas = parse_data_packet(packet)  # 16 sub-lists of 4 values each
                    self.update_arena_labels(arenas)
            except Exception as e:
                print(f"Error reading FTDI data: {e}")
        
        # Schedule next poll in 100 ms
        self.root.after(100, self.poll_data)
    
    def update_arena_labels(self, arenas):
        """
        Given a list of 16 sub-lists (each has 4 values),
        update the label text for each arena.
        """
        for i in range(NUM_ARENAS):
            # arenas[i] is [value0, value1, value2, value3]
            values = arenas[i]
            for j in range(4):
                self.arena_labels[i][j].config(text=f"Val{j}: {values[j]}")
    
    def stop_device(self):
        """Stop device if open and close the port."""
        if self.ftdi_serial:
            send_stop_command(self.ftdi_serial)
            try:
                self.ftdi_serial.close()
            except:
                pass
            self.ftdi_serial = None

def main():
    root = tk.Tk()
    app = FlypadViewerApp(root)
    
    # When user closes the window
    def on_closing():
        app.stop_device()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
