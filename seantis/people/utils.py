from collections import MutableSequence
from uuid import UUID


class UUIDList(MutableSequence):
    """ A class that acts exactly like a list, but only accepts UUIDS. In case
    of another 'typed' class or acute bordedom implement as a metaclass.

    """

    def __init__(self, data=None):
        self._list = list()

        if data is not None:
            map(self.append, data)

    def get_uuid(self, item):
        if not isinstance(item, UUID):
            return UUID(item).hex
        else:
            return item.hex

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __delitem__(self, i):
        del self._list[i]

    def __setitem__(self, i, item):
        self._list[i] = self.get_uuid(item)

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return repr(self._list)

    def insert(self, i, item):
        self._list.insert(i, self.get_uuid(item))

    def append(self, item):
        self.insert(len(self._list), self.get_uuid(item))
