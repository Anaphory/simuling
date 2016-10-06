class Bipartite(dict):
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
        return Bipartite(self.backwards, self.forwards)
    
    def __getitem__(self, item):
        return self.forwards[item]

    def add(self, item, value):
        self.forwards.setdefault(
            item, set()).add(value)
        self.backwards.setdefault(
            value, set()).add(item)

    def remove(self, item, value):
        self.forwards[item].remove(value)
        self.backwards[value].remove(item)

    def keys(self):
        return self.forwards.keys()

    def values(self):
        return self.backwards.keys()

    def __len__(self):
        return len(self.forwards)

