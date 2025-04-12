import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports

class LEDControlApp:
    def __init__(self, root):
        self.root = root
        root.title("LED Control")
        root.geometry("500x500")  # Increased height for serial settings

        self.manual = tk.BooleanVar(value=True)
        self.target = tk.StringVar(value="freq")
        self.r_freq = tk.DoubleVar(value=0.0)
        self.r_cur = tk.DoubleVar(value=0.0)
        self.b_freq = tk.DoubleVar(value=0.0)
        self.b_cur = tk.DoubleVar(value=0.0)
        
        # Serial communication variables
        self.serial_port = tk.StringVar()
        self.baud_rate = tk.IntVar(value=9600)
        self.serial_connection = None

        self.build_ui()
        self.update_available_ports()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill='both', expand=True)

        self.add_mode_section(frame)
        self.opt_frame = self.add_opt_section(frame)
        self.param_frame = self.add_param_section(frame)
        self.add_serial_section(frame)
        self.add_buttons(frame)
        self.add_output_section(frame)
        self.status = ttk.Label(frame, text="Ready", wraplength=480)
        self.status.pack(anchor='w', pady=(5, 0))

        self.update_ui()

    def add_mode_section(self, parent):
        mode = ttk.LabelFrame(parent, text="Mode")
        mode.pack(fill='x', pady=5)
        for i, (text, val) in enumerate([("Manual", True), ("Optimization", False)]):
            ttk.Radiobutton(mode, text=text, variable=self.manual, value=val, command=self.update_ui).grid(row=0, column=i, padx=10)

    def add_opt_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Optimization Target")
        options = [("Frequency", "freq"), ("Current", "current"), ("Both", "both")]
        for idx, (text, val) in enumerate(options):
            ttk.Radiobutton(frame, text=text, variable=self.target, value=val, command=self.update_ui).grid(row=idx//2, column=idx%2, padx=10)
        return frame

    def add_param_section(self, parent):
        pf = ttk.Frame(parent)
        pf.pack(fill='x', pady=5)

        def create_led_frame(label, freq_var, cur_var):
            f = ttk.LabelFrame(pf, text=f"{label} LED")
            ttk.Label(f, text="Freq (0-100 Hz):").grid(row=0, column=0, sticky='w', padx=5)
            freq_entry = ttk.Entry(f, textvariable=freq_var, width=8)
            freq_entry.grid(row=0, column=1, padx=5)
            ttk.Label(f, text="Cur (50-900 mA):").grid(row=1, column=0, sticky='w', padx=5)
            cur_entry = ttk.Entry(f, textvariable=cur_var, width=8)
            cur_entry.grid(row=1, column=1, padx=5)
            return f, freq_entry, cur_entry

        red_frame, self.red_freq_entry, self.red_cur_entry = create_led_frame("Red", self.r_freq, self.r_cur)
        blue_frame, self.blue_freq_entry, self.blue_cur_entry = create_led_frame("Blue", self.b_freq, self.b_cur)

        red_frame.grid(row=0, column=0, padx=5, sticky='ew')
        blue_frame.grid(row=0, column=1, padx=5, sticky='ew')
        pf.columnconfigure(0, weight=1)
        pf.columnconfigure(1, weight=1)
        return pf
    
    def add_serial_section(self, parent):
        serial_frame = ttk.LabelFrame(parent, text="Serial Communication")
        serial_frame.pack(fill='x', pady=5)
        
        # Port selection
        port_frame = ttk.Frame(serial_frame)
        port_frame.pack(fill='x', pady=2)
        ttk.Label(port_frame, text="Port:").pack(side='left', padx=5)
        self.port_combobox = ttk.Combobox(port_frame, textvariable=self.serial_port, state="readonly", width=15)
        self.port_combobox.pack(side='left', padx=5)
        ttk.Button(port_frame, text="Refresh", command=self.update_available_ports).pack(side='left', padx=5)
        
        # Baud rate selection
        baud_frame = ttk.Frame(serial_frame)
        baud_frame.pack(fill='x', pady=2)
        ttk.Label(baud_frame, text="Baud Rate:").pack(side='left', padx=5)
        baud_rates = [9600, 19200, 38400, 57600, 115200]
        baud_combobox = ttk.Combobox(baud_frame, textvariable=self.baud_rate, values=baud_rates, state="readonly", width=10)
        baud_combobox.pack(side='left', padx=5)
        
        # Connect/Disconnect
        connect_frame = ttk.Frame(serial_frame)
        connect_frame.pack(fill='x', pady=2)
        self.connect_button = ttk.Button(connect_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side='left', padx=5)
        self.connection_status = ttk.Label(connect_frame, text="Disconnected")
        self.connection_status.pack(side='left', padx=5)

    def add_buttons(self, parent):
        btns = ttk.Frame(parent)
        btns.pack(fill='x', pady=10)
        ttk.Button(btns, text="Apply Settings", command=self.apply_settings).pack(side='left', padx=5)
        ttk.Button(btns, text="Reset", command=self.reset).pack(side='left', padx=5)

    def add_output_section(self, parent):
        out = ttk.LabelFrame(parent, text="Output")
        out.pack(fill='x', pady=5)
        self.output = tk.Text(out, height=1, wrap='word', bg='lightgray', font=("Courier", 10))
        self.output.pack(fill='x', padx=5, pady=5)

    def update_ui(self):
        if self.manual.get():
            self.opt_frame.pack_forget()
            self.set_entries_state('normal')
        else:
            self.opt_frame.pack(fill='x', pady=5)
            self.update_opt_controls()

    def update_opt_controls(self):
        mode = self.target.get()
        if mode == "freq":
            self.set_entries_state(cur='normal', freq='disabled')
        elif mode == "current":
            self.set_entries_state(cur='disabled', freq='normal')
        else:
            self.set_entries_state(cur='disabled', freq='disabled')
            self.r_freq.set(0)
            self.r_cur.set(0)
            self.b_freq.set(0)
            self.b_cur.set(0)

    def set_entries_state(self, freq='normal', cur='normal'):
        self.red_freq_entry.config(state=freq)
        self.blue_freq_entry.config(state=freq)
        self.red_cur_entry.config(state=cur)
        self.blue_cur_entry.config(state=cur)

    def validate(self):
        errors = []
        if not (0 <= self.r_freq.get() <= 100): errors.append("Red freq must be 0-100 Hz")
        if not (0 <= self.b_freq.get() <= 100): errors.append("Blue freq must be 0-100 Hz")
        if self.r_cur.get() > 0 and not (50 <= self.r_cur.get() <= 900): errors.append("Red current must be 50-900 mA")
        if self.b_cur.get() > 0 and not (50 <= self.b_cur.get() <= 900): errors.append("Blue current must be 50-900 mA")
        if errors:
            messagebox.showerror("Invalid Input", "\n".join(errors))
            return False
        return True

    def apply_settings(self):
        if not self.validate():
            return

        r_on = 50 <= self.r_cur.get() <= 900
        b_on = 50 <= self.b_cur.get() <= 900
        power_on = r_on or b_on
        freq_active = self.r_freq.get() > 0 or self.b_freq.get() > 0

        values = [
            int(r_on), #redLEDOn
            int(b_on), #blueLEDOn
            int(self.manual.get()), #manualMode
            int(power_on), #powerOn
            int(freq_active), #frequencyOn
            self.r_freq.get() if 0 <= self.r_freq.get() <= 100 else 0, #redLEDFrequency
            self.r_cur.get() if 50 <= self.r_cur.get() <= 900 else 0, #redLEDPower
            self.b_freq.get() if 0 <= self.b_freq.get() <= 100 else 0, #blueLEDFrequency
            self.b_cur.get() if 50 <= self.b_cur.get() <= 900 else 0 #blueLEDPower
        ]

        message = "<" + ", ".join(map(str, values)) + ">"

        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", message)

        # Send to serial if connected
        self.send_to_serial(message)

        msg = []
        if r_on:
            msg.append(f"Red: {self.r_cur.get()} mA at {self.r_freq.get()} Hz")
        if b_on:
            msg.append(f"Blue: {self.b_cur.get()} mA at {self.b_freq.get()} Hz")
        self.status.config(text=" | ".join(msg) or "No LEDs active")

    def reset(self):
        for var in [self.r_freq, self.r_cur, self.b_freq, self.b_cur]:
            var.set(0.0)
        self.manual.set(True)
        self.target.set("freq")
        self.update_ui()
        self.status.config(text="Values reset")
    
    def update_available_ports(self):
        """Update the list of available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox['values'] = ports
        if ports and not self.serial_port.get():
            self.serial_port.set(ports[0])
    
    def toggle_connection(self):
        """Connect or disconnect from the serial port"""
        if self.serial_connection is None:
            # Try to connect
            try:
                self.serial_connection = serial.Serial(
                    port=self.serial_port.get(),
                    baudrate=self.baud_rate.get(),
                    timeout=1
                )
                self.connection_status.config(text=f"Connected to {self.serial_port.get()}")
                self.connect_button.config(text="Disconnect")
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            # Disconnect
            try:
                self.serial_connection.close()
            except:
                pass
            finally:
                self.serial_connection = None
                self.connection_status.config(text="Disconnected")
                self.connect_button.config(text="Connect")
    
    def send_to_serial(self, message):
        """Send a message to the serial port if connected"""
        if self.serial_connection is None:
            return
        
        try:
            # Add a newline to the message for proper line termination
            serial_message = (message + '\n').encode('utf-8')
            self.serial_connection.write(serial_message)
            self.status.config(text=f"{self.status.cget('text')} | Sent to serial")
        except Exception as e:
            messagebox.showerror("Serial Error", f"Failed to send data: {str(e)}")   

    def on_closing(self):
        """Ensure the serial connection is closed when the app is closed"""
        if self.serial_connection is not None:
            try:
                self.serial_connection.close()
            except:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LEDControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Handle window closing
    root.mainloop()
