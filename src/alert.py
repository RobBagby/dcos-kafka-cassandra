"""module for LagEvent data class"""
import json

class Alert:
    """Alert data class"""
    def __init__(self, sensor_id, event_date, event_time, temperature):
        self.sensor_id = sensor_id
        self.event_date = event_time.strftime("%Y/%m/%d %H:%M:%S")
        self.temperature = temperature

    def to_json(self):
        """Serializes class to json"""
        return self.__dict__

class Alerts:
    """Alerts data class"""
    def __init__(self):
        self.alerts = []

    def append(self, alert):
        """appends a message"""
        self.alerts.append(alert)

    def encode_alert(self, obj):
        if isinstance(obj, Alert):
            return obj.to_json()
        return obj

    # def to_json(self):
    #     """Serializes class to json"""
    #     return json.dumps(self.__dict__, default=self.encode_alert)

class WebViewData:
    def __init__(self):
        self.last_alerts = Alerts()

    def encode_alert(self, obj):
        if isinstance(obj, Alerts):
            return obj.to_json()
        return obj

    # def to_json(self):
    #     """Serializes class to json"""
    #     return json.dumps(self.__dict__, default=self.encode_alert)

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        # Here you can serialize your object depending of its type
        # or you can define a method in your class which serializes the object           
        if isinstance(o, (Alert, Alerts, WebViewData)):
            return o.__dict__  # Or another method to serialize it
        else:
            return json.JSONEncoder.encode(self, o)


