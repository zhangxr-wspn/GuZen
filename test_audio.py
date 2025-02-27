import pyaudio
import numpy as np
import matplotlib.pyplot as plt

RATE=22050
CHUNK = 2048

# Set up PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Set up plotting
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(np.random.rand(CHUNK))

print("Listening...")

try:
    while True:
        data = stream.read(CHUNK)
        signal = np.frombuffer(data, dtype=np.int16)
        fft_result = np.fft.fft(signal)
        magnitudes = np.abs(fft_result)

        # Visual feedback
        line.set_ydata(signal)
        plt.pause(0.01)

        # Trigger action if frequency magnitude exceeds threshold
        if max(magnitudes) > 10000:
            print("Trigger detected!")


finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
