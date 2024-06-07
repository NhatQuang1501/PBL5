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
from google.cloud import storage
from firebase_admin import credentials, db, initialize_app

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

    non_speech_signal = signal[start_index * hop_size:end_index * hop_size]
    output_path = os.path.join("D:\\", "web_HMM", "web", "webai", "ai", "record_sentence", "audio_trimmed1.wav")
    sf.write(output_path, non_speech_signal, sample_rate)

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
    # Read input audio file
    signal, sample_rate = sf.read(input_file)

    # Calculate Short-Time Energy
    squared_signal = np.square(signal)
    num_frames = 1 + int(np.ceil(len(signal) / hop_size))
    ste = np.zeros(num_frames)
    for i in range(num_frames):
        start = i * hop_size
        end = min(len(signal), start + frame_size)
        frame_squared = squared_signal[start:end]
        ste[i] = np.sum(frame_squared)

    # Detect speech segments
    is_speech = ste > threshold * np.max(ste)
    result = find_true_subarrays(is_speech)

    # Adjust speech segments
    speech_segments = []
    i = 0
    pre_end = pre_start = 0
    for start, end in result:
        if i == 0 and start > 0 and start - 1 < 50:
            start = 0
        elif i > 0 and start - pre_end + 1 < 50:
            start = pre_start
            speech_segments.pop(-1)
        speech_segments.append((start, end))
        i += 1
        pre_end = end
        pre_start = start

    # Extend speech segments frames
    speech_segments = [(max(start - 20, 0), min(end + 20, len(is_speech) - 2)) for start, end in speech_segments]

    # Load models for the initial command prediction
    model_path = 'D:/web_HMM/web/webai/ai/model_train/modelLabel3_giamstate.pkl'
    trained_models = load_models(model_path)
    
    # Predict the command type using the first segment
    start = speech_segments[0][0]
    end = speech_segments[0][1]
    speech_signal = signal[start * hop_size:end * hop_size]
    temp_filename = "D:/web_HMM/web/webai/ai/record_sentence/audio_temp.wav"
    sf.write(temp_filename, speech_signal, sample_rate)
    predicted_class = classify_audio_file(temp_filename, trained_models)
    commandType = {'Thêm': 1, 'Huỷ': 2}.get(predicted_class, 0)
    
    # Adjust segments based on the command type
    if commandType == 1 and len(speech_segments) == 4:
        speech_segments[2] = (speech_segments[2][0], speech_segments[3][1])
        speech_segments.pop()
    elif commandType == 2 and len(speech_segments) == 3:
        speech_segments[1] = (speech_segments[1][0], speech_segments[2][1])
        speech_segments.pop()
    elif predicted_class == 'Xác nhận' or predicted_class == 'Chưa':
        return predicted_class, True
    # Predict using the remaining segments
    predicted_classes = [predicted_class]  # Include the first prediction
    for i, (start, end) in enumerate(speech_segments[1:], start=1):  # Skip the first already processed
        if commandType == 1:
            if i == 1:
                model_path = 'D:/web_HMM/web/webai/ai/model_train/modelLabel1_giamstate.pkl'
            elif i >= 2:
                model_path = 'D:/web_HMM/web/webai/ai/model_train/modelLabel2_giamstate.pkl'
        elif commandType == 2:
            if i >= 1:
                model_path = 'D:/web_HMM/web/webai/ai/model_train/modelLabel2_giamstate.pkl'
        
        trained_models = load_models(model_path)
        speech_signal = signal[start * hop_size:end * hop_size]
        temp_filename = "D:/web_HMM/web/webai/ai/record_sentence/audio_temp.wav"
        sf.write(temp_filename, speech_signal, sample_rate)
        predicted_class = classify_audio_file(temp_filename, trained_models)
        predicted_classes.append(predicted_class)

    valid_sentences = load_valid_sentences('D:/web_HMM/web/webai/ai/Sentence.txt')
    # Concatenate all the predictions
    final_prediction = ' '.join(predicted_classes)
        
    if not final_prediction.strip():
        return final_prediction, False

    # if final_prediction not in valid_sentences:
    #     print(f"Câu lệnh không hợp lệ: {final_prediction}")
    #     return final_prediction, False

    
    print(f"Câu lệnh: {final_prediction}")
    return final_prediction, True

def load_valid_sentences(file_path):
    if not os.path.isfile(file_path):
        print(f"File {file_path} không tồn tại.")
        return []

    with open(file_path, 'r', encoding='utf-8') as file:
        valid_sentences = file.read().splitlines()
    
    return valid_sentences

def get_mfcc(file_path):
    y, sr = librosa.load(file_path)
    hop_length = math.floor(sr * 0.010)
    win_length = math.floor(sr * 0.025)

    # Tính toán MFCC, delta và delta-delta
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=1024, hop_length=hop_length, win_length=win_length)
    mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1, 1))
    delta1 = librosa.feature.delta(mfcc, order=1)
    delta2 = librosa.feature.delta(mfcc, order=2)
    X = np.concatenate([mfcc, delta1, delta2], axis=0)

    return X.T

def download_audio_from_storage(bucket_name, blob_name, local_filename, service_account_json):
    storage_client = storage.Client.from_service_account_json(service_account_json)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.download_to_filename(local_filename)
    print(f"Downloaded audio file from {bucket_name}/{blob_name} to {local_filename}")

    return local_filename

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
    
    # Tạofile âm thanh
    audio_filename = f"/ai/record_sentence/audio.wav"
    
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
    os.makedirs(os.path.dirname(audio_filename), exist_ok=True)
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Ghi âm thành công!")
    
    return audio_filename

def get_latest_audio_file_name(bucket_name):
    # Initialize Google Cloud Storage client with authentication
    storage_client = storage.Client()

    # List blobs in the specified bucket
    blobs = storage_client.list_blobs(bucket_name)

    latest_file_name = None
    latest_file_number = -1

    # Iterate through blobs to find the latest audio file based on the number in the filename
    for blob in blobs:
        if blob.name.endswith('.wav') and blob.name.startswith('audio'):
            # Extract the number from the file name (e.g., audio17.wav -> 17)
            file_number = int(blob.name.split('audio')[1].split('.wav')[0])

            # Check if this file number is greater than the current latest file number
            if file_number > latest_file_number:
                latest_file_number = file_number
                latest_file_name = blob.name

    return latest_file_name

if __name__ == "__main__":

    credential_path = "D:\\PBL5\\pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

    cred = credentials.Certificate(credential_path)
    initialize_app(cred, {
        'databaseURL': 'https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

    # Predict the class of the latest audio file in the bucket
    BUCKET_NAME = 'pbl5-nhom7.appspot.com'
    latest_file_name = get_latest_audio_file_name(BUCKET_NAME)

    reduceNoise(latest_file_name, latest_file_name)
    STE_cutter_from_file(latest_file_name)
    STE_cutter("D:/web_HMM/web/webai/audio_trimmed1.wav")

    