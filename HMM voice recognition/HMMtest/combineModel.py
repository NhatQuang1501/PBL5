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
import csv


# Chuyển label số thành chữ
# with open("D:/PBL5/PBL5_CODE/DemoHMM/model_train/model1.pkl", 'rb') as file:
# with open("D:/PBL5/PBL5_CODE/DemoHMM/model_train/model2.pkl", 'rb') as file:
with open("D:/PBL5/PBL5_CODE/DemoHMM/model_train/model3.pkl", 'rb') as file:
    models = pickle.load(file)

modelLabel = {}

with open("D:/PBL5/PBL5_CODE/DemoHMM/label_dataset/label.csv", 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    label = {}

    for i, row in enumerate(reader):
        # if i > 9:
        #     break
        # if i <= 9 or i >= 20:
        #     continue
        if i < 20:
            continue

        
        if row[0] == '':
            continue
        if i == 0 and row[0].startswith('\ufeff'):
            row[0] = row[0][1:]  # Loại bỏ ký tự BOM
        label[row[0]] = row[1]
    # print(label)

for key, value in label.items():
    modelLabel[value] = models[key]
    print(f"{key}: {value};   ")
print()

# with open('D:/PBL5/PBL5_CODE/DemoHMM/model_train/modelLabel1.pkl', 'wb') as file:
# with open('D:/PBL5/PBL5_CODE/DemoHMM/model_train/modelLabel2.pkl', 'wb') as file:
with open('D:/PBL5/PBL5_CODE/DemoHMM/model_train/modelLabel3.pkl', 'wb') as file:
        pickle.dump(modelLabel, file)
print("Saving label models done!")

def createSentence():
    with open('Sentence.txt', 'w' , encoding='utf-8') as file:
        for keyNum, valueNum in label.items():
            x = keyNum.split('.')[0]
            if x != '1':
                continue
            # if int(keyNum.split('.')[1]) > 5:
            #     continue
            for keyFood, valueFood in label.items():
                x = keyFood.split('.')[0]
                if x != '2':
                    continue
                # if int(keyFood.split('.')[1]) > 5:
                #     continue    

                file.write('Thêm,'+ valueNum + ',' + valueFood + '\n')
                # file.write(valueNum + ',' + valueFood + '\n')
            # file.write('Thêm,'+ valueNum + '\n')

                # file.write('Thêm,' + valueFood + '\n')
            # break

        for key, value in label.items():
            x = key.split('.')[0]
            if x != '2':
                continue
            # if int(key.split('.')[1]) > 5:
            #     continue
            file.write('Huỷ,' + value + '\n')
        file.write('Xác nhận' + '\n')
        file.write('Chưa' + '\n')

createSentence()