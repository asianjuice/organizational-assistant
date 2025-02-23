import time
import sys

def countdown(minutes):
    seconds = minutes * 60 # Converts the total number of minutes to seconds
    while seconds:
        mins, secs = divmod(seconds, 60) # Gets the value of total minutes and seconds by dividing the total by 60 (Sets up the minutes and seconds format)
        timer = '{:02d}:{:02d}'.format(mins, secs) # Formats the mins,secs into a readable output of Minutes:Seconds
        print(timer, end='\r')
        time.sleep(1)
        seconds -= 1

def pomodoro_timer(work_time, short_break_time, long_break_time, cycles): # Defines the funtion pomodoro_timer and lables the parameters
    for _ in range(cycles):
        print("Work for {} minutes".format(work_time))
        countdown(work_time)
        print("Have a short break for {} minutes".format(short_break_time))
        countdown(short_break_time)
        print("Work for {} minutes".format(work_time))
        countdown(work_time)
        print("Have a long break for {} minutes".format(long_break_time))
        countdown(long_break_time)
if __name__ == "__main__":
    work_time = 25  # Minutes of work
    short_break_time = 5  # Short break time
    long_break_time = 10 # Long break time
    cycles = 2      # Number of Cycles

    try:
        pomodoro_timer(work_time, short_break_time, long_break_time, cycles)
    except KeyboardInterrupt:
        print("\nTimer interrupted.")
        sys.exit(0)
