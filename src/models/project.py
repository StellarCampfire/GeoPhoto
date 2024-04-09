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