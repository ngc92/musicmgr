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

    @property
    def path(self):
        return self._path

    def merge(self, lib: "Library"):
        for alb in lib.albums:
            self.add_album(alb)

    def difference(self, lib: "Library"):
        """
        Find all songs present in `self` that are not in lib.
        """
        surplus = Library(self.path)
        for song in self._songs:
            # OK, now we need to identify songs
            same = False
            for other in lib._songs:
                if song.is_same_song(other):
                    same = True
                    break
            if same:
                continue
            surplus.add_song(song)
        return surplus

    def __str__(self):
        return "<Library at '%s'>" % self._path

    def save_txt(self, file, tags, delim="\t"):
        albs = sorted(self.albums, key=lambda x: x.artist)
        for alb in albs:
            alb.save_txt(file, tags, delim)

    def save(self, target_file):
        target_dir = os.path.split(target_file)[0]
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        library_db = []
        for alb in self.albums:  # type: Album
            library_db.append(alb.save_dict())
        pickle.dump(library_db, open(target_file, "wb"))

    def load(self, source_file):
        if not os.path.exists(source_file):
            _logger.warning("Could not find library database %s", source_file)

        data = pickle.load(open(source_file, "rb"))
        for album_data in data:
            album = Album(album_data["title"], album_data["artist"], directory=album_data["directory"])
            for s in album_data["songs"]:
                album.add_song(Song(s))
            self.add_album(album)

#def check_for_missing_tags(lib: Library):
#    for s in lib.songs:
