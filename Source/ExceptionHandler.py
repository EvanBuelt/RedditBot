import time
import prawcore.exceptions as praw_exceptions
__author__ = 'Evan'


def praw_caller(function_call, default_return, debug_message, *args):
    return_object = default_return
    processed = False
    wait_times = [1, 2, 4, 8, 16, 32]
    index = 0

    while not processed:
        try:
            return_object = function_call(*args)

            processed = True
        except praw_exceptions.PrawcoreException:
            print debug_message
            if index >= len(wait_times):
                break
            sleep_time = wait_times[index]
            time.sleep(sleep_time)
            print "Waited: ", sleep_time
            index += 1
    return return_object
