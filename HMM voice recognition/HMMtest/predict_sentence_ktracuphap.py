import os
import datetime
import pyaudio
import wave
import math
import numpy as np
import librosa
import hmmlearn.hmm as hmm
import pickle
from pydub import AudioSegment

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

    bonus = 25
    start_index = np.argmax(is_speech)
    start_index = max(0, start_index - bonus)
    end_index = len(is_speech) - np.argmax(is_speech[::-1]) - 1
    end_index = min(is_speech.size, end_index + bonus)
    # print(f"STE: {start_index * hop_size} - {end_index * hop_size}")

    non_speech_signal = signal[start_index * hop_size:end_index * hop_size]
    sf.write("record_sentence/audio_trimmed.wav", non_speech_signal, sample_rate)

def isCommand(str):
    f = open("Sentence.txt", "r", encoding='utf8')
    sentences = f.read().split('\n')
    for sentence in sentences:
        tmp = sentence.replace(',', ' ')
        # print(sentence)
        tmp = tmp + ' '
        if tmp == str:
            return True
    return False

def find_true_subarrays(arr):
    false_subarrays = []
    start_index = None

    for i in range(len(arr)):
        if arr[i] == True:
            if start_index is None:
                start_index = i
        elif start_index is not None:
            false_subarrays.append((start_index, i - 1))
            start_index = None

    if start_index is not None:
        false_subarrays.append((start_index, len(arr) - 1))

    return false_subarrays

def STE_cutter(input_file, frame_size=256, hop_size=128, threshold=0.05):
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
    result = find_true_subarrays(is_speech)
    # print(result)

    speechs_segment = []
    i = 0
    for start, end in result:
        if i == 0:
            if start > 0:
                if start - 1 < 40:
                    start = 0
        else:
            if start - pre_end + 1 < 40:
                start = pre_start
                speechs_segment.pop(-1)
        speechs_segment.append((start, end))
        i += 1
        pre_end = end
        pre_start = start
    
    for i in range(len(speechs_segment)):
        start, end = speechs_segment[i]
        speechs_segment[i] = (max(start - 20, 0), min(end + 20, len(is_speech) - 2))

    
    print(speechs_segment)

    # output_signal = np.array([])

    model_path = 'model_train/modelLabel3.pkl'
    trained_models = load_models(model_path)
    # print(speechs_segment[0][0])
    start = speechs_segment[0][0]
    end = speechs_segment[0][1]

    speech_signal = signal[start * hop_size:end * hop_size]
    sf.write("record_sentence/audio_temp.wav", speech_signal, sample_rate)
    predicted_class = classify_audio_file("record_sentence/audio_temp.wav", trained_models)

    commandType = 0
    print(predicted_class)
    if predicted_class == 'Thêm':
        print(1)
        commandType = 1
        if len(speechs_segment) == 4:
            speechs_segment[2] = (speechs_segment[2][0],speechs_segment[3][1])
            speechs_segment.pop()
    elif predicted_class == 'Huỷ':
        print(2)
        commandType = 2
        if len(speechs_segment) == 3:
            speechs_segment[1] = (speechs_segment[1][0],speechs_segment[2][1])
            speechs_segment.pop()
    elif predicted_class == 'Xác nhận' or predicted_class == 'Chưa':
        return

    print(speechs_segment)
    ret = ''

    cnt = 1
    for start, end in speechs_segment:
        # output_signal = np.concatenate((output_signal, signal[start * hop_size: (end + 1) * hop_size]))
        if commandType == 1:
            if cnt == 1:
                model_path = 'model_train/modelLabel3.pkl'
            elif cnt == 2:
                model_path = 'model_train/modelLabel1.pkl'
            else:
                model_path = 'model_train/modelLabel2.pkl'
        else:
            if cnt == 1:
                model_path = 'model_train/modelLabel3.pkl'
            else:
                model_path = 'model_train/modelLabel2.pkl'
        trained_models = load_models(model_path)
        speech_signal = signal[start * hop_size:end * hop_size]
        sf.write("record_sentence/audio_temp.wav", speech_signal, sample_rate)
        STE_cutter_from_file("record_sentence/audio.wav")
        predicted_class = classify_audio_file("record_sentence/audio_temp.wav", trained_models)
        # print(predicted_class, end=' ')
        ret += predicted_class + " "

        cnt += 1
    

    # print(ret)
    if isCommand(ret):
        print(ret)
    else:
        print("Câu lệnh không đúng cú pháp")

def get_mfcc(file_path):
    y, sr = librosa.load(file_path)
    hop_length = math.floor(sr * 0.010) # 10ms hop
    win_length = math.floor(sr * 0.025) # 25ms frame

    # Tính toán MFCC, delta và delta-delta
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=1024, hop_length=hop_length, win_length=win_length)
    mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1, 1)) # Chuẩn hóa MFCC
    delta1 = librosa.feature.delta(mfcc, order=1)
    delta2 = librosa.feature.delta(mfcc, order=2)
    X = np.concatenate([mfcc, delta1, delta2], axis=0) # Kết hợp các đặc trưng

    return X.T

def load_models(model_path):
    with open(model_path, 'rb') as file:
        models = pickle.load(file)

    return models

def classify_audio_file(audio_file, models):
    mfcc_features = get_mfcc(audio_file)

    # Phân loại dữ liệu âm thanh
    scores = {cname: model.score(mfcc_features) for cname, model in models.items()}
    predicted_class = max(scores, key=scores.get)

    return predicted_class

def record_audio():
    CHUNK = 96000
    FORMAT = pyaudio.paInt32
    CHANNELS = 1
    RATE = 48000
    RECORD_SECONDS = 5
    
    # Tạo tên file âm thanh dựa trên thời gian hiện tại
    audio_filename = f"record_sentence/audio.wav"
    
    audio = pyaudio.PyAudio()

    # Bắt đầu ghi âm
    stream = audio.open(format=FORMAT, 
                        channels=CHANNELS,
                        rate=RATE, 
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Đang ghi âm...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Hoàn thành ghi âm.")

    # Dừng và lưu ghi âm vào file WAV
    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Ghi âm thành công!")
    
    return audio_filename

if __name__ == "__main__":

    audio_file = record_audio()

    reduceNoise(audio_file, audio_file)
    STE_cutter_from_file(audio_file)
    STE_cutter("record_sentence/audio_trimmed.wav")
