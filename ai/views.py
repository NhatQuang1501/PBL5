from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.cloud import storage
import os
import random
import string
import io
import numpy as np
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import pygame
import time
import threading
import requests
from firebase_admin import credentials, initialize_app, db
from .predict import STE_cutter, reduceNoise, STE_cutter_from_file
from .predict import get_latest_audio_file_name
from .text_to_speech import text_to_speech_func as text_to_speech
import firebase_admin

# Set environment variable to avoid a known issue with OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Initialize Firebase Admin SDK
credential_path = "D:\\PBL5\\pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate(credential_path)
if not firebase_admin._apps:
    initialize_app(cred, {
        'databaseURL': 'https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def say_hello(request):
    return render(request, 'hello.html')

def trangchu(request):
    return render(request, 'index.html')

def download_file_from_firebase(file_path):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        local_filename = file_path.split('/')[-1]
        blob.download_to_filename(local_filename)
        print("Downloaded file from Firebase Storage.")
        return local_filename
    except Exception as e:
        print(f"Error downloading file from Firebase: {e}")
        return None

def generate_new_table_id(table_name):
    ref = db.reference('data_temp')
    data = ref.get(shallow=True)

    if data is None:
        print("No data found at 'data_temp'. Initializing new table with ID 0.")
        return "0"

    max_id = -1
    for key in data.keys():
        if key.isdigit():
            table_id = int(key)
            if table_id > max_id:
                max_id = table_id

    new_table_id = str(max_id + 1)
    return new_table_id

def update_data_temp_with_predictions(predictions):
    latest_table_id = generate_new_table_id('data_temp')

    if not latest_table_id:
        print("Could not find the latest ID in data_temp.")
        return False

    new_entry = {'menu': {}}

    for prediction in predictions:
        add, dish = prediction.split(maxsplit=1)
        if add.lower() == "thêm":
            # Tách từng phần của tên món
            parts = dish.split()
            if len(parts) >= 2:
                # Lấy số từ phần đầu tiên của tên món nếu có thể chuyển đổi
                try:
                    quantity = int(parts[0])
                    # Xóa phần số ra khỏi tên món
                    dish = ' '.join(parts[1:])
                    # Thêm món vào menu với số lượng đã chuyển đổi
                    new_entry['menu'].setdefault(dish, 0)
                    new_entry['menu'][dish] += quantity
                except ValueError:
                    # Nếu không thể chuyển đổi số, thêm món với số lượng mặc định là 1
                    new_entry['menu'].setdefault(dish, 0)
                    new_entry['menu'][dish] += 1
            else:
                # Nếu không có số ở đầu, thêm món với số lượng mặc định là 1
                new_entry['menu'].setdefault(dish, 0)
                new_entry['menu'][dish] += 1

    ref = db.reference(f'data_temp/{latest_table_id}')
    ref.set(new_entry)
    print(f"Updated data_temp/{latest_table_id} with predictions: {new_entry}")
    return True

def text_to_speech_func(texts):
    try:
        combined_audio = AudioSegment.silent(duration=0)

        for text in texts:
            tts = gTTS(text=text, lang='vi')
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            audio_segment = AudioSegment.from_file(mp3_fp, format='mp3')
            combined_audio += audio_segment

        existing_files_count = 0

        while True:
            output_filename = f"outputre_{existing_files_count}.mp3"
            if not os.path.exists(output_filename):
                break
            existing_files_count += 1
        
        combined_audio.export(output_filename, format='mp3')
        print(f"Generated speech successfully saved to {output_filename}")

        pygame.mixer.init()
        pygame.mixer.music.load(output_filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")

def save_order_to_table(table_id, order):
    try:
        ref = db.reference(f'data_temp/Ban{table_id}')
        ref.push(order)
        print(f"Saved order to table Ban{table_id}: {order}")
        return True
    except Exception as e:
        print(f"Error saving order to table Ban{table_id}: {e}")
        return False
    

def read_menu_for_table(table_id):
    try:
        ref = db.reference(f'data_temp/Ban{table_id}')
        orders_snapshot = ref.get()
        orders = []

        if orders_snapshot:
            for key, value in orders_snapshot.items():
                orders.append(value)

        print(f"Menu for table Ban{table_id}: {orders}")
        return orders
    except Exception as e:
        print(f"Error reading menu for table Ban{table_id}: {e}")
        return None

def get_latest_table_id():
    ref = db.reference('data_temp')
    data = ref.get(shallow=True)
    
    if not data:
        return None 

    latest_id = max(data.keys(), key=int)  
    return latest_id

def convert_text_numbers_to_numeric(text):
    numbers_map = {
        "Một": "1", "Hai": "2", "Ba": "3", "Bốn": "4",
        "Năm": "5", "Sáu": "6", "Bảy": "7", "Tám": "8",
        "Chín": "9", "Mười": "10"
    }
    for word, digit in numbers_map.items():
        text = text.replace(word, digit)
    return text

confirmation_requested = False

def update_latest_table_with_prediction(prediction):
    global confirmation_requested

    try:
        latest_table_id = get_latest_table_id()  # Ensure you get the latest table ID dynamically
        if not latest_table_id:
            return False

        menu_ref = db.reference(f'data_temp/{latest_table_id}/menu')
        current_menu = menu_ref.get() or {}

        if isinstance(current_menu, list):
            # Convert list to dict if needed
            current_menu = {str(i + 1): item for i, item in enumerate(current_menu)}

        next_item_id = str(max([int(key) for key in current_menu.keys()] + [0]) + 1) if current_menu else "1"

        if prediction.startswith("Huỷ "):
            parts = prediction.split()
            dish = ' '.join(parts[1:])
            item_name_to_cancel = ' '.join(dish.split()).lower()
            item_ids_to_remove = [item_id for item_id, item in current_menu.items() if item and item_name_to_cancel in item.lower()]
            for item_id in item_ids_to_remove:
                del current_menu[item_id]
            menu_ref.set(current_menu)
        elif prediction.startswith("Thêm "):
            parts = prediction.split()
            dish = ' '.join(parts[1:])
            dish_split = dish.split()
            quantity = convert_text_numbers_to_numeric(dish_split[0])
            dish_name = ' '.join(dish_split[1:]).lower()
            existing_item_id = None
            for item_id, item in current_menu.items():
                if item and dish_name in item.lower():
                    existing_item_id = item_id
                    break
            if existing_item_id:
                current_quantity = int(current_menu[existing_item_id].split()[0])
                updated_quantity = current_quantity + int(quantity)
                current_menu[existing_item_id] = f"{updated_quantity} {dish_name}"
            else:
                current_menu[next_item_id] = f"{quantity} {dish_name}"
        elif prediction == "Xác nhận":
            if any(current_menu.values()):
                if not confirmation_requested:
                    # Tạo menu_text chỉ với các món ăn không phải None
                    menu_text = ", ".join([f"{dish}" for index, dish in current_menu.items() if dish])
                    print(f"Menu for table {latest_table_id}: {menu_text}")
                    text_to_speech_func([f"Menu hiện tại bao gồm: {menu_text}"])
                    text_to_speech_func(["Quý khách có muốn xác nhận các món trên không ạ?"])
                    confirmation_requested = True
                else:
                    text_to_speech_func(["Đã xác nhận menu của quý khách. Xin cảm ơn."])
                    confirmation_requested = False  # Reset the confirmation state after final confirmation
            else:
                # Nếu không có món ăn, thông báo rằng menu trống
                print(f"Menu for table {latest_table_id} is empty.")
                text_to_speech_func(["Menu hiện tại đang trống."])
        elif prediction == "Chưa":
            if confirmation_requested:
                text_to_speech_func(["Quý khách vui lòng tiếp tục gọi món."])
                confirmation_requested = False  # Reset the confirmation state
        else:
            if confirmation_requested:
                text_to_speech_func(["Hãy nói 'Xác nhận' hoặc 'Chưa' để xác nhận menu."])
            else:
                text_to_speech_func(["Gọi món trên không hợp lệ. Vui lòng thử lại."])

        menu_ref.update(current_menu)
        print(f"Updated menu for table {latest_table_id} with prediction: {prediction}")
        return True
    except Exception as e:
        print(f"Error updating the latest table with prediction: {e}")
        return False

table_timers = {}

def database_listener(event):
    try:
        if event and isinstance(event.data, dict):
            data_dict = event.data
            if 'file_name' in data_dict and 'file_url' in data_dict:
                file_url = data_dict['file_url']
                text_to_speech_func(["Đang nhận diện giọng nói", "Xin quý khách chờ trong giây lát."])

                prediction, error = perform_prediction(file_url, from_url=True)
                if error:
                    text_to_speech_func(["Không thể nhận diện được món ăn. Vui lòng thử lại."])
                elif prediction and 'predicted_class' in prediction:
                    predicted_class = prediction['predicted_class']
                    if predicted_class == "Chưa":
                        text_to_speech_func([f"Chưa xác nhận."])
                    else:
                        text_to_speech_func([f"Đã {predicted_class}"])
                    update_latest_table_with_prediction(predicted_class)
                else:
                    text_to_speech_func(["Không có kết quả dự đoán."])
            else:
                print('Invalid event data: missing required keys.')
        else:
            print('Invalid event or event data format.')
    except Exception as e:
        print(f"Error in database listener: {e}")


# def read_menu_for_table_after_timeout(table_id):
#     print("Reading menu for table after timeout:                                            " + table_id)
#     global table_timers
    
#     try:
#         ref = db.reference(f'data_temp/{table_id}/menu')
#         menu_snapshot = ref.get()
#         print(menu_snapshot)
        
#         # Kiểm tra xem có dữ liệu menu không
#         if menu_snapshot is None:
#             print(f"Không tìm thấy menu cho bàn {table_id}")
#             return

#         # Khởi tạo danh sách rỗng cho các món ăn
#         dishes_texts = []

#         # Xử lý khi menu_snapshot là danh sách các strings
#         if isinstance(menu_snapshot, list):
#             for item in menu_snapshot:
#                 if isinstance(item, str) and item.startswith("Thêm "):
#                     dish = item.split("Thêm ", 1)[-1]  # Loại bỏ phần "Thêm " và lấy tên món ăn
#                     dishes_texts.append(dish)
#         else:
#             print(f"Kiểu dữ liệu của menu_snapshot không hợp lệ: {type(menu_snapshot)}")
#             return

#         menu_text = ", ".join(dishes_texts)
        
#         if dishes_texts:  # Nếu có danh sách món ăn để thông báo
#             print(f"Menu cho bàn {table_id} bao gồm: {menu_text}")
#             # Assuming `text_to_speech_func` là một hàm chuyển văn bản thành giọng nói
#             text_to_speech_func([f"Menu bạn đã gọi gồm có: {menu_text}"])
#             text_to_speech_func(["Quý khách có muốn xác nhận các món trên không ạ?"])
#         else:
#             print(f"Không có món ăn mới phù hợp tại bàn {table_id}")

#     except Exception as e:
#         print(f"Lỗi khi đọc menu cho bàn {table_id}: {e}")

    # finally:
    #     # Kiểm tra xem liệu có dữ liệu mới đã được cập nhật hay không
    #     if menu_snapshot is None or not menu_snapshot:
    #         # Nếu không có dữ liệu mới, thực hiện đọc lại
    #         if table_id in table_timers:
    #             timer = table_timers.pop(table_id)
    #             timer.cancel()
    #         timer = threading.Timer(10.0, read_menu_for_table_after_timeout, args=(table_id,))
    #         table_timers[table_id] = timer
    #         timer.start()
    #     else:
    #         # Nếu có dữ liệu mới, hủy bộ đếm
    #         if table_id in table_timers:
    #             timer = table_timers.pop(table_id)
    #             timer.cancel()


# Dictionary to track the status of each table
table_statuses = {}

def table_status_listener(event):
    try:
        print("Received event data:", event.data)
        
        if event.data is None or not isinstance(event.data, int):
            print(f"Unexpected event data format: {type(event.data)} {event.data}")
            return

        table_name = event.path.strip('/')

        # Get the previous status of the table, default to 0 if not found
        previous_status = table_statuses.get(table_name, 0)

        # Update the current status in the dictionary
        table_statuses[table_name] = event.data

        # Only create a new entry if the status changed from 0 to 1
        if event.data == 1 and previous_status != 1:
            print(f"Table '{table_name}' status changed to 1. Updating data_temp.")
            new_table_id = generate_new_table_id('data_temp')
            new_entry = ""
            ref = db.reference(f'data_temp/{new_table_id}')
            ref.set(new_entry)
            print(f"Created new entry in data_temp/{new_table_id}")

            text_to_speech_func([
                "Chào mừng quý khách đã đến với Light Restaurant",
                "Xin chúc quý khách ngon miệng",
                "Vui lòng gọi món bằng cách nói 'Thêm' hoặc 'Hủy' và tên món ăn"
            ])
        else:
            print(f"Table '{table_name}' status changed, but not to 1. Current status: {event.data}")

    except Exception as e:
        print(f"Error in table status listener: {str(e)}")


# Add listeners for table statuses
for table_number in range(1, 5):
    ref = db.reference(f'tables/Ban{table_number}/status')
    ref.listen(table_status_listener)

def perform_prediction(audio_file, from_url=False):
    try:
        if from_url:
            response = requests.get(audio_file, stream=True)
            if response.status_code != 200:
                return None, f"Failed to download file from URL. HTTP Status Code: {response.status_code}"
            
            # Load audio file from URL response
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            audio.export("temp_audio.wav", format="wav")
            full_audio_path = "temp_audio.wav"
        else:
            full_audio_path = audio_file
        
        # Check if the file exists
        if not os.path.exists(full_audio_path):
            return None, f"File {full_audio_path} does not exist."
        
        # Perform noise reduction and segmentation
        reduceNoise(full_audio_path, full_audio_path)
        STE_cutter_from_file(full_audio_path)
        
        # Perform the prediction on the processed audio file
        predicted_class, success = STE_cutter("D:/web_HMM/web/webai/ai/record_sentence/audio_trimmed1.wav")

        if success:
            audio_id = int(audio_file.split('audio')[1].split('.wav')[0])
            ref = db.reference('audio_results')
            audio_data = {
                'audioId': audio_id,
                'result': str(predicted_class)
            }
            ref.child(f'audio_detail-{audio_data["audioId"]}').set(audio_data)
            return {'predicted_class': predicted_class}, None
        else:
            return None, 'Prediction failed.'
    except Exception as e:
        return None, str(e)

# Listen for changes in the Firebase Realtime Database
ref = db.reference('/')
ref.listen(database_listener)

def update_data_temp_with_audio_prediction(request):
    if request.method == 'POST':
        audio_file_url = request.POST.get('audio_file_url')
        if not audio_file_url:
            return JsonResponse({'error': 'No audio_file_url provided.'}, status=400)

        predictions, error = perform_prediction(audio_file_url, from_url=True)
        if error:
            return JsonResponse({'error': error}, status=500)

        success = update_latest_table_with_prediction(predictions['predicted_class']) if predictions else False

        if success:
            return JsonResponse({'status': 'success', 'predictions': predictions}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to update Firebase.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
