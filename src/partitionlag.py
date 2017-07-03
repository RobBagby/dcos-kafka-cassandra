"""module for PartitionLag data class"""
import json

class PartitionLag:
    """PartitionLag data class"""
    def __init__(self, partition, lag):
        self.partition = partition
        self.lag = lag

    @classmethod
    def from_json(cls, jsonstring):
        """Hydrates the class from json input"""
        mydict = json.loads(jsonstring)
        return cls(mydict['partition'], mydict['lag'])

    def to_json(self):
        """Serializes class to json"""
        return json.dumps(self.__dict__)
