import cv2
import pygame
import speech_recognition as sr
import pyttsx3
import threading

# pip install opencv-python pygame speechrecognition pyttsx3


# Function to play audio
def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Function to play video
def play_video(file_path):
    cap = cv2.VideoCapture(file_path)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Video', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

# Function for speech recognition
def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        print("Say something!")
        audio = recognizer.listen(source)
    try:
        response = recognizer.recognize_google(audio)
        print("You said: " + response)
        return response
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        print("Request Error.")
        return ""

# Function for text to speech
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Main function
def main():
    # Play the initial audio file
    audio_thread = threading.Thread(target=play_audio, args=(r"D:\Mr-Smith-AI-Resources\Mr Smith's Fan Fare Music CLEAN.mp3",))
    audio_thread.start()

    # Start the video playback
    video_thread = threading.Thread(target=play_video, args=(r"D:\Mr-Smith-AI-Resources\s2-enhanced.mp4",))
    video_thread.start()

    # Wait for the audio and video threads to start
    audio_thread.join()
    video_thread.join()

    # Engage in voice interaction
    while True:
        user_input = recognize_speech()
        if user_input.lower() == "exit":
            break
        response = "You said: " + user_input
        speak_text(response)

if __name__ == "__main__":
    main()
