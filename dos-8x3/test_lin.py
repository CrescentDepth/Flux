from test_support import verbose, findfile, TestFailed
import linuxaudiodev
import os

def play_sound_file(path):
    fp = open(path, 'r')
    data = fp.read()
    fp.close()
    try:
        a = linuxaudiodev.open('w')
    except linuxaudiodev.error, msg:
        raise TestFailed, msg
    else:
        a.write(data)
        a.close()

def test():
    play_sound_file(findfile('audiotest.au'))

test()
