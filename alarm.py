#!/usr/bin/env python
# -*- coding:utf-8 -*-

import multiprocessing, winsound
# from playsound import playsound
# import os.path

# sound = os.path.join('.', 'alarm.wav')
sound = 'alarm.wav'


class AlarmProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        self.m = winsound.PlaySound(sound, winsound.SND_FILENAME) #  winsound.SND_FILENAME | winsound.SND_LOOP
        # playsound(sound)
        self.run()
#       input()


if __name__ == "__main__":
    p = AlarmProcess()
    p.start()