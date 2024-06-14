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
dataset_path = 'DATASET_CHINHTHUC'
# Đường dẫn tới thư mục dataset_phanloai
output_path = 'DATASET_phanloai'

import re
def get_number_in_parentheses(text):
  match = re.search(r"\d+ \((\d+)\)", text)
  if match:
    return int(match.group(1))
  else:
    return None


for root, dirs, files in os.walk(dataset_path):
    for directory in dirs:
        source_dir = os.path.join(root, directory)
        # Lấy danh sách tất cả các file trong thư mục hiện tại
        # file_list = os.listdir(source_dir)
        # total_files = len(file_list)
        
        print(f"root: {root}, dirs: {dirs}, files: {files}, directory: {directory}")

        for sub_dir in os.listdir(source_dir):
            for wavfile in os.listdir(os.path.join(source_dir, sub_dir)):
                # print(wavfile)
                filename, ext = os.path.splitext(wavfile)
                # print(f"{filename}")
                try:
                    # order = int(filename.split(' ')[-1].split('(')[0])
                    order = get_number_in_parentheses(filename)
                    # print(order)
                except ValueError as e:
                    print(f"Lỗi: {e}")
                    print(f"Bỏ qua file {wavfile} do định dạng tên file không hợp lệ.")
                    continue
                # print(order)

                if order % 10 == 6 or order == 75:
                    target_dir = os.path.join(output_path, "test", sub_dir)
                    os.makedirs(target_dir, exist_ok=True)
                    target_dir = os.path.join(target_dir, wavfile)
                    path_file = os.path.join(source_dir, sub_dir, wavfile)
                    print(path_file)
                    print(target_dir)
                    reduceNoise(path_file, target_dir)
                    STE_cutter_from_file(target_dir)
                
                    


        # for wavfile in os.listdir(source_dir):
        #     # print(wavfile)
        #     filepath = os.path.join(source_dir, wavfile)
        #     # source_file_output = os.path.join(output_path, directory, lablefolder, wavfile)
        #     reduceNoise(filepath, filepath)
        #     STE_cutter_from_file(filepath)
        #     # print(f"{filepath} -->" )
        #     # break
        # # break
        
        break
    break

print("Done!")