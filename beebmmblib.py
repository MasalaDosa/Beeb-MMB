import os
from enum import Enum, auto


NUMBER_OF_IMAGES = 511
SIZE_OF_MMB_HEADER = 16
SIZE_OF_IMAGE_HEADER = 16
SIZE_OF_IMAGE = 204800

STATUS_NOT_INITIALISED = 240
STATUS_LOCKED = 15
STATUS_UNLOCKED = 0


def check_mmb(path_to_mmb: str):
    if not os.path.isfile(path_to_mmb):
        raise FileNotFoundError("BEEB.MMB File not found.")
    if not os.path.getsize(path_to_mmb) == SIZE_OF_MMB_HEADER + NUMBER_OF_IMAGES * (
            SIZE_OF_IMAGE_HEADER + SIZE_OF_IMAGE):
        raise ValueError("BEEB.MMB File is not valid.")


def check_index(index: int):
    if index < 0 or index > NUMBER_OF_IMAGES:
        raise IndexError("Invalid card index.")


class SSDImageStatus(Enum):
    """Describes the status of an SSD Image within the archive."""
    Unknown = auto()
    NotInitialised = auto()
    Unlocked = auto()
    Locked = auto()


class SSDImage:
    """Represents an SSDImage with the archive."""
    def __init__(self, index: int, path_to_mmb: str):
        check_index(index)
        check_mmb(path_to_mmb)

        self._index = index
        self._mmb_file = path_to_mmb
        self._name = None
        self._status = None
        self._data = None


    def _header_position(self) -> int:
        return SIZE_OF_MMB_HEADER + self._index * SIZE_OF_IMAGE_HEADER


    def _data_position(self) -> int:
        return SIZE_OF_MMB_HEADER + NUMBER_OF_IMAGES * SIZE_OF_IMAGE_HEADER + self._index * SIZE_OF_IMAGE;


    def __repr__(self) -> str:
        return "{:<5}\t{:<15}\t{}".format(self._index, self.name, self.status.name)


    @property
    def name(self) -> str:
        if self._name is None:
            with open(self._mmb_file, "rb") as f:
                f.seek(self._header_position());
                ba = f.read(SIZE_OF_IMAGE_HEADER - 1)
                self._name = "" + ba.decode('ascii').rstrip('\0')
        return self._name;


    @name.setter
    def name(self, value: str):
        if value is None:
            raise ValueError("Name must be provided")

        if len(value) > SIZE_OF_IMAGE_HEADER - 1:
            value = value[:SIZE_OF_IMAGE_HEADER - 1]

        ba = bytearray(value, 'ascii')
        while len(ba) < SIZE_OF_IMAGE_HEADER - 1:
            ba.append(0)

        with open(self._mmb_file, "rb+") as f:
            f.seek(self._header_position());
            f.write(ba)
        self._name = value


    @property
    def status(self) -> SSDImageStatus:
        if self._status is None:
            with open(self._mmb_file, "rb") as f:
                f.seek(self._header_position() + SIZE_OF_IMAGE_HEADER - 1);
                ba = f.read(1)
                self._status = SSDImageStatus.NotInitialised if ba[0] == STATUS_NOT_INITIALISED else \
                               SSDImageStatus.Locked if ba[0] == STATUS_LOCKED else \
                               SSDImageStatus.Unlocked if ba[0] == STATUS_UNLOCKED else \
                               SSDImageStatus.Unknown
        return self._status;


    @status.setter
    def status(self, value: SSDImageStatus):
        if value is None:
            raise ValueError("Status must be provided")

        if value == SSDImageStatus.Unknown:
            raise ValueError("Status must not be Unknown when setting")

        lookup = {SSDImageStatus.NotInitialised : STATUS_NOT_INITIALISED, SSDImageStatus.Locked : STATUS_LOCKED, SSDImageStatus.Unlocked : STATUS_UNLOCKED}
        ba = bytes([lookup[value]])

        with open(self._mmb_file, "rb+") as f:
            f.seek(self._header_position() + SIZE_OF_IMAGE_HEADER - 1);
            f.write(ba)
        self._status = value


    @property
    def data(self)->bytearray:
        if self._data is None:
            with open(self._mmb_file, "rb") as f:
                f.seek(self._data_position());
                self._data = f.read(SIZE_OF_IMAGE)
        return self._data;


    @data.setter
    def data(self, value: bytearray):
        if value is None:
            raise ValueError("Data must be provided")

        if len(value) != SIZE_OF_IMAGE:
            raise ValueError("Data must be {} bytes in length.".format(SIZE_OF_IMAGE))

        with open(self._mmb_file, "rb+") as f:
            f.seek(self._data_position());
            f.write(value)
        self._data = value


    def save_to_file(self, file_name: str):
        if file_name is None:
            raise ValueError("Filename must be provided")

        with open(file_name, "wb") as f:
            f.write(self.data)


    def load_from_file(self, file_name: str, image_name: str = None, force: bool = False):
        if file_name is None:
            raise ValueError("Filename must be provided")

        if not os.path.isfile(file_name):
            raise ValueError("SSD File not found.")

        if not os.path.getsize(file_name) == SIZE_OF_IMAGE:
            raise ValueError("SSD File is not valid.")

        if image_name is None:
            image_name = os.path.basename(file_name)

        if len(image_name) > SIZE_OF_IMAGE_HEADER - 1:
            image_name = image_name[:SIZE_OF_IMAGE_HEADER - 1]

        if not force and not self.status == SSDImageStatus.NotInitialised:
            raise ValueError("Attempt to overwrite an existing image at index {}.".format((self._index)));

        with open(file_name, "rb") as f:
            ba = f.read(SIZE_OF_IMAGE)

        self.da = ba
        self.name = image_name
        self.status = SSDImageStatus.Unlocked


class BeebArchive:
    """Represents the archive BEEB.MMB file."""
    def __init__(self, path_to_mmb: str):
        check_mmb(path_to_mmb)

        self._mmb_file = path_to_mmb
        self._index_to_image = {}


    def __getitem__(self, index: int) -> SSDImage:
        check_index(index)

        if not index in self._index_to_image:
            self._index_to_image[index] = SSDImage(index, self._mmb_file)

        return self._index_to_image[index]
