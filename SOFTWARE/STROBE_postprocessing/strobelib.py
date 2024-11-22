import csv
from collections import deque
from itertools import islice
import numpy as np
import os

# base function library
# system-specific constants
NUM_DATAVALS_PER_ARENA = 4
NUM_ARENAS = 16
NUM_DATAFRAME_VALUES = 64
MAX_CAPDAC_VALUE = 4095
CH1_INTERNAL_DATAVAL_INDEX = 0
CH2_INTERNAL_DATAVAL_INDEX = 1
LED1_INTERNAL_DATAVAL_INDEX = 2
LED2_INTERNAL_DATAVAL_INDEX = 3

# GUI constants
LED_GRAPHICAL_SCALE = 2000;
NUM_ARENAS_PER_GUI_ROW = 6;

# simulation constants
LED_ON = 1
LED_OFF = 0
NUM_HISTORIC_VALUES = 10
NOISE_LEVEL = 100
NULL_VALUE = -1

# option setting
def parse_numeric_query(query, NUMERIC_DEFAULT):
    """
    Takes a string from user as input. Attempts to parse and return
    integer representation, returns passed numeric default if unsuccessful
    """
    try:
        int_query = int(query)
        print ("Option set to %s" % int_query)
    except ValueError:
        print ("Could not parse answer as integer, defaulting to %s" % NUMERIC_DEFAULT)
        int_query = NUMERIC_DEFAULT
    return int_query

def parse_YN_query(query):
    if (query == "Y" or query == "YES" or query == "y" or query == "yes"):
        print("Option set to Yes")
        return True
    elif (query == "N" or query == "NO" or query == "n" or query == "no"):
        print("Option set to No")
        return False
    else:
        print ("Could not parse answer, option defaulting to No")
        return False

# file IO stuff
# TODO: rewrite
# from SO http://stackoverflow.com/a/14350444
def replace_element(lst, new_element, indices):
    for i in indices:
        lst[i] = new_element
    return lst

def read_dataframe(filename, START_TIME, STOP_TIME):
    """
    Takes a STROBE system datafile as input; parses into a 
    NUM_DATAFRAME_VALUES x n dataframe
    """
    dataframe = [[0]*0 for i in range(NUM_DATAFRAME_VALUES)] #i believe this becomes a vector?
    datafile = csv.reader(open('%s' % filename, 'r'), delimiter="\n")
    
    if STOP_TIME != None:
        assert START_TIME < STOP_TIME

    for i,datarow in enumerate(datafile):
        if STOP_TIME != None:
            if i >= START_TIME and i < STOP_TIME:
                split_datarow = datarow[0].split('\t')
                for i in range(0, NUM_DATAFRAME_VALUES):
                    dataframe[i].append(split_datarow[i])
        else:
            if i >= START_TIME:
                split_datarow = datarow[0].split('\t')
                for i in range(0, NUM_DATAFRAME_VALUES):
                    dataframe[i].append(split_datarow[i])
    return dataframe # so i believe this is a matrix. And we access separate rows in the following function

def read_arena_values(dataframe, arena_num):
    """
    Takes a STROBE system dataframe as input; returns tuple of
    CH1, CH2, LED1, LED2 values for a given arena.
    """
    offset = arena_num * NUM_DATAVALS_PER_ARENA
    CH1_values = dataframe[offset + CH1_INTERNAL_DATAVAL_INDEX]
    # CH1_values_length = len(list(map(int, dataframe[offset + CH1_INTERNAL_DATAVAL_INDEX])))
    CH2_values = dataframe[offset + CH2_INTERNAL_DATAVAL_INDEX]
    # CH2_values_length = len(list(map(int, dataframe[offset + CH2_INTERNAL_DATAVAL_INDEX])))
    LED1_values = dataframe[offset + LED1_INTERNAL_DATAVAL_INDEX]
    # LED1_values_length = len(list(map(int, dataframe[offset + LED1_INTERNAL_DATAVAL_INDEX])))
    LED2_values = dataframe[offset + LED2_INTERNAL_DATAVAL_INDEX]
    # LED2_values_length = len(list(map(int, dataframe[offset + LED2_INTERNAL_DATAVAL_INDEX])))

    # convert numbers from str representation to int
    CH1_values = list(map(int, CH1_values))
    CH2_values = list(map(int, CH2_values))
    LED1_values = list(map(int, LED1_values))
    LED2_values = list(map(int, LED2_values))

    return(CH1_values, CH2_values, LED1_values, LED2_values)

def save_calculations(base, arena_num, LED1_array, LED2_array, dirpath):
    """
    Takes calculated values on LED1 data as LED1_array, same for LED2
    as input. Takes base filename and arena num as input.
    Saves calculated values for each LED as a separate text files.
    Ensures passed dirpath exists in the current working directory.
    """
    
    os.getcwd()
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    
    np.savetxt('%s/%s_arena_%s_ch1.txt' % (dirpath, base, arena_num), 
        LED1_array, delimiter='\n', fmt='%10.5f')
    np.savetxt('%s/%s_arena_%s_ch2.txt' % (dirpath, base, arena_num), 
        LED2_array, delimiter='\n', fmt='%10.5f')
    return

