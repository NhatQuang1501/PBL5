import pygame
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment

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

        # Export the combined audio to a file named 'output.mp3'
        output_path = 'output.mp3'
        combined_audio.export(output_path, format='mp3')
        print("Generated speech successfully saved to output.mp3")

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")

# Call the function with your text inputs
if __name__ == "__main__":
    texts = ["Đang xử lý yêu cầu", "Xin chờ trong giây lát."]
    text_to_speech_func(texts)
