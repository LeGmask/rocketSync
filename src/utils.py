import unicodedata
import re


def getTag(name: str):
    match = re.search("\[(.+?)\]", name)
    if match:
        return match[1]


def removeTag(name: str, tag: str):
    return name[: -(len(tag) + 2)]  # remove the tag since not needed


def strip_accents(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return str(text)


def formatName(name: str):
    name = strip_accents(name)
    name = name.replace("_", "-")  # ' is replaced to _ and we use - instead
    return name.strip().replace(" ", "_")  # we replace space with underscore_
