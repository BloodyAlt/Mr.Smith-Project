# To install modules go to terminal at the bottom of the screen
# Then python --version
# Then pip --version

# Create virtual environment: python -m venv venv
# Activate virtual environment on Windows: .\venv\Scripts\activate
# Activate virtual environment on Linux/MacOS: source venv/bin/activate

# Once virtual environment activated download necessary packages:
# pip install SpeechRecognition pyaudio pyttsx3 pygame transformers torch opencv-python gtts

# Verifies installation of all packages installed 
# Import necessary modules
import os
import time
from datetime import datetime, timedelta
import pygame
import threading
import sys
import torch 
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import speech_recognition as sr
import pyttsx3
import cv2
import pygame.mixer
import time

# Initialize global variables
should_stop = threading.Event()  # Use threading.Event for better thread synchronization
video_thread = None
audio_thread = None
video_lock = threading.Lock()

# Initialize components
recognizer = sr.Recognizer()
model_name = "distilgpt2"  # Use distilgpt2 for offline functionality

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Directory for cache (where Hugging Face caches models by default)
cache_dir = os.path.join(base_dir, '.cache', 'huggingface', 'transformers')

def load_model():
    tokenizer_path = os.path.join(cache_dir, model_name, 'tokenizer_config.json')
    model_path = os.path.join(cache_dir, model_name, 'pytorch_model.bin')
    
    if os.path.exists(tokenizer_path) and os.path.exists(model_path):
        print("Loading model from cache.")
        tokenizer = GPT2Tokenizer.from_pretrained(model_name, local_files_only=True)
        model = GPT2LMHeadModel.from_pretrained(model_name, local_files_only=True)
    else:
        print("Model files not found in cache. Downloading the model...")
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Save the model to the cache directory
        tokenizer.save_pretrained(os.path.join(cache_dir, model_name))
        model.save_pretrained(os.path.join(cache_dir, model_name))
    
    return tokenizer, model

tokenizer, model = load_model()

# Path to the resources folder
resources_dir = os.path.join(base_dir, 'Mr-Smith-AI-Resources')

def play_audio(audio_file):
    """Play audio file."""
    audio_path = os.path.join(resources_dir, audio_file)
    
    # Initialize the mixer
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    
    # Set the volume
    pygame.mixer.music.set_volume(1.0)  # Volume range is from 0.0 to 1.0

    # Play the audio
    pygame.mixer.music.play()

    # Wait until the audio finishes playing or stop flag is set
    while pygame.mixer.music.get_busy() and not should_stop.is_set():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.stop()  # Ensure the audio stops if the flag is set

def listen():
    """Listen for and recognize speech commands."""
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            return None

def play_video(video_file):
    """Play video in fullscreen mode."""
    video_path = os.path.join(resources_dir, video_file)
    
    # Initialize pygame display
    pygame.display.init()
    
    # Get the primary monitor's resolution
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    
    # Set pygame display mode to fullscreen on the primary monitor
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    while not should_stop.is_set():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            continue
        
        # Resize the frame to match the screen resolution
        frame = cv2.resize(frame, (screen_width, screen_height))
        
        # Convert the frame to RGB (pygame uses RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create a pygame surface from the frame
        frame_surface = pygame.surfarray.make_surface(frame)
        
        # Blit the frame surface onto the screen
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                should_stop.set()  # Stop video on window close
                break
    
    cap.release()
    pygame.quit()

def generate_response(prompt):
    """Generate a response from the model with attention mask."""
    # Set padding token if not already set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Encode the prompt with padding and return tensors
    inputs = tokenizer.encode(prompt, return_tensors="pt", padding=True, truncation=True)
    
    # Create an attention mask where padding tokens are marked as 0
    attention_mask = torch.ones(inputs.shape, dtype=torch.long)
    
    # Generate a response from the model
    outputs = model.generate(
        inputs,
        attention_mask=attention_mask,
        max_length=150,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id
    )
    
    # Decode the response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def startup():
    """Start video and audio in separate threads."""
    global video_thread, audio_thread
    video_thread = threading.Thread(target=play_video, args=("s2-enhanced.mp4",))
    audio_thread = threading.Thread(target=play_audio, args=("Mr Smith's Fan Fare Music CLEAN.mp3",))
    
    video_thread.start()
    audio_thread.start()

