import pyaudio
import wave
import threading
import os

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 30  

recording = False

def record_audio():
    global recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    print("Recording...")
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    save_audio(frames)

def save_audio(frames):
    audio = pyaudio.PyAudio()
    wave_file = wave.open("recorded_audio.wav", 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    audio.terminate()

def start_recording():
    global recording
    recording = True
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

def stop_recording():
    global recording
    recording = False

def main():
    print("Press to end.")
    start_recording()
    while True:
        key_input = input()
        if key_input == '4':
            stop_recording()
            break

if __name__ == "__main__":
    main()
