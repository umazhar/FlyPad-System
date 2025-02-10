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
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
from pyftdi.serialext import serial_for_url

NUM_ARENAS = 16
is_running = False  # Global flag for data collection status

# Thresholds
SIP_THRESHOLD = 21000            # Anything above this is considered a "sip"
RIGHT_SENSOR_THRESHOLD = 28000   # Values above this range are considered a "right sip"

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
        self.debug_mode = debug_mode
        if not self.debug_mode:
            self.ftdi_serial = serial_for_url(device_url, baudrate=9600, timeout=1)
        else:
            self.ftdi_serial = None

    def run(self):
        while self.is_running:
            if self.debug_mode:
                # Example fake data generator:
                # 70% no sip, 15% left-sip range, 15% right-sip range
                data_values = []
                for _ in range(NUM_ARENAS):
                    r = random.random()
                    if r < 0.70:
                        val = random.uniform(10000, 15000)   # no sip
                    elif r < 0.85:
                        val = random.uniform(21000, 25000)  # left sip range
                    else:
                        val = random.uniform(28000, 30000)  # right sip range
                    data_values.append(val)
                self.data_queue.put(data_values)
                time.sleep(0.1)
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

        self.setWindowTitle("STROBE Data Collection UI (Dark Mode) with Total Sips & CSV Logging")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        central_widget.setLayout(main_layout)

        # ------------------
        # Top Layout
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
        self.show_all_arenas = False

        self.debug_button = QPushButton("Debug Mode")
        self.debug_button.setCheckable(True)
        self.debug_button.toggled.connect(self.toggle_debug_mode)
        self.debug_mode = False

        top_layout.addWidget(QLabel("Select Arena:"))
        top_layout.addWidget(self.arena_selector)
        top_layout.addWidget(self.show_all_button)
        top_layout.addWidget(self.debug_button)
        top_layout.addStretch(1)

        # ------------------
        # Plot Stacked Widget (Single vs All)
        # ------------------
        self.plot_stack = QStackedWidget()
        main_layout.addWidget(self.plot_stack)

        # Single plot widget container
        self.single_plot_container = QWidget()
        single_plot_layout = QVBoxLayout(self.single_plot_container)
        single_plot_layout.setContentsMargins(5, 5, 5, 5)
        single_plot_layout.setSpacing(8)

        self.single_plot_widget = pg.PlotWidget(title="Data Plot (Single Arena)")
        self.single_plot_widget.setYRange(0, 32000)
        single_plot_layout.addWidget(self.single_plot_widget)

        # Horizontal layout for Left, Right, Total, Pref
        self.single_labels_layout = QHBoxLayout()
        self.single_labels_layout.setSpacing(15)

        self.single_sip_left_label = QLabel("Left: 0")
        line1 = QFrame()
        line1.setFrameShape(QFrame.VLine)
        line1.setFrameShadow(QFrame.Sunken)

        self.single_sip_right_label = QLabel("Right: 0")
        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)
        line2.setFrameShadow(QFrame.Sunken)

        self.single_sip_total_label = QLabel("Total: 0")
        line3 = QFrame()
        line3.setFrameShape(QFrame.VLine)
        line3.setFrameShadow(QFrame.Sunken)

        self.single_pref_label = QLabel("Pref: 0.00")

        self.single_labels_layout.addWidget(self.single_sip_left_label)
        self.single_labels_layout.addWidget(line1)
        self.single_labels_layout.addWidget(self.single_sip_right_label)
        self.single_labels_layout.addWidget(line2)
        self.single_labels_layout.addWidget(self.single_sip_total_label)
        self.single_labels_layout.addWidget(line3)
        self.single_labels_layout.addWidget(self.single_pref_label)
        self.single_labels_layout.addStretch(1)

        single_plot_layout.addLayout(self.single_labels_layout)
        self.plot_stack.addWidget(self.single_plot_container)

        # Multiple plots widget
        self.all_plots_widget = QWidget()
        self.all_plots_layout = QGridLayout()
        self.all_plots_layout.setSpacing(10)
        self.all_plots_layout.setContentsMargins(5, 5, 5, 5)
        self.all_plots_widget.setLayout(self.all_plots_layout)
        self.plot_stack.addWidget(self.all_plots_widget)

        self.all_plot_widgets = []
        # We'll store references to the 4 labels: left, right, total, pref
        self.all_sip_left_labels = []
        self.all_sip_right_labels = []
        self.all_sip_total_labels = []
        self.all_pref_labels = []

        for i in range(NUM_ARENAS):
            arena_container = QWidget()
            arena_layout = QVBoxLayout(arena_container)
            arena_layout.setContentsMargins(5, 5, 5, 5)
            arena_layout.setSpacing(5)

            plot = pg.PlotWidget(title=f"Arena {i+1}")
            plot.setYRange(0, 32000)
            arena_layout.addWidget(plot)

            # Horizontal row for sip + preference
            label_row = QHBoxLayout()
            label_row.setSpacing(10)

            sip_left_label = QLabel("Left: 0")
            lineA = QFrame()
            lineA.setFrameShape(QFrame.VLine)
            lineA.setFrameShadow(QFrame.Sunken)

            sip_right_label = QLabel("Right: 0")
            lineB = QFrame()
            lineB.setFrameShape(QFrame.VLine)
            lineB.setFrameShadow(QFrame.Sunken)

            sip_total_label = QLabel("Total: 0")
            lineC = QFrame()
            lineC.setFrameShape(QFrame.VLine)
            lineC.setFrameShadow(QFrame.Sunken)

            pref_label = QLabel("Pref: 0.00")

            label_row.addWidget(sip_left_label)
            label_row.addWidget(lineA)
            label_row.addWidget(sip_right_label)
            label_row.addWidget(lineB)
            label_row.addWidget(sip_total_label)
            label_row.addWidget(lineC)
            label_row.addWidget(pref_label)
            label_row.addStretch(1)

            arena_layout.addLayout(label_row)
            self.all_plots_layout.addWidget(arena_container, i // 4, i % 4)

            self.all_plot_widgets.append(plot)
            self.all_sip_left_labels.append(sip_left_label)
            self.all_sip_right_labels.append(sip_right_label)
            self.all_sip_total_labels.append(sip_total_label)
            self.all_pref_labels.append(pref_label)

        # ------------------
        # Bottom Layout: Buttons
        # ------------------
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        main_layout.addLayout(bottom_layout)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_baseline_button = QPushButton("Reset Baseline")
        self.reset_view_button = QPushButton("Reset View")

        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.stop_button)
        bottom_layout.addWidget(self.reset_baseline_button)
        bottom_layout.addWidget(self.reset_view_button)
        bottom_layout.addStretch(1)

        # Connect button signals
        self.start_button.clicked.connect(self.start_data_collection)
        self.stop_button.clicked.connect(self.stop_data_collection)
        self.reset_baseline_button.clicked.connect(self.reset_baseline)
        self.reset_view_button.clicked.connect(self.reset_view)

        # Data structures
        self.data = [[] for _ in range(NUM_ARENAS)]
        self.baseline_offsets = [0 for _ in range(NUM_ARENAS)]
        self.current_arena_index = 0

        # Sip counting
        self.left_counts = [0 for _ in range(NUM_ARENAS)]
        self.right_counts = [0 for _ in range(NUM_ARENAS)]
        self.was_above_threshold = [False for _ in range(NUM_ARENAS)]

        # Threading
        self.data_queue = queue.Queue()
        self.data_thread = None
        self.data_file = None

    def start_data_collection(self):
        global is_running
        is_running = True
        print("Data collection started.")

        # Create logs directory if needed
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Generate filename
        filename = datetime.datetime.now().strftime("data_%Y%m%d_%H%M%S.txt")
        file_path = os.path.join(logs_dir, filename)

        # ------------------------------------------------------------
        # Build CSV Header
        # ------------------------------------------------------------
        # Basic columns: Timestamp + ArenaX ADC
        header = ["Timestamp"]
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_ADC")
        # Then for each arena, add LeftCount, RightCount, TotalCount, Pref
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_LeftCount")
            header.append(f"Arena{i+1}_RightCount")
            header.append(f"Arena{i+1}_TotalCount")
            header.append(f"Arena{i+1}_Preference")

        self.data_file = open(file_path, "w")
        self.data_file.write(",".join(header) + "\n")

        # Start data thread
        self.data_thread = DataAcquisitionThread(self.data_queue, debug_mode=self.debug_mode)
        self.data_thread.start()

        # Start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)

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
        while not self.data_queue.empty():
            data_values = self.data_queue.get()
            timestamp = datetime.datetime.now().isoformat()

            # ------------------------------------------------------------
            # Update internal data + sip counts
            # ------------------------------------------------------------
            for i in range(NUM_ARENAS):
                new_value = data_values[i]
                calibrated_value = new_value - self.baseline_offsets[i]
                self.data[i].append(calibrated_value)
                if len(self.data[i]) > 100:
                    self.data[i].pop(0)

                # Sip detection
                above_threshold = (new_value > SIP_THRESHOLD)
                if above_threshold and not self.was_above_threshold[i]:
                    if new_value > RIGHT_SENSOR_THRESHOLD:
                        self.right_counts[i] += 1
                    else:
                        self.left_counts[i] += 1
                    self.was_above_threshold[i] = True
                elif not above_threshold:
                    self.was_above_threshold[i] = False

            # ------------------------------------------------------------
            # Build line for CSV with updated counts
            # ------------------------------------------------------------
            row_values = [timestamp]
            # First, all arena ADC readings
            for val in data_values:
                row_values.append(str(val))

            # Then, for each arena, leftCount, rightCount, total, pref
            for i in range(NUM_ARENAS):
                left = self.left_counts[i]
                right = self.right_counts[i]
                total = left + right
                pref = 0.0
                if total > 0:
                    pref = (left - right) / total
                row_values.append(str(left))
                row_values.append(str(right))
                row_values.append(str(total))
                row_values.append(f"{pref:.3f}")

            # Write to CSV
            if self.data_file:
                self.data_file.write(",".join(row_values) + "\n")

        # ------------------------------------------------------------
        # Update plots + labels
        # ------------------------------------------------------------
        if self.show_all_arenas:
            # Multi-arena
            for i in range(NUM_ARENAS):
                self.all_plot_widgets[i].plot(self.data[i], clear=True)
                self.update_arena_labels(i, single_view=False)
        else:
            # Single arena
            idx = self.current_arena_index
            self.single_plot_widget.plot(self.data[idx], clear=True)
            self.update_arena_labels(idx, single_view=True)

    def update_arena_labels(self, arena_index, single_view=False):
        left = self.left_counts[arena_index]
        right = self.right_counts[arena_index]
        total = left + right
        pref = 0.0
        if total > 0:
            pref = (left - right) / total

        if single_view:
            self.single_sip_left_label.setText(f"Left: {left}")
            self.single_sip_right_label.setText(f"Right: {right}")
            self.single_sip_total_label.setText(f"Total: {total}")
            self.single_pref_label.setText(f"Pref: {pref:.2f}")
        else:
            self.all_sip_left_labels[arena_index].setText(f"Left: {left}")
            self.all_sip_right_labels[arena_index].setText(f"Right: {right}")
            self.all_sip_total_labels[arena_index].setText(f"Total: {total}")
            self.all_pref_labels[arena_index].setText(f"Pref: {pref:.2f}")

    def change_arena(self, index):
        self.current_arena_index = index
        print(f"Arena changed to: Arena {index + 1}")
        if not self.show_all_arenas:
            self.single_plot_widget.plot(self.data[self.current_arena_index], clear=True)
            self.reset_view()
            self.update_arena_labels(self.current_arena_index, single_view=True)

    def reset_baseline(self):
        if self.show_all_arenas:
            for i in range(NUM_ARENAS):
                if self.data[i]:
                    current_value = self.data[i][-1] + self.baseline_offsets[i]
                else:
                    current_value = 0
                self.baseline_offsets[i] = current_value
                print(f"Baseline reset for Arena {i+1} to {current_value}")
        else:
            current_arena = self.current_arena_index
            if self.data[current_arena]:
                current_value = self.data[current_arena][-1] + self.baseline_offsets[current_arena]
            else:
                current_value = 0
            self.baseline_offsets[current_arena] = current_value
            print(f"Baseline reset for Arena {current_arena+1} to {current_value}")

    def reset_view(self):
        if self.show_all_arenas:
            for plot in self.all_plot_widgets:
                plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
                plot.autoRange()
            print("All plots view reset.")
        else:
            self.single_plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            self.single_plot_widget.autoRange()
            print("Single arena view reset.")

    def toggle_show_all_arenas(self, checked):
        self.show_all_arenas = checked
        if self.show_all_arenas:
            print("Showing all arenas.")
            self.plot_stack.setCurrentWidget(self.all_plots_widget)
            self.arena_selector.setEnabled(False)
        else:
            print("Showing selected arena.")
            self.plot_stack.setCurrentWidget(self.single_plot_container)
            self.arena_selector.setEnabled(True)
            idx = self.current_arena_index
            self.single_plot_widget.plot(self.data[idx], clear=True)
            self.update_arena_labels(idx, single_view=True)

    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        print("Debug mode activated." if self.debug_mode else "Debug mode deactivated.")
        if is_running:
            self.stop_data_collection()
            self.start_data_collection()

    def closeEvent(self, event):
        self.stop_data_collection()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
