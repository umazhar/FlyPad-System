#!/usr/bin/env python3

"""
STROBE - Data processing module
"""

from constants import *

class DataProcessor:
    """Processes sensor data and detects sips"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all data structures"""
        # Data arrays
        self.data_left = [[] for _ in range(NUM_ARENAS)]
        self.data_right = [[] for _ in range(NUM_ARENAS)]
        self.baseline_offsets_left = [0 for _ in range(NUM_ARENAS)]
        self.baseline_offsets_right = [0 for _ in range(NUM_ARENAS)]
        
        # Sip counters
        self.left_counts = [0 for _ in range(NUM_ARENAS)]
        self.right_counts = [0 for _ in range(NUM_ARENAS)]
        
        # State bits (0: not above, 1: left above, 2: right above, 3: both above)
        self.was_above_threshold = [0 for _ in range(NUM_ARENAS)]
        
        # Data counter
        self.historic_val_counter = 0
    
    def has_data(self):
        """Check if there's any data yet"""
        for data in self.data_left:
            if data:
                return True
        for data in self.data_right:
            if data:
                return True
        return False
    
    def process_data(self, left_values, right_values):
        """Process new sensor readings"""
        self.historic_val_counter += 1
        
        # Handle each arena
        for i in range(min(NUM_ARENAS, len(left_values), len(right_values))):
            self._process_arena_data(i, left_values[i], right_values[i])
    
    def _process_arena_data(self, arena_index, left_val, right_val):
        """Process single arena data"""
        # Process left sensor
        calibrated_left = left_val - self.baseline_offsets_left[arena_index]
        self.data_left[arena_index].append(calibrated_left)
        if len(self.data_left[arena_index]) > NUM_HISTORIC_VALUES:
            self.data_left[arena_index].pop(0)
        
        # Process right sensor
        calibrated_right = right_val - self.baseline_offsets_right[arena_index]
        self.data_right[arena_index].append(calibrated_right)
        if len(self.data_right[arena_index]) > NUM_HISTORIC_VALUES:
            self.data_right[arena_index].pop(0)
        
        # Check for sips
        self._detect_sips(arena_index, left_val, right_val)
    
    def _detect_sips(self, arena_index, left_val, right_val):
        """Detect sips for an arena"""
        # Get current state of each sensor
        left_was_above = self.was_above_threshold[arena_index] & 1
        right_was_above = (self.was_above_threshold[arena_index] & 2) >> 1
        
        # Debug print if values are high
        if left_val > LEFT_SIP_THRESHOLD or right_val > RIGHT_SIP_THRESHOLD:
            print(f"Arena {arena_index+1}: Left={left_val} (was_above={left_was_above}), Right={right_val} (was_above={right_was_above})")
        
        # Right sensor triggers left counter
        left_above_threshold = (right_val > LEFT_SIP_THRESHOLD)
        if left_above_threshold and not left_was_above:
            self.left_counts[arena_index] += 1
            print(f"LEFT SIP DETECTED - Arena {arena_index+1}, Value: {right_val}")
            self.was_above_threshold[arena_index] |= 1
        elif not left_above_threshold:
            self.was_above_threshold[arena_index] &= ~1
        
        # Left sensor triggers right counter
        right_above_threshold = (left_val > RIGHT_SIP_THRESHOLD)
        if right_above_threshold and not right_was_above:
            self.right_counts[arena_index] += 1
            print(f"RIGHT SIP DETECTED - Arena {arena_index+1}, Value: {left_val}")
            self.was_above_threshold[arena_index] |= 2
        elif not right_above_threshold:
            self.was_above_threshold[arena_index] &= ~2
    
    def reset_baseline(self, current_arena_index, all_arenas=False):
        """Reset the baseline calibration"""
        if all_arenas:
            for i in range(NUM_ARENAS):
                self._reset_arena_baseline(i)
        else:
            self._reset_arena_baseline(current_arena_index)
    
    def _reset_arena_baseline(self, arena_index):
        """Reset baseline for one arena"""
        # Reset left sensor baseline
        if self.data_left[arena_index]:
            current_value_left = self.data_left[arena_index][-1] + self.baseline_offsets_left[arena_index]
        else:
            current_value_left = 0
        self.baseline_offsets_left[arena_index] = current_value_left
        
        # Reset right sensor baseline
        if self.data_right[arena_index]:
            current_value_right = self.data_right[arena_index][-1] + self.baseline_offsets_right[arena_index]
        else:
            current_value_right = 0
        self.baseline_offsets_right[arena_index] = current_value_right
        
        print(f"Baseline reset: Arena {arena_index+1} - Left: {current_value_left}, Right: {current_value_right}")