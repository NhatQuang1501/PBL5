from celery import shared_task
from .predict import predict, get_latest_audio_file_name
from firebase_admin import db

@shared_task
def process_audio_prediction():
    # Get the latest audio file name
    bucket_name = 'pbl5-nhom7.appspot.com'
    audio_file_name = get_latest_audio_file_name(bucket_name)

    # Perform prediction
    model_path = 'D://HMM_MODEL//models_train//model123.pkl'
    service_account_json = 'D:\\PBL5\\pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json'
    predicted_class, success = predict(audio_file_name, model_path, bucket_name, audio_file_name, service_account_json)

    if success:
        # Push the result to Firebase Realtime Database
        audio_id = int(audio_file_name.split('audio')[1].split('.wav')[0])
        ref = db.reference('audio_result')
        audio_data = {
            'audioId': audio_id,
            'result': str(predicted_class)  # Convert predicted class to string if needed
        }
        ref.child(f'audio_detail-{audio_data["audioId"]}').set(audio_data)
        print("Result pushed to Firebase database.")
    else:
        print("Failed to predict class for the latest audio file.")
