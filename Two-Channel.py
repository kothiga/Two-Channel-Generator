import argparse
import numpy as np
import pyaudio
import wave

def save_wav(file_name, ch0, ch1, samp_rate):

    # Params for wav.
    num_channels = 2
    samp_width   = 2
    num_frames   = len(ch0)
    comptype     = "NONE"
    compname     = "not compressed"

    audio = np.asarray(list(zip(ch0, ch1)), dtype=np.float16)
    audio = np.reshape(audio, (num_channels * num_frames), order='C')
    audio = np.asarray(audio * 28672.0, dtype=np.int16)

    wave_file = wave.open(file_name, 'wb')
    wave_file.setparams((num_channels, samp_width, samp_rate, num_frames, comptype, compname))
    wave_file.writeframes(audio)
    wave_file.close()


# Grab some parameters from the user.
parser = argparse.ArgumentParser(description='Two-Channel Pure Tone (Sine) Generator')
parser.add_argument('--play',     default=False, action='store_true', help='Play the specified tone out of the speakers (default: {})'.format(False))
parser.add_argument('--filename', default=None,  help='Filename to save the specified tone as a wave file. If none is given, the tone will not be saved.')
parser.add_argument('--freq',     default=440.0, type=float,          help='Frequency of the tone to be generated (default: {})'.format(440.0))
parser.add_argument('--dur',      default=1.0,   type=float,          help='Duration (in seconds) that the pure tone should be generated. (default: {})'.format(1.0))
parser.add_argument('--lag',      default=0,     type=int,            help='Number of frames to lag the left channel by (default: {})'.format(0))
parser.add_argument('--samp',     default=48000, type=int,            help='Sampling rate (in Hz) for the pure tone. (default: {})'.format(48000))
args = parser.parse_args()

# Set these parameters.
play_tone      =  args.play
filename       =  args.filename
frequency      =  args.freq
duration       =  args.dur
lag_channel    =  args.lag
sampling_rate  =  args.samp

# Generate identical pure tone for right and left channels.
left_channel  = np.sin(2 * np.pi * np.arange(sampling_rate * duration) * frequency / sampling_rate).astype(np.float32)
right_channel = np.sin(2 * np.pi * np.arange(sampling_rate * duration) * frequency / sampling_rate).astype(np.float32)

# Lag the Left Channel +/-.
left_channel = np.roll(left_channel, shift=lag_channel)


# Play a tone through the default audio device.
if play_tone:
    
    # Reorder the audio samples to be L,R,L,R,... for pyaudio.
    samples = np.asarray(list(zip(left_channel, right_channel)), dtype=np.float32)

    # For paFloat32 sample values must be in range [-1.0, 1.0]
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=2,
        rate=sampling_rate,
        output=True
    )

    # Play the tone.
    stream.write(samples.tobytes())

    # Clean up.
    stream.stop_stream()
    stream.close()
    p.terminate()

# Save the pure tone to the provided file name.
if filename != None:

    # Make sure we have a wav file for a file name.
    assert (filename.find('.wav') != -1) or (filename == "default")

    if filename == "default":
        filename = "freq_{}_lag_{:02d}.wav".format(int(frequency), lag_channel)

    # Save the audio file.    
    save_wav(file_name=filename, ch0=left_channel, ch1=right_channel, samp_rate=sampling_rate)
