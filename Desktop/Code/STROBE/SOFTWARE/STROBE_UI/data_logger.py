#!/usr/bin/env python3

"""
STROBE - Data logger for saving files
"""

import os
import datetime
from constants import NUM_ARENAS

class DataLogger:    
    def __init__(self):
        self.sip_data_file = None
    
    def setup_files(self, custom_path=None):
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_path:
            sip_file_path = custom_path
        else:
            sip_filename = f"sip_data_{timestamp}.csv"
            sip_file_path = os.path.join(logs_dir, sip_filename)

        # CSV
        header = ["Timestamp"]
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_Left")
            header.append(f"Arena{i+1}_Right")
        for i in range(NUM_ARENAS):
            header.append(f"Arena{i+1}_LeftCount")
            header.append(f"Arena{i+1}_RightCount")
            header.append(f"Arena{i+1}_TotalCount")
            header.append(f"Arena{i+1}_Preference")
        
        self.sip_data_file = open(sip_file_path, "w")
        self.sip_data_file.write(",".join(header) + "\n")
        
        return logs_dir
    
    def log_sip_data(self, left_values, right_values, left_counts, right_counts):
        if not self.sip_data_file:
            return
            
        try:
            timestamp = datetime.datetime.now().isoformat()
            row = [timestamp]

            for i in range(min(NUM_ARENAS, len(left_values))):
                row.append(str(left_values[i]))
            
            for i in range(min(NUM_ARENAS, len(right_values))):
                row.append(str(right_values[i]))
            
            # Add sip stats
            for i in range(NUM_ARENAS):
                left = left_counts[i]
                right = right_counts[i]
                total = left + right
                pref = (left - right)/total if total > 0 else 0
                row.append(str(left))
                row.append(str(right))
                row.append(str(total))
                row.append(f"{pref:.3f}")
            
            self.sip_data_file.write(",".join(row) + "\n")
            self.sip_data_file.flush()
        except Exception as e:
            print(f"Sip data error: {e}")
    
    def close_files(self):
        if self.sip_data_file:
            self.sip_data_file.close()
            self.sip_data_file = None