# calculations  
def filter_LED_values_by_duration(LED_values, MIN_DURATION):
    """
    
    """
    filtered_LED_values = list(LED_values)
    LED_value_prev = 0
    current_LED_value_index = 0
    while (current_LED_value_index < len(LED_values)):
        current_sip_duration = 0
        LED_value = LED_values[current_LED_value_index]
        # if 0 1 pattern
        if (LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == 0):
            # while 1 1... pattern
            while (LED_value == LED_GRAPHICAL_SCALE * LED_ON):
                current_sip_duration += 1
                LED_value_prev = LED_value
                current_LED_value_index += 1
                if current_LED_value_index < len(LED_values):
                    LED_value = LED_values[current_LED_value_index]
                else:
                    break
            # if final duration of the sip that just finished is less than the min
            if (current_sip_duration < MIN_DURATION):
                filtered_LED_values = replace_element(filtered_LED_values, 
                    LED_OFF, range(current_LED_value_index - current_sip_duration, 
                    current_LED_value_index)) # so here, we're overwriting it to say LED_OFF to show that we don't care about this segment and it's as if it was off that whole time
        current_LED_value_index += 1
        LED_value_prev = LED_value

    return filtered_LED_values
    
def calculate_LED_values(CH_values): # this function is never used it seems
    LED_values = []
    sliding_window = deque([NULL_VALUE]*NUM_HISTORIC_VALUES)
    for ch_value in CH_values:
        ch_value = int(ch_value)
        minima = int(min(sliding_window))
        if (ch_value > minima) and (ch_value - minima > NOISE_LEVEL):
            LED_values.append(LED_ON * LED_GRAPHICAL_SCALE)
        else:
            LED_values.append(LED_OFF * LED_GRAPHICAL_SCALE)
        sliding_window.popleft()
        sliding_window.append(ch_value)
    return LED_values

def cumulative_sips(LED_values):
    cumulative_rising_edges = []
    LED_value_prev = 0
    num_rising_edges = 0
    for LED_value in LED_values:
        if (LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF):
            num_rising_edges += 1
        cumulative_rising_edges.append(num_rising_edges)
        LED_value_prev = LED_value
    return cumulative_rising_edges

def cumulative_bin_sips(LED_values, TIME_BIN):
    splittable_index = int(len(LED_values)/TIME_BIN)
    assert (splittable_index != 0), "Your time bin is greater than the length of your dataset!"
    binned_LED_values = np.split(np.array(LED_values[0:splittable_index * TIME_BIN]), splittable_index);
    rising_edges = []
    LED_value_prev = 0
    num_rising_edges = 0
    for binned_subarray in binned_LED_values:
        for LED_value in binned_subarray:
            if ((LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF)):
                num_rising_edges += 1
            LED_value_prev = LED_value
        rising_edges.append(num_rising_edges)
    for LED_value in LED_values[splittable_index * TIME_BIN:]:
        if ((LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF)):
            num_rising_edges += 1
        LED_value_prev = LED_value
    rising_edges.append(num_rising_edges)
    return rising_edges

def bin_rising_edges(LED_values, TIME_BIN):
    splittable_index = int(len(LED_values)/TIME_BIN)
    #print("length of list: " + str(LED_val_length))
    assert (splittable_index != 0), "Your time bin is greater than the length of your dataset!"
    binned_LED_values = np.split(np.array(LED_values[0:splittable_index * TIME_BIN]), splittable_index);
    rising_edges = []
    LED_value_prev = 0
    for binned_subarray in binned_LED_values:
        num_rising_edges = 0
        for LED_value in binned_subarray:
            if ((LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF)):
                num_rising_edges += 1
            LED_value_prev = LED_value
        rising_edges.append(num_rising_edges)
    num_rising_edges = 0
    for LED_value in LED_values[splittable_index * TIME_BIN:]:
        if ((LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF)):
            num_rising_edges += 1
        LED_value_prev = LED_value
    rising_edges.append(num_rising_edges)
    return rising_edges
    
def sip_duration(LED_values):
    # calculate sip duration
    LED_value_prev = 0
    sip_duration_array = []
    current_LED_value_index = 0
    while (current_LED_value_index < len(LED_values)):
        current_sip_duration = 0
        LED_value = LED_values[current_LED_value_index]
        if (LED_value == LED_GRAPHICAL_SCALE * LED_ON) and (LED_value_prev == LED_OFF):
            while (LED_value == LED_GRAPHICAL_SCALE * LED_ON):
                current_sip_duration += 1
                LED_value_prev = LED_value
                current_LED_value_index += 1
                if current_LED_value_index < len(LED_values):
                    LED_value = LED_values[current_LED_value_index]
                else:
                    break
            sip_duration_array.append(current_sip_duration)
        current_LED_value_index += 1
        LED_value_prev = LED_value
    return sip_duration_array

# sip duration and LED duration are very similar functions

# only thing i don't understand is the bins