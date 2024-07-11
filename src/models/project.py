import os


class Project:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.media_path = os.path.join(path, 'media')

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
        }

    def get_file_path(self):
        return os.path.join(self.path, f"{self.name}.json")

    @staticmethod
    def from_dict(data):
        if "name" not in data or "path" not in data:
            raise ValueError("Missing required field in project data")
        return Project(data["name"], data["path"])