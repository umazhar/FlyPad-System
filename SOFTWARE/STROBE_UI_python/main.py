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
SIP_THRESHOLD = 21000            # Anything above this => "sip"
RIGHT_SENSOR_THRESHOLD = 28000   # Above this => "right sip"

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
    return data_values

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
                # 70% no sip, 15% left sip (21000–25000), 15% right sip (28000–30000)
                data_values = []
                for _ in range(NUM_ARENAS):
                    r = random.random()
                    if r < 0.70:
                        val = random.uniform(10000, 15000)   # no sip
                    elif r < 0.85:
                        val = random.uniform(SIP_THRESHOLD, 25000)  # left sip
                    else:
                        val = random.uniform(RIGHT_SENSOR_THRESHOLD, 30000)  # right sip
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

        self.setWindowTitle("STROBE Data Collection UI")
        self.setGeometry(100, 100, 1000, 700)

        # ------------------
        # Central Widget & Main Layout
        # ------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
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
        # Plot Stack (Single vs All)
        # ------------------
        self.plot_stack = QStackedWidget()
        main_layout.addWidget(self.plot_stack)

        # ========== SINGLE-ARENA VIEW ==========
        self.single_plot_container = QWidget()
        single_plot_layout = QVBoxLayout(self.single_plot_container)
        single_plot_layout.setContentsMargins(5, 5, 5, 5)
        single_plot_layout.setSpacing(8)

        self.single_plot_widget = pg.PlotWidget(title="Data Plot (Single Arena)")
        self.single_plot_widget.setYRange(0, 32000)
        single_plot_layout.addWidget(self.single_plot_widget)

        # -- Threshold Lines for Single Plot
        self.single_sip_line = pg.InfiniteLine(
            pos=SIP_THRESHOLD, angle=0,
            pen=pg.mkPen(color='red', style=Qt.DashLine, width=2),
            movable=False
        )
        self.single_right_line = pg.InfiniteLine(
            pos=RIGHT_SENSOR_THRESHOLD, angle=0,
            pen=pg.mkPen(color='magenta', style=Qt.DashLine, width=2),
            movable=False
        )
        self.single_plot_widget.addItem(self.single_sip_line)
        self.single_plot_widget.addItem(self.single_right_line)

        # -- Single PlotDataItem (no "clear=True")
        self.single_data_item = pg.PlotDataItem([], pen='y')
        self.single_plot_widget.addItem(self.single_data_item)

        # -- Single labels for sip counts
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

        # ========== MULTI-ARENA VIEW ==========
        self.all_plots_widget = QWidget()
        self.all_plots_layout = QGridLayout()
        self.all_plots_layout.setSpacing(10)
        self.all_plots_layout.setContentsMargins(5, 5, 5, 5)
        self.all_plots_widget.setLayout(self.all_plots_layout)
        self.plot_stack.addWidget(self.all_plots_widget)

        # We'll create a PlotWidget + data item + threshold lines for each arena
        self.all_plot_widgets = []
        self.all_data_items = []

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

            # -- Threshold lines for multi
            sip_line = pg.InfiniteLine(
                pos=SIP_THRESHOLD, angle=0,
                pen=pg.mkPen(color='red', style=Qt.DashLine, width=2),
                movable=False
            )
            right_line = pg.InfiniteLine(
                pos=RIGHT_SENSOR_THRESHOLD, angle=0,
                pen=pg.mkPen(color='magenta', style=Qt.DashLine, width=2),
                movable=False
            )
            plot.addItem(sip_line)
            plot.addItem(right_line)

            # -- Data item for multi-plot
            data_item = pg.PlotDataItem([], pen='y')
            plot.addItem(data_item)

            # Label row for left, right, total, pref
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
            self.all_data_items.append(data_item)

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

        # -------------
        # Data Structures
        # -------------
        self.data = [[] for _ in range(NUM_ARENAS)]
        self.baseline_offsets = [0 for _ in range(NUM_ARENAS)]
        self.current_arena_index = 0

        self.left_counts = [0 for _ in range(NUM_ARENAS)]
        self.right_counts = [0 for _ in range(NUM_ARENAS)]
        self.was_above_threshold = [False for _ in range(NUM_ARENAS)]

        self.data_queue = queue.Queue()
        self.data_thread = None
        self.data_file = None

    # --------------------------------------------------------
    # Start / Stop Data Collection
    # --------------------------------------------------------
    def start_data_collection(self):
        global is_running
        is_running = True
        print("Data collection started.")

        # Create logs directory if needed
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        filename = datetime.datetime.now().strftime("data_%Y%m%d_%H%M%S.txt")
        file_path = os.path.join(logs_dir, filename)

        # Build CSV Header
        header = ["Timestamp"]
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_ADC")
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_LeftCount")
            header.append(f"Arena{i+1}_RightCount")
            header.append(f"Arena{i+1}_TotalCount")
            header.append(f"Arena{i+1}_Preference")

        self.data_file = open(file_path, "w")
        self.data_file.write(",".join(header) + "\n")

        self.data_thread = DataAcquisitionThread(self.data_queue, debug_mode=self.debug_mode)
        self.data_thread.start()

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

    # --------------------------------------------------------
    # Update Plots (No "clear=True")
    # --------------------------------------------------------
    def update_plots(self):
        while not self.data_queue.empty():
            data_values = self.data_queue.get()
            timestamp = datetime.datetime.now().isoformat()

            # Update sip counts & store data
            for i in range(NUM_ARENAS):
                new_value = data_values[i]
                calibrated_value = new_value - self.baseline_offsets[i]
                self.data[i].append(calibrated_value)
                if len(self.data[i]) > 100:
                    self.data[i].pop(0)

                # Threshold crossing for sips
                above_threshold = (new_value > SIP_THRESHOLD)
                if above_threshold and not self.was_above_threshold[i]:
                    if new_value > RIGHT_SENSOR_THRESHOLD:
                        self.right_counts[i] += 1
                    else:
                        self.left_counts[i] += 1
                    self.was_above_threshold[i] = True
                elif not above_threshold:
                    self.was_above_threshold[i] = False

            # Write CSV row
            row = [timestamp]
            for val in data_values:
                row.append(str(val))
            for i in range(NUM_ARENAS):
                left = self.left_counts[i]
                right = self.right_counts[i]
                total = left + right
                pref = (left - right)/total if total > 0 else 0
                row.append(str(left))
                row.append(str(right))
                row.append(str(total))
                row.append(f"{pref:.3f}")
            if self.data_file:
                self.data_file.write(",".join(row) + "\n")

        # Update single or multi plots
        if self.show_all_arenas:
            for i in range(NUM_ARENAS):
                # Use setData(...) on each multi plot's data item
                self.all_data_items[i].setData(self.data[i])
                self.update_arena_labels(i, single_view=False)
        else:
            idx = self.current_arena_index
            # Single plot data item
            self.single_data_item.setData(self.data[idx])
            self.update_arena_labels(idx, single_view=True)

    # --------------------------------------------------------
    # Label Updates
    # --------------------------------------------------------
    def update_arena_labels(self, arena_index, single_view=False):
        left = self.left_counts[arena_index]
        right = self.right_counts[arena_index]
        total = left + right
        pref = (left - right)/total if total > 0 else 0

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

    # --------------------------------------------------------
    # Arena Select / Baseline / View
    # --------------------------------------------------------
    def change_arena(self, index):
        self.current_arena_index = index
        print(f"Arena changed to: Arena {index + 1}")
        if not self.show_all_arenas:
            self.single_data_item.setData(self.data[index])
            self.reset_view()
            self.update_arena_labels(index, single_view=True)

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
            idx = self.current_arena_index
            if self.data[idx]:
                current_value = self.data[idx][-1] + self.baseline_offsets[idx]
            else:
                current_value = 0
            self.baseline_offsets[idx] = current_value
            print(f"Baseline reset for Arena {idx+1} to {current_value}")

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

    # --------------------------------------------------------
    # Toggles
    # --------------------------------------------------------
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
            self.single_data_item.setData(self.data[idx])
            self.update_arena_labels(idx, single_view=True)

    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        print("Debug mode activated." if self.debug_mode else "Debug mode deactivated.")
        if is_running:
            self.stop_data_collection()
            self.start_data_collection()

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------
    def closeEvent(self, event):
        self.stop_data_collection()
        event.accept()

# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")  # optional; remove if you want system default

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
