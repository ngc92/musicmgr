import taglib
import os
import logging
import hashlib

_log = logging.getLogger(__name__)


class TAGS:
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    TITLE = "TITLE"
    GENRE = "GENRE"
    DATE = "DATE"
    TRACKNUMBER = "TRACKNUMBER"


default_tags = {"ARTIST", "ALBUM", "TITLE", "GENRE", "DATE", "TRACKNUMBER"}


def ensure_unique(tag_value):
    assert isinstance(tag_value, list)
    assert len(tag_value) == 1
    return tag_value[0]


def get_tag(tags, tag, file):
    if tag in tags:
        return tags[tag]
    else:
        _log.warning("Missing tag %s in %s", tag, file)
        return None


def merge_tag(v1, v2):
    if v1 is None:
        return v2
    elif v2 is None:
        return v1
    elif v1 == v2:
        return v1
    assert False, (v1, v2)


def hash_file(file_name):
    return hashlib.sha256(open(file_name, 'rb').read()).digest()


class Song:
    def __init__(self, source):
        if isinstance(source, taglib.File):
            tags = source.tags
            self._artist = get_tag(tags, TAGS.ARTIST, source.path)
            self._album = ensure_unique(tags[TAGS.ALBUM])
            self._title = ensure_unique(tags[TAGS.TITLE])
            self._genre = get_tag(tags, TAGS.GENRE, source.path)
            self._date = get_tag(tags, TAGS.DATE, source.path)
            self._track = get_tag(tags, TAGS.TRACKNUMBER, source.path)
            self._duration = source.length
            self._file_path = source.path
        elif isinstance(source, dict):
            self._artist = source.get(TAGS.ARTIST, None)
            self._title = source.get(TAGS.TITLE, None)
            self._album = source.get(TAGS.ALBUM, None)
            self._genre = source.get(TAGS.GENRE, None)
            self._date = source.get(TAGS.DATE, None)
            self._track = source.get(TAGS.TRACKNUMBER, None)

            self._file_path = source.get("path", None)
            self._duration = source.get("duration", None)

    @property
    def file_path(self):
        return self._file_path

    @property
    def title(self) -> str:
        return self._title

    @property
    def album(self) -> str:
        return self._album

    @property
    def artist(self):
        return self._artist

    @property
    def genre(self):
        return self._genre

    @property
    def track(self):
        if self._track is None:
            return -1
        else:
            return self._track

    @property
    def date(self):
        return self._date

    @property
    def duration(self):
        return self._duration

    @property
    def directory(self):
        return os.path.split(self.file_path)[0]

    def get_tag(self, tag):
        if tag == TAGS.ARTIST:
            return self.artist
        elif tag == TAGS.DATE:
            return self.date
        elif tag == TAGS.GENRE:
            return self.genre
        elif tag == TAGS.ALBUM:
            return self.album
        elif tag == TAGS.TRACKNUMBER:
            return self._track
        elif tag == TAGS.TITLE:
            return self.title

    def __str__(self):
        if isinstance(self.artist, list) and len(self.artist) == 1:
            artist = self.artist[0]
        else:
            artist = self.artist
        return '<Song "%s" by %s>' % (self.title, artist)

    def __repr__(self):
        return self.__str__()

    def is_same_song(self, other):
        assert isinstance(other, Song)
        if self.title.lower() != other.title.lower():
            return False
        if self.artist != other.artist:
            return False
        if self.album is not None and other.album is not None and self.album.lower() != other.album.lower():
            return False

        return True

    def missing_tags(self):
        missing = []
        if self.title is None:
            missing.append(TAGS.TITLE)
        if self.album is None:
            missing.append(TAGS.ALBUM)
        if self.track == -1:
            missing.append(TAGS.TRACKNUMBER)
        if self.genre is None:
            missing.append(TAGS.GENRE)
        if self.artist is None:
            missing.append(TAGS.ARTIST)
        return missing

    def save_txt(self, file, tags, delim="\t"):
        if tags is None:
            tags = ("ARTIST", "ALBUM", "TITLE")

        def get_tag_value(t):
            if t is None:
                return ""
            if isinstance(t, list):
                if len(t) == 1:
                    return t[0]
                return ", ".join(t)
            else:
                return t

        data = [get_tag_value(self.get_tag(t)) for t in tags]
        line = delim.join(["%s"] * len(data)) + "\n"

        line = line % tuple(data)
        file.write(line)

    def merge(self, other: "Song"):
        self._artist = merge_tag(self._artist, other._artist)
        self._title = merge_tag(self._title, other._title)
        self._track = merge_tag(self._track, other._track)
        self._genre = merge_tag(self._genre, other._genre)
        self._album = merge_tag(self._album, other._album)
        self._date = merge_tag(self._date, other._date)

    def save_dict(self):
        save = {}
        for tag in default_tags:
            save[tag] = self.get_tag(tag)
        save["path"] = self.file_path
        return save
