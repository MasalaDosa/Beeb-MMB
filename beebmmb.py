#!/usr/bin/env python3
import sys, getopt
import beebmmblib


def main():
    # Parse command line
    args = sys.argv[1:]
    short_opts = "hf:"
    long_opts = ["help", "file="]
    try:
        arguments, values = getopt.getopt(args, short_opts, long_opts)
    except  getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        sys.exit(2)

    # Default MMB file is in the working folder, but can be overridden
    mmb_file = "./BEEB.MMB"
    for current_argument, current_value in arguments:
        args.remove(current_argument)
        if current_value:
            args.remove(current_value)
        if current_argument in ("-h", "--help"):
            usage()
        elif current_argument in ("-f", "--file"):
            mmb_file = current_value
    try:
        card = beebmmblib.BeebArchive(mmb_file)
    except (FileNotFoundError, ValueError) as err:
        print(str(err))
        sys.exit(2)

    # Execute the requested cmd.
    if args:
        if args[0].upper() == "LS":
            ls(card)
        elif args[0].upper() == "SAVE":
            save(card, args[1:])
        elif args[0].upper() == "LOAD":
            load(card, args[1:])
        elif args[0].upper() == "LOCK":
            lock(card, args[1:])
        elif args[0].upper() == "UNLOCK":
            unlock(card, args[1:])
        elif args[0].upper() == "ERASE":
            erase(card, args[1:])
        else:
            usage()


def ls(card: beebmmblib.BeebArchive):
    """Lists all images stored within the MMB archive."""
    try:
        for i in range(0, beebmmblib.NUMBER_OF_IMAGES):
            print(card[i])
    except (FileNotFoundError, IOError, OSError) as err:
        print("Unable to read MMB file.")
        print(str(err))
        sys.exit(2)


def save(card: beebmmblib.BeebArchive, args: list):
    """Saves the image from the at index in the archive to file."""
    if len(args) < 2:
        print("save requires an index and a destination file.")
        sys.exit(2)
    i = _get_index(args[0])
    file_name = args[1]
    try:
        card[i].save_to_file(file_name)
    except (FileNotFoundError, IOError, OSError) as err:
        print("Unable to save MMB file.")
        print(str(err))
        sys.exit(2)


def load(card: beebmmblib.BeebArchive, args: list):
    """Loads an SSD File into the archive at index."""
    if len(args) < 2:
        print("load requires an index and a destination file.")
        sys.exit(2)
    i = _get_index(args[0])
    file_name = args[1]
    image_name = None
    if len(args) > 2:
        image_name = args[2]
    force = False
    if len(args) > 3:
        force = args[3].upper() in ['TRUE', '1', 'T', 'Y', 'YES']
    try:
        card[i].load_from_file(file_name, image_name, force)
    except (ValueError, FileNotFoundError, IOError, OSError) as err:
        print("Unable to load into MMB file.")
        print(str(err))
        sys.exit(2)


def lock(card: beebmmblib.BeebArchive, args: list):
    """Marks the image at index as locked."""
    if len(args) < 1:
        print("lock requires an index.")
        sys.exit(2)
    i = _get_index(args[0])
    card[i].status = beebmmblib.SSDImageStatus.Locked


def unlock(card: beebmmblib.BeebArchive, args: list):
    """Marks the image at index as unlocked."""
    if len(args) < 1:
        print("unlock requires an index.")
        sys.exit(2)
    i = _get_index(args[0])
    card[i].status = beebmmblib.SSDImageStatus.Unlocked


def erase(card: beebmmblib.BeebArchive, args: list):
    """Marks the image at index as erased."""
    if len(args) < 1:
        print("erase requires an index.")
        sys.exit(2)
    i = _get_index(args[0])
    card[i].status = beebmmblib.SSDImageStatus.NotInitialised


def _get_index(index_str: str) -> int:
    try:
        i = int(index_str)
    except ValueError as err:
        print("Index should be numeric.")
        sys.exit(2)
    try:
        beebmmblib.check_index(i)
    except IndexError as err:
        print("Index should be between 0 and {}".format(beebmmblib.NUMBER_OF_IMAGES))
        sys.exit(2)
    return i


def usage():
    print("usage: beebmmb.py [-h] [-f:<PathToMMBFile>] [cmd and parameters]")
    print("optional arguments:")
    print(("\t-h, --help\t\tshow this help message and exit."))
    print(("\t-f, --file\t\tset the path to the MMB file.  If omitted then BEEB.MMB in the current directory is assumed."))
    print("command and parameters can be:")
    print("\tls\t\tlist all images in the card file.")
    print("\tsave <index> <filename>\t\tsaves the image at <index> into a local file.")
    print("\tload <index> <filename> [image_name] [force] \t\tloads a local file into the image at <index>.")
    print("\t\tThe image is named [image_name] or derived from <filename> if not specified.")
    print("\t\tIf [force] is set to TRUE then non erased images may be overwritten.")
    print("\tlock <index>\t\t marks the image at <index> as locked.")
    print("\tunlock <index>\t\t marks the image at <index> as unlocked.")
    print("\terase <index>\t\t marks the image at <index> as erased.")
    sys.exit(0)


if __name__ == '__main__':
    main()
