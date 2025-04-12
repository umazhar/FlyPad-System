import csv
import strobelib
import numpy as np
import os
import re
import string

# defaults
DURATION_FILTER_MODE = False
MIN_DURATION = 0
CUMULATIVE_SIPS_MODE = False
DURATION_SIPS_MODE = False
BINNED_SIPS_MODE = False # seems like a finite state machine
TIME_BIN = 1
TIME_CUM_BIN_SIPS = 1
TOTAL_NUM_SIPS = False
PREF_INDEX = False
IMPOSSIBLE_PREF_INDEX = -999999999999999 # what does pref stand for

START_TIME = 0
STOP_TIME = None

# filename constants
cum_sips_base = "cumulative_sips_vs_time"
cum_bin_sips_base = "cumulative_bin_sips_vs_time"
binned_sips_base = "binned_rising_edges"
sip_durations_base = "sip_durations"
total_num_sips_base = "total_num_sips"
total_sips_base = "total_sips"
pref_index_base = "pref_index" # preference index -> what is the preference index?

# base main
if __name__ == '__main__':
    raw_filename = input("Please enter the path to your cap data file "
        "(output from the STROBE system):\n")
    
    # assume drag and drop filename
    filename = str.replace(raw_filename, "\\", "/")
    filename = re.sub(r'^"|"$', '', filename) # remove double quotes from string
    
    assert os.path.exists(filename), "I did not find the file at " + str(filename)  
    
    # user sets options here
    custom_startstop_query = input("Custom start/stop? (Y/N):\n")
    CUSTOM_STARTSTOP_MODE = strobelib.parse_YN_query(custom_startstop_query)
    
    if CUSTOM_STARTSTOP_MODE:
        start_query = input("Enter the start point as an integer "
            "(amount of time per bin divided by 10 ms):\n") # what do they mean by bin here.... like the individual sensors?
        START_TIME = strobelib.parse_numeric_query(
            start_query, START_TIME)
            
        stop_query = input("Enter the stop point as an integer "
            "(amount of time per bin divided by 10 ms):\n")
        STOP_TIME = strobelib.parse_numeric_query(
            stop_query, STOP_TIME)
        # we could potentially add option here to have custom start but not custom stop (ie it automatically runs to the end of the file)

    duration_filter_query = input("Filter sips of duration "
        "less than n? (Y/N):\n")
    DURATION_FILTER_MODE = strobelib.parse_YN_query(duration_filter_query)
    
    if DURATION_FILTER_MODE:
        min_duration_filter_query = input("Enter the minimum duration "
            "for a sip as an integer (eg, such that all sips of smaller "
            "duration will be filtered out):\n")
        MIN_DURATION = strobelib.parse_numeric_query(
            min_duration_filter_query, MIN_DURATION)

    cum_sips_query = input("Calculate and save cumulative sips vs "
        "time? (Y/N):\n")
    CUMULATIVE_SIPS_MODE = strobelib.parse_YN_query(cum_sips_query)
    if CUMULATIVE_SIPS_MODE:
        cum_bin_sips_query = input("Bin cumulative number of sips vs time? (Y/N):\n")
        CUMULATIVE_BIN_SIPS_MODE = strobelib.parse_YN_query(cum_bin_sips_query)

        if CUMULATIVE_BIN_SIPS_MODE:
            time_cum_bin_sips_query = input("Enter the ideal time bin as an integer "
            "(amount of time per bin divided by 10 ms):\n")
            TIME_CUM_BIN_SIPS = strobelib.parse_numeric_query(time_cum_bin_sips_query, TIME_CUM_BIN_SIPS)
    
    duration_sips_query = input("Calculate and save sip durations? (Y/N):\n")
    DURATION_SIPS_MODE = strobelib.parse_YN_query(duration_sips_query)
    
    binned_sips_query = input("Calculate and save binned number of sips? "
        "(eg number of sips in 1 minute, or number of sips in 30 seconds) (Y/N):\n")
    BINNED_SIPS_MODE = strobelib.parse_YN_query(binned_sips_query)
    
    if BINNED_SIPS_MODE:
        time_bin_query = input("Enter the ideal time bin as an integer "
            "(amount of time per bin divided by 10 ms):\n")
        TIME_BIN = strobelib.parse_numeric_query(time_bin_query, TIME_BIN)
        
    total_num_sips_query = input("Calculate and save total "
        "number of sips? (Y/N):\n")
    TOTAL_NUM_SIPS = strobelib.parse_YN_query(total_num_sips_query)
        
    if TOTAL_NUM_SIPS:
        total_sips_experiment = []

    pref_index_query = input("Calculate and save the preference index? (Y/N):\n")
    PREF_INDEX = strobelib.parse_YN_query(pref_index_query)

    if PREF_INDEX:
       pref_index = []

    data_frame = strobelib.read_dataframe(filename, START_TIME, STOP_TIME); # why is there a semicolon
    print("Successfully read datafile") # just some brackets?
    
    for arena_num in range(0, strobelib.NUM_ARENAS):
        CH1_values, CH2_values, LED1_values, LED2_values = strobelib.read_arena_values(data_frame, arena_num)
    
        if DURATION_FILTER_MODE:
            LED1_values = strobelib.filter_LED_values_by_duration(LED1_values, MIN_DURATION)
            LED2_values = strobelib.filter_LED_values_by_duration(LED2_values, MIN_DURATION)

        if CUMULATIVE_SIPS_MODE:
            if not CUMULATIVE_BIN_SIPS_MODE:
                cum_sips_1 = strobelib.cumulative_sips(LED1_values)
                cum_sips_2 = strobelib.cumulative_sips(LED2_values)
                strobelib.save_calculations(cum_sips_base, arena_num, cum_sips_1, cum_sips_2, "%s_cum_sips" % filename)
            else:
                cum_bin_sips_1 = strobelib.cumulative_bin_sips(LED1_values, TIME_CUM_BIN_SIPS)
                cum_bin_sips_2 = strobelib.cumulative_bin_sips(LED2_values, TIME_CUM_BIN_SIPS)
                strobelib.save_calculations(cum_bin_sips_base, arena_num, cum_bin_sips_1, cum_bin_sips_2, "%s_cum_bin_sips" % filename)

        if DURATION_SIPS_MODE:
            sip_durations_1 = strobelib.sip_duration(LED1_values)
            sip_durations_2 = strobelib.sip_duration(LED2_values)
            strobelib.save_calculations(sip_durations_base, arena_num, sip_durations_1, sip_durations_2, "%s_sips_dur" % filename)

        if BINNED_SIPS_MODE:
            rising_edges_1 = strobelib.bin_rising_edges(LED1_values, TIME_BIN)
            rising_edges_2 = strobelib.bin_rising_edges(LED2_values, TIME_BIN)
            strobelib.save_calculations(binned_sips_base, arena_num, rising_edges_1, rising_edges_2, "%s_bin_sips" % filename)
            if TOTAL_NUM_SIPS:
                total_num_sips_1 = sum(rising_edges_1)
                total_num_sips_2 = sum(rising_edges_2)
                total_sips_experiment.append([total_num_sips_1, total_num_sips_2])
                
        if not BINNED_SIPS_MODE and TOTAL_NUM_SIPS:
                rising_edges_1 = strobelib.bin_rising_edges(LED1_values, TIME_BIN)
                rising_edges_2 = strobelib.bin_rising_edges(LED2_values, TIME_BIN)
                total_num_sips_1 = sum(rising_edges_1)
                total_num_sips_2 = sum(rising_edges_2)
                total_sips_experiment.append([total_num_sips_1, total_num_sips_2])
                if PREF_INDEX:
                    if not (total_num_sips_1 == 0 and total_num_sips_1 == 0):
                        preference = float(total_num_sips_1 - total_num_sips_2)/(total_num_sips_1 + total_num_sips_2) #DEFINITION OF PREFERENCE INDEX
                    else:
                        preference = IMPOSSIBLE_PREF_INDEX
                    pref_index.append(preference)
    
    if TOTAL_NUM_SIPS:
        os.getcwd()
        np.savetxt('%s_%s.txt' % (filename, total_sips_base), total_sips_experiment, delimiter='\n', fmt='%10.5f')
        if PREF_INDEX:
            np.savetxt('%s_%s.txt' % (filename, pref_index_base), pref_index, delimiter='\n', fmt='%10.5f')
