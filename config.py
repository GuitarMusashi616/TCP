# Austin Williams
# Shawn Butler
# Computer Networks
# 11 November 2020

# config.py - Configurations used to run the program

MSL = 0                     # TimeWait states waits 2*MSL before closing
VERBOSE = True             # Prints each header's seq_num and ack_num
PRINT_ERRORS = True         # Prints when an unexpected seq_num/ack_num is encountered
TIMEOUT_SECS = 3            # Waits TIMEOUT seconds when waiting for a response
ATTEMPTS_UNTIL_EXIT = 3     # Retries waiting for a response ATTEMPTS_UNTIL_EXIT times
MAX_DATA_SIZE = 1452        # The maximum number of bytes that can be attached to a header