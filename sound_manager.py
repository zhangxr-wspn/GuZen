import pygame
from config import SOUND_COOLDOWN


class SoundManager:
    def __init__(self, sound_files):
        # Load sounds from the list of sound files
        self.sounds = [pygame.mixer.Sound(file) for file in sound_files]
        self.cooldown = SOUND_COOLDOWN  # Cooldown for sound playback

    def play_sound(self, rect_index):
        # Play the sound corresponding to the rectangle index
        self.sounds[rect_index].play()
