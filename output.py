import pygame
import os
from pyvidplayer2 import Video

pygame.init()
pygame.mixer.init()

#Window size
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("BMO")

# Global variable to hold the currently playing video/audio object
current_media = None
is_audio_only = False


def play_media(mp_name):

    global current_media, is_audio_only

    #Stops anything playing
    if current_media:
        if is_audio_only:
            pygame.mixer.music.stop()
        else:
            current_media.close()

    #determining file path
    ext = os.path.splitext(mp_name)[1].lower()

    if ext in ['.mp4']:
        try:
            current_media = Video(mp_name)
            current_media.play()
            is_audio_only = False
            print(f"Playing video: {mp_name}")
        except Exception as e:
            print(f"Error loading video: {e}")
            current_media = None
##playing mp3 if mp3
    elif ext == '.mp3':
        try:
            pygame.mixer.music.load(mp_name)
            pygame.mixer.music.play()
            current_media = None
            is_audio_only = True
            print(f"Playing audio: {mp_name}")
        except pygame.error as e:
            print(f"Error loading audio: {e}")
            current_media = None

    else:
        print(f"Unsupported file type: {ext}")


##testing method
play_media("mp3/kissmephone.mp3")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clearing screen
    screen.fill((0, 0, 0))

    if current_media and not is_audio_only:
        current_media.draw(screen, (0, 0))

    elif is_audio_only:
        #font = pygame.font.Font(None, 74)
        #text = font.render("Playing MP3...", True, (255, 255, 255))
        #screen.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - text.get_height() / 2))

        # Check if audio finished playing (only necessary if looping is disabled)
        if not pygame.mixer.music.get_busy():
            print("MP3 finished.")
            is_audio_only = False

    pygame.display.update()

# Cleanup
if current_media:
    current_media.close()
pygame.mixer.quit()
pygame.quit()