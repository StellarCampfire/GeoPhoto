import os


class Photo:
    def __init__(self, _id, path, interval_id):
        self.id = _id
        self.path = path
        self.interval_id = interval_id
        name, _ = os.path.splitext(os.path.basename(self.path))
        self.name = name