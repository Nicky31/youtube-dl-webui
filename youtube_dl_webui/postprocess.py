#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import mutagen
import shutil
import os
from mutagen.easyid3 import EasyID3

import re
import itertools

logger = logging.getLogger("postprocess")

lvl_directory_pattern = "^[1-5] - "
max_lvl = 5


def get_level_directories():
    return [lvl for lvl in os.listdir(".") if re.match(lvl_directory_pattern, lvl)]


def get_genres_list():
    return list(
        set(
            itertools.chain(
                *[
                    [genre for genre in os.listdir(lvl) if genre[0] != "."]
                    for lvl in os.listdir(".")
                    if re.match(lvl_directory_pattern, lvl)
                ]
            )
        )
    )


def apply_id3tags(filepath, id3tags):
    try:
        meta = EasyID3(filepath)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(filepath, easy=True)
        meta.add_tags()
    for key, value in id3tags.items():
        try:
            meta[key] = value
        except:
            pass  # user tags cannot be written

    # Calculate score & assign
    rating = id3tags.get("lvl", "")[0:1]
    if rating:
        meta["rating"] = int(255 / max_lvl) * int(rating)

    meta.save(filepath, v1=2)
    logger.info("Succesfully tagged %s with %s", filepath, id3tags)


def move_track_to_genre_directory(filepath, id3tags):
    if not id3tags.get("lvl") or not id3tags.get("genre"):
        logger.info("Cannot move this track without lvl & genre id3tags !")
        return
    filename = os.path.basename(filepath)
    if id3tags.get("artist") and id3tags.get("title"):
        filename = "{artist} - {title}{ext}".format(
            **id3tags, ext=os.path.splitext(filename)[1]
        )
    target_directory = "{lvl}/{genre}".format(**id3tags)
    os.makedirs(target_directory, exist_ok=True)
    shutil.move(filepath, os.path.join(target_directory, filename))
    logger.info("Moved %s to %s", filename, target_directory)


# Additional ID3 keys
def rating_get(id3, key):
    return id3["POPM"].rating


def rating_set(id3, key, value):
    try:
        frame = id3["POPM"]
    except KeyError:
        id3.add(mutagen.id3.POPM(encoding=3, email="no@email", rating=value, count=0))
    else:
        frame.encoding = 3
        frame.rating = value
        frame.count = 0


def rating_delete(id3, key):
    del id3["POPM"]


EasyID3.RegisterKey("rating", rating_get, rating_set, rating_delete)


def comment_get(id3, key):
    return id3["COMM"].text


def comment_set(id3, key, value):
    try:
        frame = id3["COMM"]
    except KeyError:
        id3.add(mutagen.id3.COMM(encoding=3, text=value))
    else:
        frame.encoding = 3
        frame.text = value


def comment_delete(id3, key):
    del id3["COMM"]


EasyID3.RegisterKey("comment", comment_get, comment_set, comment_delete)
