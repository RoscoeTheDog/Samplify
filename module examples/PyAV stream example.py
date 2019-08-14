import av
import os

path_to_video = 'C:\\Users\\Admin\\Downloads\\video.mp4'
path_to_audio = 'C:\\Users\\Admin\\Downloads\\Dist Harmonic OS 01 D.wav'


container = av.open(path_to_video)

os.chdir('C:\\Users\\Admin\\Downloads\\')

for s in container.streams:
    print(s.type)  # print type of stream

    if s.type == 'video':  # print video stream info
        print(s)

    if s.type == 'audio':  # print audio stream info
        print(s.format.name)
        print(s.sample_rate)
        print(s.format.bits)
