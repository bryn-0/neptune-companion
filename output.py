import sys
import os
import json
import cv2
import time
import pygame
import threading
import subprocess
from moviepy import VideoFileClip

WINDOW_W = 600
WINDOW_H = 800
pygame.mixer.init()

current_request = None
lock = threading.Lock()
current_frame = None


##OPENING AND LOADING JSON FILES
with open('commands.json', 'r') as f:
    commandsJSON = json.load(f)

with open('music.json', 'r') as s:
    musicJSON = json.load(s)

with open('videos.json', 'r') as t:
    videosJSON = json.load(t)

##EXTRACT MP3 FROM MP4, (ALLOWS US TO CHANGE/KEEP DISPLAY WITH DIF AUDIOS)
##ALSO FOUND THAT CV2 ONLY PLAYS VID AND NO AUDIO SO WE NEED THIS :(
def extract(mp4_path, output_dir="audio_cache"):

    os.makedirs(output_dir, exist_ok=True)

    # Create MP3 file path
    base_name = os.path.splitext(os.path.basename(mp4_path))[0]
    mp3_path = os.path.join(output_dir, f"{base_name}.mp3")

    # Extract audio
    clip = VideoFileClip(mp4_path)
    clip.audio.write_audiofile(mp3_path, logger=None)  # logger=None to suppress output

    return mp3_path

##PLAY AUDIO METHOD USING PYGAME
def play_audio(mp_name):
    pygame.mixer.music.load(mp_name)
    pygame.mixer.music.play()
    print("Playing MP3:", mp_name)
    while pygame.mixer.music.get_busy():
        time.sleep(0.01)
        with lock:
            if current_request is not None:
                pygame.mixer.music.stop()
                break

##PLAY VID METHOD USING CV2
def play_vid(path):
    global current_frame, current_request

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("Cannot open:", path)
        return

    # Getting FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30
    frame_duration = 1.0 / fps

    while True:
        start_time = time.perf_counter()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (WINDOW_W, WINDOW_H))

        with lock:
            current_frame = frame.copy()
            if current_request is not None:
                break

        # Adjusting for fps of vid
        elapsed = time.perf_counter() - start_time
        sleep_time = max(0, frame_duration - elapsed)
        time.sleep(sleep_time)

    cap.release()


##LOOPING IDLE VID, JUMPS INTO MP4/MP3 AND GOES BACK TO IDLE LOOP
def media_loop():
    global current_request
    idle_vid = "deadpool.mp4" ##IDLE LOOPED ANIMATION FOR NEPTUNE

    while True:

        play_vid(idle_vid)

        req = current_request
        current_request = None

        if req is None:
            continue

        ext = os.path.splitext(req)[1].lower()

        if ext == ".mp4":
            mp3 = extract(req)
            audio_thread = threading.Thread(target=play_audio, args=(mp3,))
            audio_thread.start()
            play_vid(req)
            audio_thread.join()

        elif ext == '.mp3':
            play_audio(req)
            #play_vid("dance.mp4") ##Dancing Neptune Animation

##CODEKEY RECOGNIZES IF MP3 or MP4 AND FINDS KEY -> COMMAND IN JSON,
## EXAMPLE: M9 -> MP3 -> goes to music.json -> finds key "9"
# -> gets value which is the mp4 file -> calls playmedia method

def codeKey(key):
    global current_request

    if key [0] == "m" :
        print("Read as MP3")
        if key[1] in musicJSON:
            print(musicJSON[key[1]])
            path = musicJSON[key[1]]
            with lock:
                current_request = path

    if key [0] == "v" :
        print("Read as Video")
        if key[1] in videosJSON:
            print(videosJSON[key[1]])
            path = videosJSON[key[1]]
            with lock:
                current_request = path


def start_media_loop():
    threading.Thread(target=media_loop, daemon=True).start()

