import sys
import threading
import queue
import time
import datetime
import random
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QFrame, QStackedWidget
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from pyftdi.serialext import serial_for_url

NUM_ARENAS = 16
is_running = False  # Global flag for data collection status

# Thresholds
SIP_THRESHOLD = 21000          # Anything above this is considered a "sip"
RIGHT_SENSOR_THRESHOLD = 25000 # Values above this are considered a "right sip"; else "left sip"

# USB Vendor ID (VID) 0403h FTDI default VID (hex)
# USB Product ID (PID) 6015h FTDI default PID (hex)
device_url = 'ftdi://0x0403:0x6015:FTWCKS5Q/1'

def read_ftdi_data(ftdi_serial):
    """Read a single line from the FTDI device and parse it."""
    try:
        line = ftdi_serial.readline()
        if line:
            return parse_data_line(line)
    except Exception as e:
        print(f"Error reading from FTDI device: {e}")
    return None

def parse_data_line(line):
    """Convert a comma-separated string of floats into a list of floats."""
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

        # ------------------
        # Top Layout: Arena Selector, Show All, Debug Mode
        # ------------------
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self.arena_selector = QComboBox()
        for i in range(NUM_ARENAS):
            self.arena_selector.addItem(f"Arena {i+1}")
        self.arena_selector.currentIndexChanged.connect(self.change_arena)

        self.show_all_button = QPushButton("Show All Arenas")
        self.show_all_button.setCheckable(True)
        self.show_all_button.toggled.connect(self.toggle_show_all_arenas)
        self.show_all_arenas = False  # Flag to track the toggle state

        self.debug_button = QPushButton("Debug Mode")
        self.debug_button.setCheckable(True)
        self.debug_button.toggled.connect(self.toggle_debug_mode)
        self.debug_mode = False  # Flag to track debug mode

        top_layout.addWidget(QLabel("Select Arena:"))
        top_layout.addWidget(self.arena_selector)
        top_layout.addWidget(self.show_all_button)
        top_layout.addWidget(self.debug_button)

        # ------------------
        # Plot Stacked Widget (Single vs All)
        # ------------------
        self.plot_stack = QStackedWidget()
        main_layout.addWidget(self.plot_stack)

        # Single plot widget container + labels
        self.single_plot_container = QWidget()
        single_plot_layout = QVBoxLayout(self.single_plot_container)

        self.single_plot_widget = pg.PlotWidget(title="Data Plot")
        self.single_plot_widget.setYRange(-50, 150)  # Adjust range as needed
        single_plot_layout.addWidget(self.single_plot_widget)

        # Container for "Sip Count" and "Preference" under single plot
        self.single_sip_label = QLabel("Left: 0, Right: 0")
        self.single_pref_label = QLabel("Preference: 0.00")
        single_plot_layout.addWidget(self.single_sip_label)
        single_plot_layout.addWidget(self.single_pref_label)

        self.plot_stack.addWidget(self.single_plot_container)

        # Multiple plots widget (grid layout of 16 arenas)
        self.all_plots_widget = QWidget()
        self.all_plots_layout = QGridLayout()
        self.all_plots_widget.setLayout(self.all_plots_layout)
        self.plot_stack.addWidget(self.all_plots_widget)

        # Create a combined widget+labels for each arena
        self.all_plot_widgets = []
        self.all_sip_labels = []
        self.all_pref_labels = []

        for i in range(NUM_ARENAS):
            # Container per arena
            arena_container = QWidget()
            arena_layout = QVBoxLayout(arena_container)

            # Plot
            plot = pg.PlotWidget(title=f"Arena {i+1}")
            plot.setYRange(-50, 150)
            arena_layout.addWidget(plot)

            # Labels for sip counts and preference
            sip_label = QLabel("Left: 0, Right: 0")
            pref_label = QLabel("Preference: 0.00")

            arena_layout.addWidget(sip_label)
            arena_layout.addWidget(pref_label)

            # Place this arena's container in the grid
            self.all_plots_layout.addWidget(arena_container, i // 4, i % 4)

            # Keep references for later updates
            self.all_plot_widgets.append(plot)
            self.all_sip_labels.append(sip_label)
            self.all_pref_labels.append(pref_label)

        # ------------------
        # Bottom Layout: Buttons
        # ------------------
        button_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)

        # First row: Start and Stop
        start_stop_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        start_stop_layout.addWidget(self.start_button)
        start_stop_layout.addWidget(self.stop_button)
        button_layout.addLayout(start_stop_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        button_layout.addWidget(divider)

        # Second row: Reset Baseline and Reset View
        reset_buttons_layout = QHBoxLayout()
        self.reset_baseline_button = QPushButton("Reset Baseline")
        self.reset_view_button = QPushButton("Reset View")
        reset_buttons_layout.addWidget(self.reset_baseline_button)
        reset_buttons_layout.addWidget(self.reset_view_button)
        button_layout.addLayout(reset_buttons_layout)

        # Connect button signals
        self.start_button.clicked.connect(self.start_data_collection)
        self.stop_button.clicked.connect(self.stop_data_collection)
        self.reset_baseline_button.clicked.connect(self.reset_baseline)
        self.reset_view_button.clicked.connect(self.reset_view)

        # ------------------
        # Data structures
        # ------------------
        # Historical data for plotting
        self.data = [[] for _ in range(NUM_ARENAS)]  # raw data minus baseline offsets
        self.baseline_offsets = [0 for _ in range(NUM_ARENAS)]  # calibration offsets
        self.current_arena_index = 0  # which arena is selected in the single-plot view

        # Variables for sip counting
        self.left_counts = [0 for _ in range(NUM_ARENAS)]
        self.right_counts = [0 for _ in range(NUM_ARENAS)]
        # Track whether we were above threshold on the *previous* sample
        # so we only count a sip once per crossing
        self.was_above_threshold = [False for _ in range(NUM_ARENAS)]

        # Data acquisition
        self.data_queue = queue.Queue()
        self.data_thread = None
        self.data_file = None

    def start_data_collection(self):
        global is_running
        is_running = True
        print("Data collection started.")

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Generate a filename with timestamp and place it in the logs folder
        filename = datetime.datetime.now().strftime("data_%Y%m%d_%H%M%S.txt")
        file_path = os.path.join(logs_dir, filename)

        # Open the data file for writing
        self.data_file = open(file_path, "w")
        # Write header to the data file
        self.data_file.write("Timestamp," + ",".join([f"Arena{i+1}" for i in range(NUM_ARENAS)]) + "\n")

        # Start the data acquisition thread
        self.data_thread = DataAcquisitionThread(self.data_queue, debug_mode=self.debug_mode)
        self.data_thread.start()

        # Start the timer to update the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # Update every 100 ms

    def stop_data_collection(self):
        global is_running
        is_running = False
        print("Data collection stopped.")
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

        if self.data_thread:
            self.data_thread.stop()
            self.data_thread.join()
            self.data_thread = None

        if self.data_file:
            self.data_file.close()
            self.data_file = None

    def update_plots(self):
        # Process all available data in the queue
        while not self.data_queue.empty():
            data_values = self.data_queue.get()
            timestamp = datetime.datetime.now().isoformat()

            # Write to file
            if self.data_file:
                self.data_file.write(f"{timestamp}," + ",".join(map(str, data_values)) + "\n")

            # Process each arena's reading
            for i in range(NUM_ARENAS):
                new_value = data_values[i]

                # Apply baseline offset
                calibrated_value = new_value - self.baseline_offsets[i]
                self.data[i].append(calibrated_value)
                if len(self.data[i]) > 100:  # limit the history
                    self.data[i].pop(0)

                # Check sip threshold crossing
                above_threshold = (new_value > SIP_THRESHOLD)
                if above_threshold and not self.was_above_threshold[i]:
                    # This is a new sip event
                    if new_value > RIGHT_SENSOR_THRESHOLD:
                        # Right sip
                        self.right_counts[i] += 1
                    else:
                        # Left sip
                        self.left_counts[i] += 1

                    self.was_above_threshold[i] = True
                elif not above_threshold:
                    self.was_above_threshold[i] = False

        # Update plots and labels
        if self.show_all_arenas:
            # Update all plots
            for i in range(NUM_ARENAS):
                self.all_plot_widgets[i].plot(self.data[i], clear=True)
                self.update_arena_labels(i)
        else:
            # Update only the currently selected arena plot
            idx = self.current_arena_index
            self.single_plot_widget.plot(self.data[idx], clear=True)
            self.update_arena_labels(idx, single_view=True)

    def update_arena_labels(self, arena_index, single_view=False):
        """Update the sip count and preference index labels for a given arena."""
        left = self.left_counts[arena_index]
        right = self.right_counts[arena_index]
        total = left + right

        if total > 0:
            pref_index = (left - right) / total  # (Left - Right) / (Left + Right)
        else:
            pref_index = 0

        # Format label text
        sip_text = f"Left: {left}, Right: {right}"
        pref_text = f"Preference: {pref_index:.2f}"

        # If we are updating the multi-arena grid
        if not single_view:
            self.all_sip_labels[arena_index].setText(sip_text)
            self.all_pref_labels[arena_index].setText(pref_text)
        else:
            # Update the single-arena labels
            self.single_sip_label.setText(sip_text)
            self.single_pref_label.setText(pref_text)

    def change_arena(self, index):
        self.current_arena_index = index
        print(f"Arena changed to: Arena {index + 1}")

        if not self.show_all_arenas:
            # Update the single plot with the new arena’s data
            self.single_plot_widget.plot(self.data[self.current_arena_index], clear=True)
            self.reset_view()
            self.update_arena_labels(self.current_arena_index, single_view=True)

    def reset_baseline(self):
        """Capture the current value as the new baseline for the selected or all arenas."""
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
        """Reset the plot view to the default settings (auto-range)."""
        if self.show_all_arenas:
            for plot in self.all_plot_widgets:
                plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
                plot.autoRange()
            print("All plots view reset to default.")
        else:
            self.single_plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            self.single_plot_widget.autoRange()
            print("Single arena plot view reset to default.")

    def toggle_show_all_arenas(self, checked):
        self.show_all_arenas = checked
        if self.show_all_arenas:
            print("Showing all arenas.")
            self.plot_stack.setCurrentWidget(self.all_plots_widget)
            self.arena_selector.setEnabled(False)  # Disable selector in multi-mode
        else:
            print("Showing selected arena.")
            self.plot_stack.setCurrentWidget(self.single_plot_container)
            self.arena_selector.setEnabled(True)
            # Update the single plot for the currently selected arena
            idx = self.current_arena_index
            self.single_plot_widget.plot(self.data[idx], clear=True)
            self.update_arena_labels(idx, single_view=True)

    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        print("Debug mode activated." if self.debug_mode else "Debug mode deactivated.")
        # If data collection is already running, restart to apply the debug mode change
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
