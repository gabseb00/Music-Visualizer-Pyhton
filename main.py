import tkinter as tk
import sys
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *


class WAV_File():
    def __init__(self, file):
        self.RIFF = file.read(4)                                            # 1 - 4
        self.file_size = WAV_File.byte_to_int(file.read(4))                 # 5 - 8
        self.WAVE = file.read(4)                                            # 9 - 12
        self.format_chunk_marker = file.read(4)                             # 13 - 16
        self.length_of_format_data = WAV_File.byte_to_int(file.read(4))     # 17 - 20
        self.type_of_format = WAV_File.byte_to_int(file.read(2))            # 21 - 22
        self.num_ch = WAV_File.byte_to_int(file.read(2))                    # 23 - 24
        self.sample_rate = WAV_File.byte_to_int(file.read(4))               # 25 - 28
        self.bytes = WAV_File.byte_to_int(file.read(4))                     # 29 - 32
        self.bits_per_sample_1 = WAV_File.byte_to_int(file.read(2))         # 33 - 34
        self.bits_per_sample_2 = WAV_File.byte_to_int(file.read(2))         # 35 - 36
        self.begining_of_data_chunk = file.read(4)                          # 37 - 40
        self.file_size_data = WAV_File.byte_to_int(file.read(4))            # 41 - 44
    def info(self):
        print(f'File size: {self.file_size + 8}')
        print(f'Format chunk marker: {self.format_chunk_marker}')
        print(f'Length of format data: {self.length_of_format_data}')
        print(f'Type of format: {self.type_of_format}')
        print(f'Number of channels: {self.num_ch}')
        print(f'Sample Rate: {self.sample_rate}')
        print(f'Bits per sample: {self.bits_per_sample_2}')
        print(f'File size data: {self.file_size_data}')

    @staticmethod
    def byte_to_int(bytes):
        return int.from_bytes(bytes, "little")

def scrollSign(e):
    return 1 if e.y > 0 else -1

def main(filename: str):
    if not filename.endswith(".wav"):
        return -1
    width, height = 1200, 1200
    top, bottom = 100, 1100

    SECONDS_DISPLAYED = 30



    try:
        f = open(filename, "rb")
    except FileNotFoundError:
        print("File does not exist")
        return -1
    wave = WAV_File(f)
    wave.info()
    channel_1 = np.zeros(shape=wave.file_size)
    channel_2 = np.zeros(shape=wave.file_size)


    i = 0
    while True:
        byte = f.read(2)
        if byte == b'':
            break
        first = WAV_File.byte_to_int(byte)
        channel_1[i] = first
        byte = f.read(2)
        second = WAV_File.byte_to_int(byte)
        channel_2[i] = second
        i += 1
    channel_1 = np.array(channel_1, dtype="i2")
    channel_2 = np.array(channel_2, dtype="i2")
    f.close()

    wv = np.zeros(len(channel_1), dtype=int)
    print(wave.bits_per_sample_1 - 1)
    normalized_channel_1 = channel_1 / (2 ** (wave.bits_per_sample_2 - 1))
    for idx, v in enumerate(normalized_channel_1):
        wv[idx] = height // 2 + v * (height // 2)
    print(wv)

    pygame.init()
    screen = pygame.display.set_mode((width ,height))
    pygame.display.set_caption("Demo")

    clock = pygame.time.Clock()

    done = False
    passed_time = 0
    curr_pos_in_song = 0
    curr_x_pos = 0
    music_playing = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0 and SECONDS_DISPLAYED == 5:
                    continue
                for _ in range(abs(event.y)):
                    SECONDS_DISPLAYED = SECONDS_DISPLAYED - scrollSign(event) * 5
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    music_playing = not music_playing
        
        screen.fill(pygame.Color("black"))
        middle = np.ones(width, dtype=int) * height // 2
        for idx, i in enumerate(middle):
            screen.set_at((idx, i), pygame.color.Color("white")) 
            screen.set_at((idx, wv[0:wave.sample_rate*SECONDS_DISPLAYED:wave.sample_rate*SECONDS_DISPLAYED//width][idx]), pygame.color.Color("red"))

        # The speed at which the cursor moves depends on the current number of seconds displayed
        if music_playing:
            curr_pos_in_song += 1/60
            curr_x_pos = np.floor(curr_pos_in_song)
        pygame.draw.line(screen, pygame.color.Color("yellow"), (curr_x_pos, 0), (curr_x_pos, height))
        pygame.display.flip()
        passed_time += clock.tick(60)
        
    
    
    
    
    return 0
if __name__ == "__main__":
    if len(sys.argv) == 1:
        exit(main(f'C:\\Users\\Gabriel\\Downloads\\Oldboy OST - 16. The Old Boy - Jo Yeong Wook.wav'))
    else:
        exit(main(sys.argv[1]))