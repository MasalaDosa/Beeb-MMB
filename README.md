# Beeb-MMB
Python 3 utility for managing BEEB.MMB files.
These are archives of BBC Micro software typically copied to an SD / MMC card and used with an interface such as TurboMMC to provide BBC Micros with a form of solid state storage.

usage: beebmmb.py [-h] [-f <PathToMMBFile>] [cmd and parameters]
optional arguments:
        -h, --help              show this help message and exit.
        -f, --file              set the path to the MMB file.  If omitted then BEEB.MMB in the current directory is assumed.
command and parameters can be:
        ls               list all images in the card file.
        save <index> <filename>          saves the image at <index> into a local file.
        load <index> <filename> [image_name] [force]             loads a local file into the image at <index>.
                The image is named [image_name] or derived from <filename> if not specified.
                If [force] is set to TRUE then non erased images may be overwritten.
        lock <index>             marks the image at <index> as locked.
        unlock <index>           marks the image at <index> as unlocked.
        erase <index>            marks the image at <index> as erased.
     
examples:
beebmmb.py ls
beebmmb.py erase 510
beebmmb.py load 510 tetris.ssd tetris true
beebmmb.py load 509 repton.ssd
beebmmb.py save 4 welcome.ssd
