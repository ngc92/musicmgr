import taglib
import os
import logging
from .song import Song
from .album import Album
from .library import Library


_logger = logging.getLogger(__name__)
_MUSIC_FILES = [".mp3", ".flac", ".m4a", ".wav", ".wma"]
_OTHER_FILES = [".ini", ".jpg", ".png"]


def scan_folder(directory):
    lib = Library(directory)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            sub = scan_folder(file_path)
            lib.merge(sub)
        else:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in _MUSIC_FILES:
                if ext.lower() not in _OTHER_FILES:
                    _logger.warning("Unknown file extension %s", file_path)
                continue
            try:
                song = Song(taglib.File(file_path))
                lib.add_song(song)
            except Exception as error:
                print(error)
    return lib
