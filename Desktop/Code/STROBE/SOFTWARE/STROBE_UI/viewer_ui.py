#!/usr/bin/env python3

import queue
import time
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QComboBox, QFileDialog, QGridLayout, QMessageBox,
    QFrame, QStackedWidget, QLineEdit
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIntValidator, QPalette, QColor
import pyqtgraph as pg

from constants import *
from data_acquisition import FTDIConnection, FTDIDataReader, SimulatedDataReader
from data_logger import DataLogger
from data_processor import DataProcessor

class StrobeDataViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STROBE: Sip-TRiggered Optogenetic Behavior Enclosure")
        self.setGeometry(100, 100, 1280, 800)
        self.data_queue = queue.Queue()
        self.data_processor = DataProcessor()
        self.data_logger = DataLogger()
        self.is_running = False
        self.serial_port = None
        self.data_thread = None
        self.debug_mode = False
        self.current_arena_index = 0
        
        self.show_all_arenas = True
        self.init_ui()

        self.prev_left_counts = [0] * NUM_ARENAS
        self.prev_right_counts = [0] * NUM_ARENAS
        
        # For auto-reset view after 1 second
        self.start_time = 0
        self.auto_reset_done = False
        
        # initial states
        self.show_all_button.setChecked(True)
        self.plot_stack.setCurrentWidget(self.all_plots_widget)
        self.arena_selector.setEnabled(False)
        self.scan_serial_ports()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)
        
        port_label = QLabel("FTDI Port:")
        top_layout.addWidget(port_label)
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet("QComboBox { color: white; } QComboBox QAbstractItemView { color: white; }")
        top_layout.addWidget(self.port_combo)

        self.scan_button = QPushButton("Scan Ports")
        self.scan_button.clicked.connect(self.scan_serial_ports)
        top_layout.addWidget(self.scan_button)
        
        # File save button
        self.save_location_button = QPushButton("Custom Save Location")
        self.save_location_button.setToolTip("Set custom location to save data (optional)")
        self.save_location_button.clicked.connect(self.save_to_file)
        top_layout.addWidget(self.save_location_button)
        
        # Arena selector
        self.arena_selector = QComboBox()
        for i in range(NUM_ARENAS):
            self.arena_selector.addItem(f"Arena {i+1}")
        self.arena_selector.currentIndexChanged.connect(self.change_arena)
        self.arena_selector.setStyleSheet("QComboBox { color: white; } QComboBox QAbstractItemView { color: white; }")
        
        top_layout.addWidget(QLabel("Select Arena:"))
        top_layout.addWidget(self.arena_selector)
        
        # View toggle
        self.show_all_button = QPushButton("Show All Arenas")
        self.show_all_button.setCheckable(True)
        self.show_all_button.toggled.connect(self.toggle_show_all_arenas)
        top_layout.addWidget(self.show_all_button)
        
        # # Debug toggle
        # self.debug_button = QPushButton("Debug Mode")
        # self.debug_button.setCheckable(True)
        # self.debug_button.toggled.connect(self.toggle_debug_mode)
        # top_layout.addWidget(self.debug_button)
        
        # Arena count selector
        top_layout.addWidget(QLabel("Number of Arenas:"))
        self.arena_count_input = QLineEdit()
        self.arena_count_input.setMaximumWidth(40)
        self.arena_count_input.setText(str(NUM_ARENAS))
        self.arena_count_input.setValidator(QIntValidator(1, NUM_ARENAS))
        top_layout.addWidget(self.arena_count_input)
        
        self.update_arena_count_button = QPushButton("Update")
        self.update_arena_count_button.clicked.connect(self.update_arena_count)
        top_layout.addWidget(self.update_arena_count_button)
        
        top_layout.addStretch(1)
        
        # Plot area (stack for single/multi view)
        self.plot_stack = QStackedWidget()
        main_layout.addWidget(self.plot_stack)
        
        # Create single arena view
        self.setup_single_arena_view()
        
        # Create multi-arena view
        self.setup_multi_arena_view()
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        main_layout.addLayout(bottom_layout)
        
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.restart_button = QPushButton("Restart Test")  # New button
        self.reset_view_button = QPushButton("Reset View")
        
        # Connect button actions
        self.start_button.clicked.connect(self.start_data_collection)
        self.stop_button.clicked.connect(self.stop_data_collection)
        self.restart_button.clicked.connect(self.restart_test)  # Connect new button
        self.reset_view_button.clicked.connect(self.reset_view)
        
        self.stop_button.setEnabled(False)
        self.restart_button.setEnabled(True)  # Initially enabled
        
        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.stop_button)
        bottom_layout.addWidget(self.restart_button)  # Add new button
        bottom_layout.addWidget(self.reset_view_button)
        bottom_layout.addStretch(1)
        
        # Status bar
        self.status_label = QLabel("Ready. Select a port and click Start.")
        main_layout.addWidget(self.status_label)
    
    def setup_single_arena_view(self):
        self.single_plot_container = QWidget()
        single_plot_layout = QVBoxLayout(self.single_plot_container)
        single_plot_layout.setContentsMargins(5, 5, 5, 5)
        single_plot_layout.setSpacing(8)
        
        self.single_plot_widget = pg.PlotWidget(title="Data Plot (Single Arena)")
        self.single_plot_widget.setYRange(0, MAX_CAPDAC_VALUE)
        single_plot_layout.addWidget(self.single_plot_widget)
        
        # Plot curves - change blue to light blue
        self.single_data_item_left = pg.PlotDataItem([], pen=pg.mkPen(color='r', width=2), name="Left Sensor")
        self.single_data_item_right = pg.PlotDataItem([], pen=pg.mkPen(color='#39C5BB', width=2), name="Right Sensor")  # Light blue color
        self.single_plot_widget.addItem(self.single_data_item_left)
        self.single_plot_widget.addItem(self.single_data_item_right)
        
        # Add legend
        self.single_plot_widget.addLegend()
        
        # Counters display
        self.single_labels_layout = QHBoxLayout()
        self.single_labels_layout.setSpacing(15)
        
        # Create frames for each counter - this helps provide stable highlighting without layout shifts
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setMinimumWidth(70)
        left_layout = QHBoxLayout(left_frame)
        left_layout.setContentsMargins(5, 2, 5, 2)
        self.single_sip_left_label = QLabel("Left: 0")
        left_layout.addWidget(self.single_sip_left_label)
        
        line1 = QFrame()
        line1.setFrameShape(QFrame.VLine)
        line1.setFrameShadow(QFrame.Sunken)
        
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setMinimumWidth(70)
        right_layout = QHBoxLayout(right_frame)
        right_layout.setContentsMargins(5, 2, 5, 2)
        self.single_sip_right_label = QLabel("Right: 0")
        right_layout.addWidget(self.single_sip_right_label)
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.VLine)
        line2.setFrameShadow(QFrame.Sunken)
        
        self.single_sip_total_label = QLabel("Total: 0")
        line3 = QFrame()
        line3.setFrameShape(QFrame.VLine)
        line3.setFrameShadow(QFrame.Sunken)
        
        self.single_pref_label = QLabel("Pref: 0.00")
        
        # Add frames to layout
        self.single_labels_layout.addWidget(left_frame)
        self.single_labels_layout.addWidget(line1)
        self.single_labels_layout.addWidget(right_frame)
        self.single_labels_layout.addWidget(line2)
        self.single_labels_layout.addWidget(self.single_sip_total_label)
        self.single_labels_layout.addWidget(line3)
        self.single_labels_layout.addWidget(self.single_pref_label)
        self.single_labels_layout.addStretch(1)
        
        # Store references to frames for highlighting
        self.single_left_frame = left_frame
        self.single_right_frame = right_frame
        
        single_plot_layout.addLayout(self.single_labels_layout)
        self.plot_stack.addWidget(self.single_plot_container)
    
    def setup_multi_arena_view(self):
        self.all_plots_widget = QWidget()
        self.all_plots_layout = QGridLayout()
        self.all_plots_layout.setSpacing(10)
        self.all_plots_layout.setContentsMargins(5, 5, 5, 5)
        self.all_plots_widget.setLayout(self.all_plots_layout)
        self.plot_stack.addWidget(self.all_plots_widget)
        
        self.all_plot_widgets = []
        self.all_data_items_left = []
        self.all_data_items_right = []
        
        self.all_sip_left_labels = []
        self.all_sip_right_labels = []
        self.all_sip_total_labels = []
        self.all_pref_labels = []
        
        # Store frames for highlighting
        self.all_left_frames = []
        self.all_right_frames = []
        
        # Store arena containers for recreating grid
        self.arena_containers = []
        
        # Initialize with all arenas visible
        self.visible_arena_count = NUM_ARENAS
        
        for i in range(NUM_ARENAS):
            arena_container = QWidget()
            self.arena_containers.append(arena_container)
            
            arena_layout = QVBoxLayout(arena_container)
            arena_layout.setContentsMargins(5, 5, 5, 5)
            arena_layout.setSpacing(5)
            
            plot = pg.PlotWidget(title=f"Arena {i+1}")
            plot.setYRange(0, MAX_CAPDAC_VALUE)
            arena_layout.addWidget(plot)
            

            left_curve = pg.PlotDataItem([], pen=pg.mkPen(color='r', width=2), name="Left Sensor") #red
            right_curve = pg.PlotDataItem([], pen=pg.mkPen(color='#39C5BB', width=2), name="Right Sensor")  # Light blue color
            plot.addItem(left_curve)
            plot.addItem(right_curve)
            
            # Add legend
            plot.addLegend(size=(80, 40), offset=(-10, 10))
            
            # Counter labels
            label_row = QHBoxLayout()
            label_row.setSpacing(10)
            
            # Create frames for stable highlighting
            left_frame = QFrame()
            left_frame.setFrameShape(QFrame.StyledPanel)
            left_frame.setMinimumWidth(60)
            left_layout = QHBoxLayout(left_frame)
            left_layout.setContentsMargins(5, 2, 5, 2)
            left_layout.setSpacing(0)
            sip_left_label = QLabel("Left: 0")
            left_layout.addWidget(sip_left_label)
            
            lineA = QFrame()
            lineA.setFrameShape(QFrame.VLine)
            lineA.setFrameShadow(QFrame.Sunken)
            
            right_frame = QFrame()
            right_frame.setFrameShape(QFrame.StyledPanel)
            right_frame.setMinimumWidth(60)
            right_layout = QHBoxLayout(right_frame)
            right_layout.setContentsMargins(5, 2, 5, 2)
            right_layout.setSpacing(0)
            sip_right_label = QLabel("Right: 0")
            right_layout.addWidget(sip_right_label)
            
            lineB = QFrame()
            lineB.setFrameShape(QFrame.VLine)
            lineB.setFrameShadow(QFrame.Sunken)
            
            sip_total_label = QLabel("Total: 0")
            lineC = QFrame()
            lineC.setFrameShape(QFrame.VLine)
            lineC.setFrameShadow(QFrame.Sunken)
            
            pref_label = QLabel("Pref: 0.00")
            
            # Add widgets to layout
            label_row.addWidget(left_frame)
            label_row.addWidget(lineA)
            label_row.addWidget(right_frame)
            label_row.addWidget(lineB)
            label_row.addWidget(sip_total_label)
            label_row.addWidget(lineC)
            label_row.addWidget(pref_label)
            label_row.addStretch(1)
            
            arena_layout.addLayout(label_row)
            
            # Add to grid initially
            row = i // 4
            col = i % 4
            self.all_plots_layout.addWidget(arena_container, row, col)
            
            # Store refs
            self.all_plot_widgets.append(plot)
            self.all_data_items_left.append(left_curve)
            self.all_data_items_right.append(right_curve)
            
            self.all_sip_left_labels.append(sip_left_label)
            self.all_sip_right_labels.append(sip_right_label)
            self.all_sip_total_labels.append(sip_total_label)
            self.all_pref_labels.append(pref_label)
            self.all_left_frames.append(left_frame)
            self.all_right_frames.append(right_frame)
    
    def highlight_sip(self, frame, highlight=True):
        """Highlight a frame without changing its size"""
        if highlight:
            frame.setStyleSheet("QFrame { background-color: #39C5BB; border-radius: 3px; }")
            # Create a timer to turn off the highlight
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.highlight_sip(frame, False))
            timer.start(500)  # 500ms highlight duration
        else:
            frame.setStyleSheet("")
    
    def scan_serial_ports(self):
        self.port_combo.clear()
        ftdi_ports, all_ports = FTDIConnection.scan_ports()
        if ftdi_ports:
            for port in ftdi_ports:
                self.port_combo.addItem(port["display"], port["device"])
            self.status_label.setText(f"Found {len(ftdi_ports)} FTDI device(s).")
        else:
            if all_ports:
                for port in all_ports:
                    self.port_combo.addItem(port["display"], port["device"])
                self.status_label.setText(f"No FTDI devices found. Showing all {len(all_ports)} port(s).")
            else:
                self.port_combo.addItem("No ports found")
                self.status_label.setText("No serial ports found.")
    
    def save_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self.custom_save_path = file_name
            self.status_label.setText(f"Will save to {file_name}")
    
    def update_arena_count(self):
        try:
            count = int(self.arena_count_input.text())
            if count < 1:
                count = 1
            elif count > NUM_ARENAS:
                count = NUM_ARENAS

            self.visible_arena_count = count
            self.recreate_arena_grid()
            self.status_label.setText(f"Showing {count} arenas")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number between 1 and 16.")
    
    def recreate_arena_grid(self):
        # Clear existing widgets from grid
        for i in reversed(range(self.all_plots_layout.count())): 
            self.all_plots_layout.itemAt(i).widget().setParent(None)
        for i in range(min(self.visible_arena_count, NUM_ARENAS)):
            arena_container = self.arena_containers[i]
            
            # Calculate position in grid (4 columns)
            row = i // 4
            col = i % 4
            
            # Add to grid
            self.all_plots_layout.addWidget(arena_container, row, col)
    
    def start_data_collection(self):
        # Check port
        port_name = self.port_combo.currentText()
        if not port_name or "No ports found" in port_name:
            QMessageBox.warning(self, "Warning", "No valid port selected.")
            return
        
        try:
            # Setup FTDI or sim
            if not self.debug_mode:
                success, self.serial_port = FTDIConnection.setup_device(port_name)
                if not success:
                    QMessageBox.critical(self, "Error", "Failed to connect to FTDI device.")
                    return
            
            # Setup data files
            custom_path = getattr(self, 'custom_save_path', None)
            logs_dir = self.data_logger.setup_files(custom_path)
            
            # Reset processor
            self.data_processor.reset()
            self.is_running = True
            
            # Reset previous counts
            self.prev_left_counts = [0] * NUM_ARENAS
            self.prev_right_counts = [0] * NUM_ARENAS
            
            # Set time for auto reset view
            self.start_time = time.time()
            self.auto_reset_done = False
            
            if self.debug_mode:
                self.data_thread = SimulatedDataReader(self.data_queue)
            else:
                self.data_thread = FTDIDataReader(self.data_queue, self.serial_port)
                
            self.data_thread.start()
            
            # Start UI updates
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_plots)
            self.timer.start(50)
            
            # Error checking timer - check every 2 seconds if we're still getting data
            self.error_check_timer = QTimer()
            self.error_check_timer.timeout.connect(self.check_connection_health)
            self.error_check_timer.start(2000)
            
            # Record when we started
            self.last_data_time = time.time()
            
            # Disable controls
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.scan_button.setEnabled(False)
            self.save_location_button.setEnabled(False)
            # Don't disable restart button - we want it available during collection
            
            if self.debug_mode:
                self.status_label.setText("Using SIMULATED data (for testing)")
            else:
                self.status_label.setText(f"Connected to {port_name}. Saving to {logs_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def check_connection_health(self):
        if not self.is_running:
            return
            
        # Check if we've received data recently (more than 5 seconds)
        if hasattr(self, 'last_data_time') and time.time() - self.last_data_time > 5:
            # Update status to show warning
            self.status_label.setText("Warning: No data received in the last 5 seconds. Check connection.")
            
        # Auto reset view after 1 second
        current_time = time.time()
        if not self.auto_reset_done and (current_time - self.start_time >= 1.0):
            print("Auto reset view after 1 second")
            self.reset_view()
            self.auto_reset_done = True
    
    def restart_test(self):
        # Show warning dialog first
        reply = QMessageBox.question(
            self,
            "Restart Test",
            "Are you sure you want to restart the test?\nThis will delete all current session data and start a new log file.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        # If user clicked No, just return
        if reply == QMessageBox.No:
            return
        
        # Check if we're currently running
        was_running = self.is_running
        
        # Stop current data collection if running
        if was_running:
            self.stop_data_collection()
        
        self.data_processor.reset()
        self.data_logger.close_files()
        
        custom_path = getattr(self, 'custom_save_path', None)
        logs_dir = self.data_logger.setup_files(custom_path)
        
        # Reset UI to view refreshed state
        self.reset_view()
        
        # Update status
        if custom_path:
            self.status_label.setText(f"Test restarted. Saving to custom location: {custom_path}")
        else:
            self.status_label.setText(f"Test restarted. Saving to {logs_dir}")
            
        if was_running:
            self.start_data_collection()
            
    def update_plots(self):
        got_data = False
        
        while not self.data_queue.empty():
            values = self.data_queue.get()
            got_data = True
            if isinstance(values, tuple) and len(values) == 2:
                left_values, right_values = values
            else:
                left_values = values
                right_values = [0] * len(values)
            
            # Process data
            self.data_processor.process_data(left_values, right_values)
            
            # Log data
            self.data_logger.log_sip_data(
                left_values, 
                right_values, 
                self.data_processor.left_counts,
                self.data_processor.right_counts
            )
        
        # Update last data time if we got data
        if got_data:
            self.last_data_time = time.time()
            # Clear any warning in status
            if "Warning: No data received" in self.status_label.text():
                if self.debug_mode:
                    self.status_label.setText("Using SIMULATED data (for testing)")
                else:
                    port_name = self.port_combo.currentText()
                    self.status_label.setText(f"Connected to {port_name}")
        
        # Update plots if there's data
        if self.data_processor.has_data():
            self.update_plot_display()
    
    def update_plot_display(self):
        if self.show_all_arenas:
            for i in range(min(self.visible_arena_count, NUM_ARENAS)):
                # Update left sensor
                if self.data_processor.data_left[i]:
                    self.all_data_items_left[i].setData(self.data_processor.data_left[i])
                
                # Update right sensor
                if self.data_processor.data_right[i]:
                    self.all_data_items_right[i].setData(self.data_processor.data_right[i])
                
                self.update_arena_labels(i, single_view=False)
        else:
            idx = self.current_arena_index
            # Update single view
            if self.data_processor.data_left[idx]:
                self.single_data_item_left.setData(self.data_processor.data_left[idx])
            
            if self.data_processor.data_right[idx]:
                self.single_data_item_right.setData(self.data_processor.data_right[idx])
                
            self.update_arena_labels(idx, single_view=True)
    
    def update_arena_labels(self, arena_index, single_view=False):
        left = self.data_processor.left_counts[arena_index]
        right = self.data_processor.right_counts[arena_index]
        total = left + right
        pref = (right - left)/total if total > 0 else 0
        
        # Check for new sips
        left_sip_detected = left > self.prev_left_counts[arena_index]
        right_sip_detected = right > self.prev_right_counts[arena_index]
        
        # Update previous counts
        self.prev_left_counts[arena_index] = left
        self.prev_right_counts[arena_index] = right
        
        if single_view:
            self.single_sip_left_label.setText(f"Left: {left}")
            self.single_sip_right_label.setText(f"Right: {right}")
            self.single_sip_total_label.setText(f"Total: {total}")
            self.single_pref_label.setText(f"Pref: {pref:.2f}")
            
            # Highlight frames if sips detected (won't shift layout)
            if left_sip_detected:
                self.highlight_sip(self.single_left_frame, True)
                
            if right_sip_detected:
                self.highlight_sip(self.single_right_frame, True)
        else:
            self.all_sip_left_labels[arena_index].setText(f"Left: {left}")
            self.all_sip_right_labels[arena_index].setText(f"Right: {right}")
            self.all_sip_total_labels[arena_index].setText(f"Total: {total}")
            self.all_pref_labels[arena_index].setText(f"Pref: {pref:.2f}")
            
            # Highlight frames if sips detected (won't shift layout)
            if left_sip_detected:
                self.highlight_sip(self.all_left_frames[arena_index], True)
                
            if right_sip_detected:
                self.highlight_sip(self.all_right_frames[arena_index], True)
    
    def stop_data_collection(self):
        self.is_running = False
        print("Stopped data collection")
        
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            
        if hasattr(self, 'error_check_timer') and self.error_check_timer.isActive():
            self.error_check_timer.stop()
        
        if self.data_thread:
            self.data_thread.stop()
            if hasattr(self.data_thread, 'join'):
                self.data_thread.join(timeout=1.0)
            self.data_thread = None
        
        if self.serial_port:
            try:
                self.serial_port.close()
                self.serial_port = None
            except:
                pass
        
        # Close files
        self.data_logger.close_files()
        
        # Enable controls
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.save_location_button.setEnabled(True)
        # Restart button remains enabled
        
        self.status_label.setText("Data collection stopped.")
    
    def reset_view(self):
        if self.show_all_arenas:
            for i, plot in enumerate(self.all_plot_widgets):
                if i < self.visible_arena_count:
                    plot.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
                    plot.autoRange()
        else:
            self.single_plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            self.single_plot_widget.autoRange()
        
        print("View reset applied")
    
    def change_arena(self, index):
        self.current_arena_index = index
        
        if not self.show_all_arenas:
            # Update plot with new arena's data
            if self.data_processor.data_left[index]:
                self.single_data_item_left.setData(self.data_processor.data_left[index])
            
            if self.data_processor.data_right[index]:
                self.single_data_item_right.setData(self.data_processor.data_right[index])
                
            self.reset_view()
            self.update_arena_labels(index, single_view=True)
    
    def toggle_show_all_arenas(self, checked):
        self.show_all_arenas = checked
        if self.show_all_arenas:
            self.plot_stack.setCurrentWidget(self.all_plots_widget)
            self.arena_selector.setEnabled(False)
        else:
            self.plot_stack.setCurrentWidget(self.single_plot_container)
            self.arena_selector.setEnabled(True)
            idx = self.current_arena_index
            
            if self.data_processor.data_left[idx]:
                self.single_data_item_left.setData(self.data_processor.data_left[idx])
            
            if self.data_processor.data_right[idx]:
                self.single_data_item_right.setData(self.data_processor.data_right[idx])
                
            self.update_arena_labels(idx, single_view=True)
    
    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        if self.is_running:
            self.stop_data_collection()
            self.start_data_collection()
    
    def closeEvent(self, event):
        self.stop_data_collection()
        event.accept()