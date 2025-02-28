import streamlit as st
from config import SOUND_COOLDOWN

class SoundManager:
    def __init__(self, sound_files):
        # Instead of pre-loading sounds, store the list of sound file URLs/paths.
        self.sound_files = sound_files
        self.cooldown = SOUND_COOLDOWN  # Cooldown for sound playback
        # Create a placeholder to update with an audio widget when a sound needs to be played.
        self.audio_placeholder = st.empty()

    def play_sound(self, rect_index):
        # Retrieve the sound file corresponding to the rectangle index.
        sound_file = self.sound_files[rect_index]
        # Display the audio widget. This plays the sound in the user's browser.
        self.audio_placeholder.audio(sound_file, format="audio/mp3")
