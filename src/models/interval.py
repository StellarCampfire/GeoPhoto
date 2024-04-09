from enum import Enum, auto


class IntervalCondition(Enum):
    DRY = auto()
    WET = auto()


class BaseIntervalSettings:
    def __init__(self, interval_from=0.0, interval_to=0.5, condition=IntervalCondition.WET, is_marked=False):
        self.interval_from = interval_from
        self.interval_to = interval_to
        self.condition = condition
        self.is_marked = is_marked


class Interval(BaseIntervalSettings):
    def __init__(self, _id, _version, well_id, interval_from, interval_to, condition, is_marked):
        super().__init__(interval_from, interval_to, condition, is_marked)
        self.id = _id
        self.version = _version
        self.well_id = well_id

    def get_full_name(self):
        return (f'{self.interval_from}_{self.interval_to}_v.{self.version}_'
                f'{"Marked" if self.is_marked else "NotMarked"}_{self.condition.name}')
