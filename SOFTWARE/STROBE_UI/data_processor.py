#!/usr/bin/env python3

"""
STROBE - Data processing module
"""

from constants import *
import numpy as np

class DataProcessor:    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.data_left = [[] for _ in range(NUM_ARENAS)]
        self.data_right = [[] for _ in range(NUM_ARENAS)]
        self.left_counts = [0 for _ in range(NUM_ARENAS)]
        self.right_counts = [0 for _ in range(NUM_ARENAS)]
        
        # Previous values for change detection
        self.prev_left_values = [0 for _ in range(NUM_ARENAS)]
        self.prev_right_values = [0 for _ in range(NUM_ARENAS)]
        
        # Sip state tracking (0: no sip in progress, 1: sip in progress, 2: in cooldown)
        self.left_sensor_state = [0 for _ in range(NUM_ARENAS)]
        self.right_sensor_state = [0 for _ in range(NUM_ARENAS)]
        
        # Sip timing tracking
        self.left_sensor_sip_start_time = [0 for _ in range(NUM_ARENAS)]
        self.right_sensor_sip_start_time = [0 for _ in range(NUM_ARENAS)]
        
        # Cooldown tracking
        self.left_sensor_cooldown_until = [0 for _ in range(NUM_ARENAS)]
        self.right_sensor_cooldown_until = [0 for _ in range(NUM_ARENAS)]
        
        # Data counter
        self.historic_val_counter = 0
        
        # Configuration for sip detection
        self.change_threshold = MIN_THRESHOLD      # Minimum change to trigger a potential sip
        self.min_sip_time = MIN_SIP_TIME           # Minimum readings that constitute a sip (at 10Hz, 5 = 500ms)
        self.cooldown_time = COOLDOWN_TIME        # Readings to wait before allowing another sip (at 10Hz, 150 = 15s)
    
    def has_data(self):
        for data in self.data_left:
            if data:
                return True
        for data in self.data_right:
            if data:
                return True
        return False
    
    def process_data(self, left_values, right_values):
        self.historic_val_counter += 1
        
        # Handle each arena
        for i in range(min(NUM_ARENAS, len(left_values), len(right_values))):
            self._process_arena_data(i, left_values[i], right_values[i])
    
    def _process_arena_data(self, arena_index, left_val, right_val):
        # Process left sensor
        self.data_left[arena_index].append(left_val)
        if len(self.data_left[arena_index]) > NUM_HISTORIC_VALUES:
            self.data_left[arena_index].pop(0)
        
        # Process right sensor
        self.data_right[arena_index].append(right_val)
        if len(self.data_right[arena_index]) > NUM_HISTORIC_VALUES:
            self.data_right[arena_index].pop(0)
                
        self._process_left_sensor_for_right_sips(arena_index, left_val)
        
        self._process_right_sensor_for_left_sips(arena_index, right_val)
        self.prev_left_values[arena_index] = left_val
        self.prev_right_values[arena_index] = right_val
    
    def _process_left_sensor_for_right_sips(self, arena_index, left_val):
        # Calculate change from previous value
        change = abs(left_val - self.prev_left_values[arena_index])
        current_time = self.historic_val_counter
        
        # Check if we're in cooldown, if not in cooldown, reset state
        if self.left_sensor_state[arena_index] == 2:
            if current_time > self.left_sensor_cooldown_until[arena_index]:
                self.left_sensor_state[arena_index] = 0
                print(f"Arena {arena_index+1}: Right sensor cooldown ended")
            else:
                # Still in cooldown, ignore this reading
                return
        
        if change > self.change_threshold:
            print(f"Arena {arena_index+1}: Right sensor change={change}")
        
        # State 0: No sip in progress - check for start of sip
        if self.left_sensor_state[arena_index] == 0:
            if change > self.change_threshold:
                # Start tracking a potential sip
                self.left_sensor_state[arena_index] = 1
                self.left_sensor_sip_start_time[arena_index] = current_time
                print(f"Potential RIGHT sip starting - Arena {arena_index+1}, Change: {change}")
        
        # State 1: Sip in progress - check for completion or timeout
        elif self.left_sensor_state[arena_index] == 1:
            sip_duration = current_time - self.left_sensor_sip_start_time[arena_index]
            
            if change > self.change_threshold and sip_duration >= self.min_sip_time:
                # Count the sip
                self.right_counts[arena_index] += 1
                print(f"RIGHT SIP DETECTED - Arena {arena_index+1}, Duration: {sip_duration} samples")
                
                # Enter cooldown state
                self.left_sensor_state[arena_index] = 2
                self.left_sensor_cooldown_until[arena_index] = current_time + self.cooldown_time
                print(f"Arena {arena_index+1}: Right sensor entering cooldown for {self.cooldown_time} samples")
            
            # Check for timeout (sip took too long to complete)
            elif sip_duration > 20:  # Timeout for sip in progress
                print(f"Arena {arena_index+1}: Right sip timeout - resetting")
                self.left_sensor_state[arena_index] = 0
    
    def _process_right_sensor_for_left_sips(self, arena_index, right_val):
        # Calculate change from previous value
        change = abs(right_val - self.prev_right_values[arena_index])
        current_time = self.historic_val_counter
        
        if self.right_sensor_state[arena_index] == 2:
            if current_time > self.right_sensor_cooldown_until[arena_index]:
                self.right_sensor_state[arena_index] = 0
                print(f"Arena {arena_index+1}: Left sensor cooldown ended")
            else:
                # Still in cooldown, ignore this reading
                return
        
        # Debug print for large changes
        if change > self.change_threshold:
            print(f"Arena {arena_index+1}: Left sensor change={change}")
        
        # State 0: No sip in progress - check for start of sip
        if self.right_sensor_state[arena_index] == 0:
            if change > self.change_threshold:
                # Start tracking a potential sip
                self.right_sensor_state[arena_index] = 1
                self.right_sensor_sip_start_time[arena_index] = current_time
                print(f"Potential LEFT sip starting - Arena {arena_index+1}, Change: {change}")
        
        # State 1: Sip in progress - check for completion or timeout
        elif self.right_sensor_state[arena_index] == 1:
            sip_duration = current_time - self.right_sensor_sip_start_time[arena_index]
            
            # Check if this is the end of a valid sip
            if change > self.change_threshold and sip_duration >= self.min_sip_time:
                # Count the sip
                self.left_counts[arena_index] += 1
                print(f"LEFT SIP DETECTED - Arena {arena_index+1}, Duration: {sip_duration} samples")
                
                # Enter cooldown state
                self.right_sensor_state[arena_index] = 2
                self.right_sensor_cooldown_until[arena_index] = current_time + self.cooldown_time
                print(f"Arena {arena_index+1}: Left sensor entering cooldown for {self.cooldown_time} samples")
            
            # Check for timeout (sip took too long to complete)
            elif sip_duration > 20:  # Timeout for sip in progress
                print(f"Arena {arena_index+1}: Left sip timeout - resetting")
                self.right_sensor_state[arena_index] = 0