import json
import platform
from pathlib import Path, PureWindowsPath


class DeliveryRequestDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    @staticmethod
    def object_hook(dct):
        if 'DeliveryRequest' in dct:
            return DeliveryRequestConf(dct['DeliveryRequest'])
        return dct

class DeliveryRequestConf:
    def __init__(self, delivery_request_dict):
        self.__delivery_requests = delivery_request_dict

    @property
    def delivery_requests(self):
        return self.__delivery_requests

    @staticmethod
    def from_file(file_path) -> 'dict':
        system = platform.system()
        filename = Path(file_path)
        if system is 'windows':
            filename = PureWindowsPath(filename)
        correct_path = Path(filename)
        with open(correct_path, "r") as file:
            json_str = file.read()
        return json.loads(json_str, cls=DeliveryRequestDecoder)

    def __repr__(self):
        return "<deliveryRequests> \n" + \
               f"{self.__delivery_requests} \n" + \
               f"</deliveryRequests>"

