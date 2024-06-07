from playsound import playsound
from pydub import AudioSegment

def play_audio_from_file(audio_file):
    try:
        # Đọc tệp âm thanh từ đường dẫn cục bộ
        audio_segment = AudioSegment.from_file(audio_file)
        
        # Phát âm thanh
        playsound(audio_file)
    except Exception as e:
        print(f"Đã xảy ra lỗi khi phát tệp {audio_file}: {e}")

def play_multiple_audio_files(audio_files):
    for audio_file in audio_files:
        play_audio_from_file(audio_file)

if __name__ == "__main__":
    # Thay đổi đường dẫn tệp âm thanh cục bộ ở đây
    audio_files = [
        "Welcome.mp3",
        "xinmoichonmoi.mp3"
    ]
    play_multiple_audio_files(audio_files)
