from enum import Enum, auto


class WindowType(Enum):
    START_WINDOW = auto()
    NEW_PROJECT_WINDOW = auto()
    PROJECT_WINDOW = auto()
    NEW_WELL_WINDOW = auto()
    WELL_WINDOW = auto()
    NEW_INTERVAL_WINDOW = auto()
    INTERVAL_WINDOW = auto()
    PHOTO_REVIEW_WINDOW = auto()
    PHOTO_VIEW_WINDOW = auto()
    SETTINGS_WINDOW = auto()
    DELETE_WELL_WINDOW = auto()
    DELETE_INTERVAL_WINDOW = auto()
