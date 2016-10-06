from collections import Counter


class Bipartite():
    def __init__(self, forwards, backwards=None):
        self.forwards = forwards
        if backwards is None:
            self.backwards = {}
            for key, values in forwards.items():
                for value in values:
                    self.backwards.setdefault(
                        value, set()).add(key)
        else:
            self.backwards = backwards

    @classmethod
    def from_pairs(klass, pairs):
        new = klass({})
        for pair1, pair2 in pairs:
            new.add(pair1, pair2)
        return new

    def to_pairs(self):
        for key, values in self.forwards.items():
            for value in values:
                yield key, value

    @property
    def inv(self):
        return type(self)(self.backwards, self.forwards)

    def __getitem__(self, item):
        return self.forwards[item]

    def add(self, item, value):
        self.forwards.setdefault(
            item, set()).add(value)
        self.backwards.setdefault(
            value, set()).add(item)

    def remove(self, item, value):
        self.forwards[item].remove(value)
        if not self.forwards[item]:
            del self.forwards[item]
        self.backwards[value].remove(item)
        if not self.backwards[value]:
            del self.backwards[value]

    def keys(self):
        return self.forwards.keys()

    def values(self):
        return self.backwards.keys()

    def __len__(self):
        return sum(len(x) for x in self.forwards.values())

    def __repr__(self):
        return repr(self.forwards)


class MultiBipartite(Bipartite):
    def __init__(self, forwards, backwards=None):
        self.forwards = forwards
        if backwards is None:
            self.backwards = {}
            for key, values in forwards.items():
                for value, frequency in values.items():
                    edge = self.backwards.setdefault(
                        value, Counter())
                    edge[key] += frequency
        else:
            self.backwards = backwards
        self._len = sum(
            sum(x.values()) for x in self.forwards.values())

    def to_pairs(self):
        for key, values in self.forwards.items():
            for value, frequency in values.items():
                for _ in range(frequency):
                    yield key, value

    def add(self, item, value):
        f = self.forwards.setdefault(
            item, Counter())
        f[value] += 1
        b = self.backwards.setdefault(
            value, Counter())
        b[item] += 1
        self._len += 1

    def remove(self, item, value):
        if self.forwards[item][value] >= 2:
            self.forwards[item][value] -= 1
            self.backwards[value][item] -= 1
            self._len -= 1
        elif self.forwards[item][value] == 1:
            del self.forwards[item][value]
            if not self.forwards[item]:
                del self.forwards[item]
            del self.backwards[value][item]
            if not self.backwards[value]:
                del self.backwards[value]
            self._len -= 1
        else:
            raise KeyError("{:} has no pair ({:}, {:})".format(
                self, item, value))

    def __len__(self):
        return self._len
