"""module for MachineTemperature data class"""
import json
import dateutil.parser

class MachineTemperature:
    """MachineTemperature data class"""
    def __init__(self, machineid, temperature, eventdate):
        self.machineid = machineid
        self.temperature = temperature
        self.eventdate = eventdate

    @classmethod
    def from_json(cls, jsonstring):
        """Hydrates the class from json input"""
        mydict = json.loads(jsonstring)
        eventdate = dateutil.parser.parse(mydict['eventdate'])
        return cls(mydict['machineid'], mydict['temperature'], eventdate)

    def to_json(self):
        """Serializes class to json"""
        tempdict = self.__dict__
        # tempdict['eventdate'] = self.eventdate.isoformat()
        return json.dumps(tempdict)
