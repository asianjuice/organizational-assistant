import time
import sys

# Gathering inputs
input_work = input("Please enter the number of minutes you would like to study for: ")
input_short_break = input("Please enter the number of minutes you would like your short break to be: ")
input_long_break = input("Please enter the number of minutes you would like your long break to be: ")
input_cycles = input("Please enter the number of cycles you would like to study for: ")

# Defining countdown function
def countdown(minutes):
    seconds = minutes * 60 # Converts the total number of minutes to seconds
    while seconds:
        mins, secs = divmod(seconds, 60) # Gets the value of total minutes and seconds by dividing the total by 60 (Sets up the minutes and seconds format)
        timer = '{:02d}:{:02d}'.format(mins, secs) # Formats the mins,secs into a readable output of Minutes:Seconds
        print(timer, end='\r')
        time.sleep(1)
        seconds -= 1

# Defining pomodoro_timer function
def pomodoro_timer(work_time, short_break_time, long_break_time, cycles): # Defines the funtion pomodoro_timer and lables the parameters
    for _ in range(cycles):
        print("To stop the timer please press Ctrl+C")
        print("Work for {} minutes".format(work_time))
        countdown(work_time)
        print("Have a short break for {} minutes".format(short_break_time))
        countdown(short_break_time)
        print("Work for {} minutes".format(work_time))
        countdown(work_time)
        print("Have a long break for {} minutes".format(long_break_time))
        countdown(long_break_time)

# If statement for using the inputs
if __name__ == "__main__":
    work_time = int(input_work)  # Minutes of work
    short_break_time = int(input_short_break)  # Short break time
    long_break_time = int(input_long_break) # Long break time
    cycles = int(input_cycles)      # Number of Cycles

try:
    pomodoro_timer(work_time, short_break_time, long_break_time, cycles)
except KeyboardInterrupt:
        print("\nTimer stopped.")
        sys.exit(0)
