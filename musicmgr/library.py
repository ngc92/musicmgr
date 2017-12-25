from .song import Song
from .album import Album
import os
import pickle
import logging

_logger = logging.getLogger(__name__)


class Library:
    def __init__(self, path):
        self._path = path
        self._albums = {}
        self._songs = []

    def add_album(self, album: Album):
        if album.title in self._albums:
            _logger.error("Trying to add album %s that was already present. Source folders are %s and %s",
                          album.title, album.directory, self.get_album(album.title).directory)

        self._albums[album.title] = album
        for song in album.songs:
            self.add_song(song)

    def get_album(self, title) -> Album:
        return self._albums[title]

    def add_song(self, song: Song):
        if song.album not in self._albums:
            new_album = Album(song.album, song.artist, song.directory)
            self.add_album(new_album)

        album = self.get_album(song.album)
        if song not in album:
            album.add_song(song)
        self._songs.append(song)

    @property
    def albums(self):
        return self._albums.values()

    @property
    def songs(self):
        return tuple(self._songs)

    def merge(self, lib: "Library"):
        for alb in lib.albums:
            self.add_album(alb)

    def __str__(self):
        return "<Library at '%s'>" % self._path

    def save_txt(self, file, tags, delim="\t"):
        albs = sorted(self.albums, key=lambda x: x.artist)
        for alb in albs:
            alb.save_txt(file, tags, delim)

    def save(self):
        base_path = os.path.join(self._path, ".musicmgr")
        os.makedirs(base_path, exist_ok=True)
        for alb in self.albums:  # type: Album
            sd = alb.save_dict()
            target_file = os.path.join(base_path, alb.title)
            pickle.dump(sd, open(target_file, "wb"))


#def check_for_missing_tags(lib: Library):
#    for s in lib.songs:
