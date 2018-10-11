import argparse
import curses
import numpy as np
import pyaudio

def get_args():
    # Grab some parameters from the user.
    parser = argparse.ArgumentParser(description='Two-Channel Pure Tone (Sine) Generator')
    parser.add_argument('--freq',     default=440.0, type=float,          help='Frequency of the tone to be generated (default: {})'.format(440.0))
    parser.add_argument('--lag',      default=0,     type=int,            help='Number of frames to lag the left channel by (default: {})'.format(0))
    parser.add_argument('--samp',     default=48000, type=int,            help='Sampling rate (in Hz) for the pure tone. (default: {})'.format(48000))
    args = parser.parse_args()
    return args

def main(stdscr):
    
    # Get parameters from a user.
    args = get_args()
    
    # Set these parameters.
    frequency      =  args.freq
    lag_channel    =  args.lag
    sampling_rate  =  args.samp
    duration       =  0.1
    pause_sound    =  True
    play_program   =  True
    First          =  True

    # For paFloat32 sample values must be in range [-1.0, 1.0]
    p = pyaudio.PyAudio()
    stream = p.open (
        format=pyaudio.paFloat32,
        channels=2,
        rate=sampling_rate,
        output=True
    )
    
    # do not wait for input when calling getch
    stdscr.nodelay(1)
    while play_program:

        # get keyboard input, returns -1 if none available
        c = stdscr.getch()
        stdscr.move(0, 0)

        #
        # Event List
        #
        if c == 32: # Space-Bar
            pause_sound = not pause_sound

        if c == 119: # W
            frequency += 20.0

        if c == 115: # S
            frequency += -20.0

        if c == 100: # D
            lag_channel += 1

        if c == 97: # A
            lag_channel += -1

        if c == 107: # K
            play_program = False


        if c != -1 or First:

            # Update the output when a key press has occured.
            stdscr.addstr('\n\n')
            stdscr.addstr('                   Instructions                 \n')
            stdscr.addstr('   ===========================================  \n')
            stdscr.addstr('        W      -  Increase Frequency            \n')
            stdscr.addstr('        A      -  Lag Audio Left                \n')
            stdscr.addstr('        D      -  Lag Audio Right               \n')
            stdscr.addstr('        S      -  Decrease Frequency            \n')
            stdscr.addstr('   [Space Bar] -  Play/Pause Pure Tone          \n')
            stdscr.addstr('        K      -  Kill Two Channel Generator    \n')
            stdscr.addstr('\n\n')
            stdscr.addstr('                 Current Settings               \n')
            stdscr.addstr('   ===========================================  \n')
            stdscr.addstr('     Frequency         :  {} Hz                 \n'.format(frequency))
            stdscr.addstr('     Left Channel Lag  :  {} Frames             \n'.format(lag_channel))
            stdscr.addstr('     Audio Out         :  {}                    \n'.format("Paused" if pause_sound else "Playing"))

            # return curser to start position
            stdscr.move(0, 0)
            stdscr.refresh()
            First = False

        # Do not play any Audio.
        if pause_sound:
            left_channel  = np.zeros(int(sampling_rate * duration)).astype(np.float32)
            right_channel = np.zeros(int(sampling_rate * duration)).astype(np.float32)
        
        # Generate identical pure tone for right and left channels.
        else:
            left_channel  = np.sin(2 * np.pi * np.arange(sampling_rate * duration) * frequency / sampling_rate).astype(np.float32)
            right_channel = np.sin(2 * np.pi * np.arange(sampling_rate * duration) * frequency / sampling_rate).astype(np.float32)

            # Lag the Left Channel +/-.
            left_channel = np.roll(left_channel, shift=lag_channel)

        # Reorder the audio samples to be L,R,L,R,... for pyaudio.
        samples = np.asarray(list(zip(left_channel, right_channel)), dtype=np.float32)

        # Play the tone.
        stream.write(samples.tobytes())


    # Clean up.
    stream.stop_stream()
    stream.close()
    p.terminate()
        

if __name__ == '__main__':
    curses.wrapper(main)