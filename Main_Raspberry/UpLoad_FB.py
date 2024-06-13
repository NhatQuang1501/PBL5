import pyaudio
import wave
import firebase_admin
from firebase_admin import credentials, db
from google.cloud import storage
import os
import datetime
from gpiozero import Button

# Initialize Firebase
cred = credentials.Certificate("pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json")
credential_path = "pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
db_ref = db.reference()

storage_client = storage.Client()

def make_blob_public(bucket_name, blob_name):
    """Make a blob publicly accessible."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.make_public()
    print(f"Blob {blob_name} is publicly accessible at {blob.public_url}")

def record_and_upload():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000

    previous_record_count = len(db_ref.child('audio').get() or {})
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    FILENAME = f"audio{previous_record_count}.wav"

    audio = pyaudio.PyAudio()

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"Error opening audio stream: {e}")
        return

    print("Recording...")
    frames = []

    def stop_recording():
        print("Button pressed, stopping recording.")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        bucket_name = "pbl5-nhom7.appspot.com"
        blob_name = FILENAME
        blob = storage_client.bucket(bucket_name).blob(blob_name)
        blob.upload_from_filename(FILENAME)

        make_blob_public(bucket_name, blob_name)

        audio_url = blob.public_url

        new_audio_data = {
            'file_name': FILENAME,
            'file_url': audio_url
        }
        key = os.path.splitext(os.path.basename(FILENAME))[0]
        db_ref.child('audio').child(key).set(new_audio_data)

        print("Upload successful!")
        exit(0)

    button = Button(4)
    button.when_pressed = stop_recording

    try:
        while True:
            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except Exception as e:
                print(f"Error during recording: {e}")
                break
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    try:
        record_and_upload()
    except Exception as e:
        print(f"An error occurred: {e}")
