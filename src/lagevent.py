"""module for LagEvent data class"""
import json

class LagEvent:
    """LagEvent data class"""
    def __init__(self, value):
        self.type = 'lagevent'
        self.value = value
        self.tags = ["lag"]

    def to_json(self):
        """Serializes class to json"""
        return json.dumps(self.__dict__)
