import winsound

def sound_one_file():
    duration = 1000  # milliseconds
    freq = 440  # Hz
    winsound.Beep(freq, duration)


def sound_files():
    duration = 5000  # milliseconds
    freq = 400  # Hz
    winsound.Beep(freq, duration)