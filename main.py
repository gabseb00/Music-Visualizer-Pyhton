import sys
import numpy as np
import pygame
from pygame.locals import *
import pyaudio
from threading import Thread


FRAME_RATE = 60

class WAV_File():
    def __init__(self, file):
        # Read HEADER
        self.readHeader(file)
        self.createChannels(file)
        self.current_sample = 0
        self.is_playing = False
        self.song_started = False
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate, output=True)

    def streamMusic(self):
        while self.current_sample != len(self.channel_1):
             if self.is_playing:
                self.stream.write(bytes(self.channel_1[self.current_sample: self.current_sample + self.sample_rate // FRAME_RATE]))
                self.current_sample += self.sample_rate // FRAME_RATE
    
    def startPlayingThread(self):
        t = Thread(target=self.streamMusic)
        t.start()


    def readHeader(self, file):
        file.seek(0)
        self.RIFF = file.read(4)                                            # 1 - 4
        self.file_size = WAV_File.byte_to_int(file.read(4))                 # 5 - 8
        self.WAVE = file.read(4)                                            # 9 - 12
        self.format_chunk_marker = file.read(4)                             # 13 - 16
        self.length_of_format_data = WAV_File.byte_to_int(file.read(4))     # 17 - 20
        self.type_of_format = WAV_File.byte_to_int(file.read(2))            # 21 - 22
        self.num_ch = WAV_File.byte_to_int(file.read(2))                    # 23 - 24
        self.sample_rate = WAV_File.byte_to_int(file.read(4))               # 25 - 28
        self.byte_rate = WAV_File.byte_to_int(file.read(4))                 # 29 - 32
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


    def createChannels(self, file) -> None:
        file.seek(44)
        self.channel_1 = bytearray()
        self.channel_2 = bytearray()
        data = file.read()
        for i in range(0, len(data), 4):
            self.channel_1 += data[i:i+2]
            self.channel_2 += data[i+2:i+4]

    def play(self):
        self.is_playing = True
        if not self.song_started:
            self.startPlayingThread()
            self.song_started = True

    
    def pause(self):
        self.is_playing = False


    # TODO currently assumes that every byte is its own int
    def getPixelPositions(self):
        wv = np.array(self.channel_1, dtype=np.int16)
        normalized_channel_1 = wv / (2 ** (self.bits_per_sample_2 - 1))
        return normalized_channel_1

    @staticmethod
    def byte_to_int(bytes, order="little"):
        return int.from_bytes(bytes, byteorder=order)

def scrollSign(e):
    return 1 if e.y > 0 else -1


def main(filename: str):
    if not filename.endswith(".wav"):
        return -1
    width, height = 1200, 1200

    SECONDS_DISPLAYED = 1
    try:
        f = open(filename, "rb")
    except FileNotFoundError:
        print("File does not exist")
        return -1
    wave = WAV_File(f)
    
    
    wv = wave.getPixelPositions()
    wv = (height // 2 + wv * 100).astype(int)
    print(wv)


    pygame.init()
    screen = pygame.display.set_mode((width ,height))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()
    done = False
    passed_time = 0
    curr_pos_in_song = 0
    curr_x_pos = 0
    is_playing = False    
    middle = np.ones(width, dtype=int) * height // 2
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0 and SECONDS_DISPLAYED == 1:
                    continue
                for _ in range(abs(event.y)):
                    SECONDS_DISPLAYED = SECONDS_DISPLAYED - scrollSign(event) * 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not is_playing:
                        is_playing = True
                        wave.play()
                    else:
                        is_playing = False
                        wave.pause()
        screen.fill(pygame.Color("black"))
        for idx, i in enumerate(middle):
            screen.set_at((idx, i), pygame.color.Color("white")) 
            screen.set_at((idx, wv[0: wave.sample_rate*SECONDS_DISPLAYED: wave.sample_rate*SECONDS_DISPLAYED//width][idx]), pygame.color.Color("red"))


        # The speed at which the cursor moves depends on the current number of seconds displayed
        if is_playing:
            curr_pos_in_song += width/SECONDS_DISPLAYED/FRAME_RATE
            curr_x_pos = np.floor(curr_pos_in_song)
        pygame.draw.line(screen, pygame.color.Color("yellow"), (curr_x_pos, 0), (curr_x_pos, height))
        pygame.display.flip()
        passed_time += clock.tick(FRAME_RATE)
        
    
    
    
    
    return 0
if __name__ == "__main__":
    if len(sys.argv) == 1:
        exit(main(f'C:\\Users\\Gabriel\\Downloads\\Oldboy OST - 16. The Old Boy - Jo Yeong Wook.wav'))
    else:
        exit(main(sys.argv[1]))