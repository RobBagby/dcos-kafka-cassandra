"""module for PartitionLag data class"""
import json
import dateutil.parser

class PartitionLag:
    """PartitionLag data class"""
    def __init__(self, partition, lag, eventdate):
        self.partition = partition
        self.lag = lag
        self.eventdate = eventdate

    @classmethod
    def from_json(cls, jsonstring):
        """Hydrates the class from json input"""
        mydict = json.loads(jsonstring)
        eventdate = dateutil.parser.parse(mydict['eventdate'])
        return cls(mydict['partition'], mydict['lag'], eventdate)

    def to_json(self):
        """Serializes class to json"""
        tempdict = self.__dict__
        tempdict['eventdate'] = self.eventdate.isoformat()
        return json.dumps(tempdict)
