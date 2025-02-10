import sys
import threading
import queue
import time
import datetime  # Import datetime module for timestamps
import random  # Import random module for generating random data

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QFrame, QStackedWidget
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from pyftdi.serialext import serial_for_url

NUM_ARENAS = 16
is_running = False  # Global flag for data collection status

# USB Vendor ID (VID) 0403h FTDI default VID (hex)
# USB Product ID (PID) 6015h FTDI default PID (hex)
device_url = 'ftdi://0x0403:0x6015:FTWCKS5Q/1'

def read_ftdi_data(ftdi_serial):
    try:
        line = ftdi_serial.readline()
        if line:
            data_values = parse_data_line(line)
            return data_values
    except Exception as e:
        print(f"Error reading from FTDI device: {e}")
    return None

def parse_data_line(line):
    line = line.decode('utf-8').strip()
    data_values = [float(value) for value in line.split(',')]
    return data_values  # Should be a list with values for all arenas

class DataAcquisitionThread(threading.Thread):
    def __init__(self, data_queue, debug_mode=False):
        super().__init__()
        self.data_queue = data_queue
        self.is_running = True
        self.debug_mode = debug_mode  # Flag to indicate debug mode
        self.test_value = 50  # Constant value for straight line in debug mode
        if not self.debug_mode:
            # Initialize FTDI serial connection only if not in debug mode
            self.ftdi_serial = serial_for_url(device_url, baudrate=9600, timeout=1)
        else:
            self.ftdi_serial = None  # No serial connection in debug mode

    def run(self):
        while self.is_running:
            if self.debug_mode:
                # Generate constant data for a straight line
                data_values = [self.test_value for _ in range(NUM_ARENAS)]
                self.data_queue.put(data_values)
                time.sleep(0.1)  # Simulate a delay between data samples
            else:
                data_values = read_ftdi_data(self.ftdi_serial)
                if data_values:
                    self.data_queue.put(data_values)
                else:
                    time.sleep(0.01)
    
    def stop(self):
        self.is_running = False
        if self.ftdi_serial:
            self.ftdi_serial.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("STROBE Data Collection UI")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Arena selection and show all toggle
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self.arena_selector = QComboBox()
        for i in range(NUM_ARENAS):
            self.arena_selector.addItem(f"Arena {i+1}")
        self.arena_selector.currentIndexChanged.connect(self.change_arena)

        # Add Show All Arenas button
        self.show_all_button = QPushButton("Show All Arenas")
        self.show_all_button.setCheckable(True)
        self.show_all_button.toggled.connect(self.toggle_show_all_arenas)
        self.show_all_arenas = False  # Flag to track the toggle state

        # Add Debug Mode button
        self.debug_button = QPushButton("Debug Mode")
        self.debug_button.setCheckable(True)
        self.debug_button.toggled.connect(self.toggle_debug_mode)
        self.debug_mode = False  # Flag to track debug mode

        # Arena selector, Show All button, and Debug Mode button
        top_layout.addWidget(QLabel("Select Arena:"))
        top_layout.addWidget(self.arena_selector)
        top_layout.addWidget(self.show_all_button)
        top_layout.addWidget(self.debug_button)

        # Stack to switch between single and multiple plots
        self.plot_stack = QStackedWidget()
        main_layout.addWidget(self.plot_stack)

        # Single plot widget
        self.single_plot_widget = pg.PlotWidget(title="Data Plot")
        self.single_plot_widget.setYRange(-50, 150)  # Adjust range as needed
        self.plot_stack.addWidget(self.single_plot_widget)

        # Multiple plots widget
        self.all_plots_widget = QWidget()
        self.all_plots_layout = QGridLayout()
        self.all_plots_widget.setLayout(self.all_plots_layout)
        self.plot_stack.addWidget(self.all_plots_widget)

        # Create plot widgets for all arenas
        self.all_plot_widgets = []
        for i in range(NUM_ARENAS):
            plot = pg.PlotWidget(title=f"Arena {i+1}")
            plot.setYRange(-50, 150)
            self.all_plots_layout.addWidget(plot, i // 4, i % 4)
            self.all_plot_widgets.append(plot)

        # Layout for control buttons
        button_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)

        # First row of buttons: Start and Stop
        start_stop_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        start_stop_layout.addWidget(self.start_button)
        start_stop_layout.addWidget(self.stop_button)
        button_layout.addLayout(start_stop_layout)

        # Add a visual divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        button_layout.addWidget(divider)

        # Second row of buttons: Reset Baseline and Reset View
        reset_buttons_layout = QHBoxLayout()
        self.reset_baseline_button = QPushButton("Reset Baseline")
        self.reset_view_button = QPushButton("Reset View")
        reset_buttons_layout.addWidget(self.reset_baseline_button)
        reset_buttons_layout.addWidget(self.reset_view_button)
        button_layout.addLayout(reset_buttons_layout)

        # Connect buttons to their respective methods
        self.start_button.clicked.connect(self.start_data_collection)
        self.stop_button.clicked.connect(self.stop_data_collection)
        self.reset_baseline_button.clicked.connect(self.reset_baseline)
        self.reset_view_button.clicked.connect(self.reset_view)

        # Initialize data structures
        self.data = [[] for _ in range(NUM_ARENAS)]  # Data lists for each arena
        self.baseline_offsets = [0 for _ in range(NUM_ARENAS)]  # Calibration offsets
        self.current_arena_index = 0  # Currently selected arena

        # Initialize the data queue and data thread
        self.data_queue = queue.Queue()
        self.data_thread = None

        # Initialize the data file attribute
        self.data_file = None

    def start_data_collection(self):
        global is_running
        is_running = True
        print("Data collection started.")

        # Generate a filename with timestamp
        filename = datetime.datetime.now().strftime("data_%Y%m%d_%H%M%S.txt")
        # Open the data file for writing
        self.data_file = open(filename, "w")
        # Write header to the data file
        self.data_file.write("Timestamp," + ",".join([f"Arena{i+1}" for i in range(NUM_ARENAS)]) + "\n")

        # Start the data acquisition thread with the debug mode flag
        self.data_thread = DataAcquisitionThread(self.data_queue, debug_mode=self.debug_mode)
        self.data_thread.start()

        # Start the timer to update the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # Update every 100 milliseconds

    def stop_data_collection(self):
        global is_running
        is_running = False
        print("Data collection stopped.")
        self.timer.stop()
        if self.data_thread:
            self.data_thread.stop()
            self.data_thread.join()
            self.data_thread = None

        # Close the data file
        if self.data_file:
            self.data_file.close()
            self.data_file = None

    def update_plots(self):
        # Check if there's data in the queue
        while not self.data_queue.empty():
            data_values = self.data_queue.get()
            # data_values should be a list with values for each arena
            timestamp = datetime.datetime.now().isoformat()
            # Write data to file
            if self.data_file:
                self.data_file.write(f"{timestamp}," + ",".join(map(str, data_values)) + "\n")

            for i in range(NUM_ARENAS):
                new_value = data_values[i]  # Get the value for arena i

                # Apply calibration offset
                calibrated_value = new_value - self.baseline_offsets[i]

                self.data[i].append(calibrated_value)
                if len(self.data[i]) > 100:  # Limit the history to 100 data points
                    self.data[i].pop(0)

        if self.show_all_arenas:
            # Update all plots
            for i in range(NUM_ARENAS):
                self.all_plot_widgets[i].plot(self.data[i], clear=True)
        else:
            # Update the plot for the currently selected arena
            self.single_plot_widget.plot(self.data[self.current_arena_index], clear=True)

    def change_arena(self, index):
        # Update the current arena index when a new arena is selected
        self.current_arena_index = index
        print(f"Arena changed to: Arena {index + 1}")

        if not self.show_all_arenas:
            # Clear and update the plot with data from the new arena
            self.single_plot_widget.plot(self.data[self.current_arena_index], clear=True)
            self.reset_view()

    def reset_baseline(self):
        # Capture the current value as the new baseline
        if self.show_all_arenas:
            # Reset baseline for all arenas
            for i in range(NUM_ARENAS):
                if self.data[i]:
                    current_value = self.data[i][-1] + self.baseline_offsets[i]
                else:
                    current_value = 0
                self.baseline_offsets[i] = current_value
                print(f"Baseline reset for Arena {i + 1} to {current_value}")
        else:
            # Reset baseline for the selected arena
            current_arena = self.current_arena_index
            if self.data[current_arena]:
                current_value = self.data[current_arena][-1] + self.baseline_offsets[current_arena]
            else:
                current_value = 0
            self.baseline_offsets[current_arena] = current_value
            print(f"Baseline reset for Arena {current_arena + 1} to {current_value}")

    def reset_view(self):
        # Reset the plot view to the default settings
        if self.show_all_arenas:
            for plot in self.all_plot_widgets:
                plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
                plot.autoRange()
            print("All plots view reset to default.")
        else:
            self.single_plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            self.single_plot_widget.autoRange()
            print("Plot view reset to default.")

    def toggle_show_all_arenas(self, checked):
        self.show_all_arenas = checked
        if self.show_all_arenas:
            print("Showing all arenas.")
            self.plot_stack.setCurrentWidget(self.all_plots_widget)
            self.arena_selector.setEnabled(False)  # Disable arena selector when showing all
        else:
            print("Showing selected arena.")
            self.plot_stack.setCurrentWidget(self.single_plot_widget)
            self.arena_selector.setEnabled(True)  # Enable arena selector
            # Update the plot for the selected arena
            self.single_plot_widget.plot(self.data[self.current_arena_index], clear=True)

    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        if self.debug_mode:
            print("Debug mode activated.")
        else:
            print("Debug mode deactivated.")
        if is_running:
            self.stop_data_collection()
            self.start_data_collection()

    def closeEvent(self, event):
        # Ensure the data thread is stopped when the application is closed
        self.stop_data_collection()
        event.accept()

# Main execution code
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
