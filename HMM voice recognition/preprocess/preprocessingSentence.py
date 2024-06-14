import os
import random
import shutil
import numpy as np

import librosa
import librosa.display
from pydub import AudioSegment
import gc
import numpy as np
import matplotlib.pyplot as plt

import noisereduce as nr
import soundfile as sf

def reduceNoise(filepath, output_filepath):
    audio_data, sr = librosa.load(filepath, sr=None)
    reduced_noise = nr.reduce_noise(y=audio_data, sr=sr)
    sf.write(output_filepath, reduced_noise, sr)

def STE_cutter_from_file(input_file, frame_size=256, hop_size=128, threshold=0.05):
    signal, sample_rate = sf.read(input_file)

    squared_signal = np.square(signal)
    num_frames = 1 + int(np.ceil(len(signal) / hop_size))
    ste = np.zeros(num_frames)
    for i in range(num_frames):
        start = i * hop_size
        end = min(len(signal), start + frame_size)
        frame_squared = squared_signal[start:end]
        ste[i] = np.sum(frame_squared)

    is_speech = ste > threshold * np.max(ste)

    bonus = 50
    start_index = np.argmax(is_speech)
    start_index = max(0, start_index - bonus)
    end_index = len(is_speech) - np.argmax(is_speech[::-1]) - 1
    end_index = min(is_speech.size, end_index + bonus)
    # print(f"STE: {start_index * hop_size} - {end_index * hop_size}")

    non_speech_signal = signal[start_index * hop_size:end_index * hop_size]
    sf.write(input_file, non_speech_signal, sample_rate)

# Đường dẫn tới dataset gốc
dataset_path = 'TESTCAU'
# Đường dẫn tới thư mục dataset_phanloai
output_path = 'DATASET_sentences'


for wavfile in os.listdir(dataset_path):
    # print(wavfile)
    inputFile = os.path.join(dataset_path, wavfile)
    outputFile = os.path.join(output_path, wavfile)
    reduceNoise(inputFile, outputFile)
    STE_cutter_from_file(outputFile)

print("Done!")