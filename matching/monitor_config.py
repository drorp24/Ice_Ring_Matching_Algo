from common.entities.base_entities.base_entity import JsonableBaseEntity

class MonitorConfig(JsonableBaseEntity):

    def __init__(self, enabled: bool, min_iterations: int=0, save_data:bool=False, plot_data:bool=False,
                 output_directory:str=''):
        self._enabled = enabled
        self._min_iterations = min_iterations
        self._save_data = save_data
        self._plot_data = plot_data
        self._output_directory = output_directory

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return MonitorConfig(
            enabled=dict_input["enabled"],
            min_iterations=dict_input["min_iterations"],
            save_data=dict_input["save_data"],
            plot_data=dict_input["plot_data"],
            output_directory=dict_input["output_directory"])

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def save_data(self) -> bool:
        return self._save_data

    @property
    def plot_data(self) -> bool:
        return self._plot_data

    @property
    def min_iterations(self) -> int:
        return self._min_iterations

    @property
    def output_directory(self) -> str:
        return self._output_directory

    def __eq__(self, other):
        return (self.enabled == other.enabled) and \
               (self.min_iterations == other.min_iterations) and \
               (self.save_data == other.save_data) and \
               (self.plot_data == other.plot_data) and \
               (self.output_directory == other.output_directory)
