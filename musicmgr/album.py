from .song import Song, TAGS
import os

_ALBUM_TAGS = [TAGS.ARTIST, TAGS.GENRE, TAGS.DATE]


class Album:
    def __init__(self, title, artist, directory=None):
        self._title = title
        if isinstance(artist, str):
            artist = [artist]
        self._artist = set(artist)
        self._directory = directory
        self._songs = []

    @property
    def title(self):
        return self._title

    @property
    def artist(self):
        return self._artist

    @property
    def directory(self):
        return self._directory

    @property
    def songs(self):
        return tuple(self._songs)

    def add_song(self, song: Song):
        assert isinstance(song, Song)
        assert song.album == self.title
        self._songs.append(song)
        self._songs.sort(key=lambda x: x.track)
        self._artist = set(self._artist) | set(song.artist)

    def set_tag(self, tag, value):
        album_tags = ("DATE", "GENRE")
        assert tag in album_tags
        for song in self._songs:
            song.set_tag(tag, value)

    def __contains__(self, item):
        if isinstance(item, Song):
            if item in self._songs:
                return True
            # TODO less strict check that is not object but data specific!
        return False

    def __str__(self):
        artist = list(self.artist)
        if len(artist) == 1:
            artist = artist[0]
        songs = ", ".join([s.title for s in self._songs])
        return '<Album "%s" by %s: %s>' % (self.title, artist, songs)

    def __repr__(self):
        artist = list(self.artist)
        if len(artist) == 1:
            artist = artist[0]
        return '<Album "%s" by %s>' % (self.title, artist)

    def save_txt(self, file, tags, delim="\t"):
        for song in self._songs:
            song.save_txt(file, tags, delim)

    def save_dict(self):
        save = {}
        songs = [s.save_dict() for s in self._songs]
        save["songs"] = songs
        save["title"] = self.title
        save["artist"] = self.artist
        save["directory"] = self.directory
        return save

    # validation
    def fill_missing_album_tags(self):
        present = set(_ALBUM_TAGS)
        for s in self.songs:  # type:Song
            present &= set(s.missing_tags())

        missing = set(_ALBUM_TAGS) - present
        potential_values = {t: [] for t in missing}
        for s in self.songs:  # type:Song
            for t in missing:
                v = s.get_tag(t)
                if v is not None:
                    potential_values[t].append(v)

        for p in potential_values:
            values = set(potential_values[p])
            if len(values) == 1:
                pass