def stop_program():
    """Stop all threads and clean up resources."""
    should_stop.set()  # Signal all threads to stop
    pygame.mixer.music.stop()  # Stop any audio playing
    
    # Wait for threads to finish
    if video_thread:
        video_thread.join()
    if audio_thread:
        audio_thread.join()
    
    pygame.quit()
    sys.exit()  # Exit the program

def stop_video():
    """Stop the currently playing video."""
    global should_stop, video_thread
    with video_lock:
        should_stop.set()  # Signal the video thread to stop
        if video_thread:
            video_thread.join()

def start_new_video(video_file):
    """Start a new video thread with the given video file."""
    global video_thread
    with video_lock:
        should_stop.clear()  # Clear the stop event
        video_thread = threading.Thread(target=play_video, args=(video_file,))
        video_thread.start()

def shutdown_computer():
    """Shutdown the computer based on the operating system."""
    if sys.platform == "win32":
        os.system("shutdown /s /t 10")
    elif sys.platform == "linux" or sys.platform == "darwin":
        os.system("shutdown now")

#def play_random_audio():
#    """Play a random audio file from a predefined list."""
#    audio_files = ["Temporal flux escalating in this vicinity.mp3", "My systems indicate an alien presence.mp3", "All systems are fully operational..mp3"] 
#    chosen_file = random.choice(audio_files)
#    play_audio(chosen_file)

#def random_audio_thread():
#    """Thread to play random audio files at intervals."""
#    while not should_stop.is_set():
#        play_random_audio()
#        time.sleep(20)  # Adjust the interval (in seconds) as needed

# Run startup function on startup
startup()

# Start the random audio thread
#random_audio_thread_instance = threading.Thread(target=random_audio_thread)
#random_audio_thread_instance.start()

def create_project_document(title, content):
    """Create a new text document with the given title and content."""
    # Define the directory for storing project files
    projects_dir = os.path.join(base_dir, 'Projects')
    
    # Ensure the directory exists
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    # Define the path for the new document
    file_path = os.path.join(projects_dir, f"{title}.txt")
    
    # Write content to the document
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Project document '{title}.txt' created successfully.")

# Main loop
while not should_stop.is_set():
    command = listen()
    if command:
        print(f"You said: {command}")
        if "goodbye mr smith" in command:
            stop_program()
        elif "commence deactivation" in command:
            play_audio("Goodbye Sir.mp4")
            shutdown_computer()
        elif "mr smith" in command:
            play_audio("How may I assist you today, sir.mp3")
            user_command = listen()
            if user_command:
                if "who is the doctor" in user_command:
                    play_audio("Who is the Doctor.mp3")  
                elif "start a new project" in user_command:
                    play_audio("Project title.mp3")
                    project_title = listen()
                    if project_title:
                        play_audio("What content would you like to add to the project.mp3")
                        project_content = listen()
                        if project_content:
                            create_project_document(project_title, project_content)
                            play_audio("Project created successfully.mp3")
                elif "who is sarah jane smith" in user_command:
                    play_audio("Who is Sarah Jane Smith.mp3") 
                elif "change your appearance" in user_command:
                    play_audio("Change Apperance.mp3")
                    stop_video()
                    start_new_video("s1-enhanced.mp4") 
                elif "initalize daybreak protocol" in user_command:
                    play_audio("Daybreak Protocol.mp3")
                #elif "" in user_command:
                #    response = generate_response(user_command)
                #elif "who is sarah jane smith": in user_command:
                #response = generate_response(user_command)
                else:
                    response = generate_response(user_command)
                    # Assuming you want to use a response audio file here as well
                    #play_audio("response_audio.mp3")  # Replace with a proper audio response file