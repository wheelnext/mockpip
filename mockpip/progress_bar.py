import sys
import time


def progress_bar(current, bar_length=40):
    """
    Displays a progress bar in the terminal.
    Args:
        current (int): The current progress value.
        bar_length (int): The length of the progress bar in characters.
    """
    fraction = current / 100
    arrow = "=" * int(fraction * bar_length)  # Progress indicator
    spaces = " " * (bar_length - len(arrow))  # Remaining space
    percent = int(fraction * 100)  # Percentage complete

    # Print the progress bar
    sys.stdout.write(f"\r[{arrow}{spaces}] {percent}%")
    sys.stdout.flush()


def fake_install_progress(total_time=5):
    for i in range(101):
        progress_bar(i)
        time.sleep(total_time/100)
    sys.stdout.write("\n")
