import os
from enum import Enum, auto


class IntervalCondition(Enum):
    DRY = auto()
    WET = auto()


class IntervalSettings:
    def __init__(self, interval_from=0.0, interval_to=0.5, is_marked=False, condition=IntervalCondition.WET):
        self.interval_from = interval_from
        self.interval_to = interval_to
        self.is_marked = is_marked
        self.condition = condition


class Project:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
        }

    @staticmethod
    def from_dict(data):
        if "name" not in data or "path" not in data:
            raise ValueError("Missing required field in project data")
        return Project(data["name"], data["path"])


class Well:
    def __init__(self, _id, name):
        self.id = _id
        self.name = name


class Interval:
    def __init__(self, _id, _version, well_id, interval_from, interval_to, condition, is_marked):
        self.id = _id
        self.version = _version
        self.well_id = well_id
        self.interval_from = interval_from
        self.interval_to = interval_to
        self.condition = condition
        self.is_marked = is_marked

    def get_full_name(self):
        return (f'{self.interval_from}_{self.interval_to}_v.{self.version}_'
                f'{"Marked" if self.is_marked else "NotMarked"}_{self.condition.name}')


class Photo:
    def __init__(self, _id, path, interval_id):
        self.id = _id
        self.path = path
        self.interval_id = interval_id
        name, _ = os.path.splitext(os.path.basename(self.path))
        self.name = name
