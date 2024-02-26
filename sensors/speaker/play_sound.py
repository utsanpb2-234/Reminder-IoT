import pygame
import time


pygame.init()

sample_file = "audio_file.wav"
my_sound = pygame.mixer.Sound(sample_file)

my_sound.play()

time.sleep(my_sound.get_length())

pygame.quit()