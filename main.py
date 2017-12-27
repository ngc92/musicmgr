import os, shutil

from musicmgr import scan, library
import logging
from appdirs import user_config_dir
import argparse
import configparser

logging.basicConfig(filename='errors.log', level=logging.DEBUG)

parser = argparse.ArgumentParser("musicmgr")
parser.add_argument('--merge', type=str, help="merge entries from another library")
parser.add_argument('--scan', action='store_true', help="scan library folder and add new songs")
parser.add_argument('--diff', type=str, help="find difference to other library")
parser.add_argument('--library', type=str, help="Set a library to use instead of the default library.")
parser.add_argument('--export', type=str, help="A path to where the library song files will be exported to.")
args = parser.parse_args()

config_dir = user_config_dir("muscimgr", "ngc92")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_file)
if not config.has_option(configparser.DEFAULTSECT, "path"):
    path = input("No path specified for music library. Please input a path.\n")
    if not os.path.exists(path):
        logging.error("Path %s does not exist", path)
        exit(1)
    config.set(configparser.DEFAULTSECT, "path", path)
    with open(config_file, "w") as tf:
        config.write(tf)

config = config[configparser.DEFAULTSECT]

lib = library.Library(config.get("path"))
lib_path = os.path.join(config_dir, "library.db")
if args.library is not None:
    lib_path = args.library

if os.path.exists(lib_path):
    lib.load(lib_path)

if args.merge is not None:
    other_lib = library.Library("")
    other_lib.load(args.merge)
    lib.merge(other_lib)
    lib.save(lib_path)

if args.scan:
    scanned = scan.scan_folder(lib.path, lib)
    lib.merge(scanned)
    lib.save(lib_path)

if args.diff:
    other_lib = library.Library("")
    other_lib.load(args.diff)
    diff = lib.difference(other_lib)
    diff.save("difference.db")

if args.export:
    os.makedirs(args.export)
    for song in lib.songs:
        source = song.file_path
        target = os.path.join(args.export, os.path.relpath(song.file_path, lib.path))
        print(target)
        target_dir = os.path.split(target)[0]
        os.makedirs(target_dir, exist_ok=True)
        shutil.copyfile(source, target)


with open("music.txt", "w") as file:
    lib.save_txt(file, ("ARTIST", "ALBUM", "TITLE", "GENRE", "DATE", "TRACKNUMBER"))

