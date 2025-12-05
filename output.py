import os
import os
import time
import json
import threading
import platform
import pygame
#from moviepy import VideoFileClip
from tts import tts

pygame.mixer.init()

WINDOW_W = 600
WINDOW_H = 800
current_request = None
current_frame = None
lock = threading.Lock()

# Detect if running on Raspberry Pi
IS_PI = platform.machine().startswith("arm")
print("Running on Pi:", IS_PI)

# Try VLC import only on Pi
if IS_PI:
    try:
        import vlc
        _vlc_instance = vlc.Instance()
        _vlc_player = _vlc_instance.media_player_new()
        VLC_AVAILABLE = True
    except ImportError:
        print("VLC not available, fallback to CV2")
        VLC_AVAILABLE = False
else:
    VLC_AVAILABLE = False
    import cv2

# Load JSON
with open('commands.json', 'r') as f:
    commandsJSON = json.load(f)

with open('music.json', 'r') as s:
    musicJSON = json.load(s)

with open('videos.json', 'r') as t:
    videosJSON = json.load(t)
with open('voice.json', 'r') as g:
    voiceJSON = json.load(g)

# Extract audio from MP4
def extract(mp4_path, output_dir="audio_cache"):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(mp4_path))[0]
    mp3_path = os.path.join(output_dir, f"{base_name}.mp3")
    clip = VideoFileClip(mp4_path)
    clip.audio.write_audiofile(mp3_path, logger=None)
    return mp3_path


# Play audio
def play_audio(mp_name):
    pygame.mixer.music.load(mp_name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.01)
        with lock:
            if current_request is not None:
                pygame.mixer.music.stop()
                break

# Play video
def play_vid(path):
    global current_frame, current_request
    if IS_PI and VLC_AVAILABLE:
        # VLC backend
        media = _vlc_instance.media_new(path)
        _vlc_player.set_media(media)
        _vlc_player.play()
        while True:
            time.sleep(0.1)
            state = _vlc_player.get_state()
            with lock:
                if current_request is not None:
                    _vlc_player.stop()
                    break
            if state in [vlc.State.Ended, vlc.State.Error]:
                break
    else:
        # CV2 backend
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_duration = 1.0 / fps

        while True:
            start = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (WINDOW_W, WINDOW_H))
            with lock:
                current_frame = frame.copy()
                if current_request is not None:
                    break
            elapsed = time.perf_counter() - start
            time.sleep(max(0, frame_duration - elapsed))
        cap.release()


# Media loop
def media_loop():
    global current_request
    idle_vid = "deadpool.mp4"
    while True:
        play_vid(idle_vid)
        req = current_request
        current_request = None
        if req is None:
            continue
        ext = os.path.splitext(req)[1].lower()
        if ext == ".mp4":
            mp3 = extract(req)
            t = threading.Thread(target=play_audio, args=(mp3,))
            t.start()
            play_vid(req)
            t.join()
        elif ext == ".mp3":
            play_audio(req)


# CodeKey

def codeKey(key):
    global current_request
    if key[0] == "m" and key[1] in musicJSON:
        with lock:
            current_request = musicJSON[key[1]]
    if key[0] == "v" and key[1] in videosJSON:
        with lock:
            current_request = videosJSON[key[1]]
    if key[0] == "c" and key[1] in voiceJSON:
        with lock:
           tts(voiceJSON[key[1]])


def start_media_loop():
    threading.Thread(target=media_loop, daemon=True).start()
