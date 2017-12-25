from musicmgr import scan
import logging
import argparse

parser = argparse.ArgumentParser("musicmgr")

logging.basicConfig(filename='errors.log', level=logging.DEBUG)

lib = scan.scan_folder("/home/erik/Music/")
with open("music.txt", "w") as file:
    lib.save_txt(file, ("ARTIST", "ALBUM", "TITLE", "GENRE", "DATE", "TRACKNUMBER"))

lib.save()
