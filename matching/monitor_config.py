from common.entities.base_entities.base_entity import JsonableBaseEntity


class MonitorConfig(JsonableBaseEntity):

    def __init__(self, enabled: bool, iterations_between_monitoring=1, max_iterations: int = 0, save_plot: bool = False,
                 show_plot: bool = False, separate_charts: bool = False,
                 output_directory: str = ''):
        self._enabled = enabled
        self._iterations_between_monitoring = iterations_between_monitoring
        self._max_iterations = max_iterations
        self._save_plot = save_plot
        self._show_plot = show_plot
        self._separate_charts = separate_charts
        self._output_directory = output_directory

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def save_plot(self) -> bool:
        return self._save_plot

    @property
    def show_plot(self) -> bool:
        return self._show_plot

    @property
    def separate_charts(self) -> bool:
        return self._separate_charts

    @property
    def iterations_between_monitoring(self) -> int:
        return self._iterations_between_monitoring

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    @property
    def output_directory(self) -> str:
        return self._output_directory

    def __eq__(self, other):
        return (self.enabled == other.enabled) and \
               (self.max_iterations == other.max_iterations) and \
               (self.iterations_between_monitoring == other.iterations_between_monitoring) and \
               (self.save_plot == other.save_plot) and \
               (self.show_plot == other.show_plot) and \
               (self.separate_charts == other.separate_charts) and \
               (self.output_directory == other.output_directory)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return MonitorConfig(
            enabled=dict_input["enabled"],
            iterations_between_monitoring=dict_input["iterations_between_monitoring"],
            max_iterations=dict_input["max_iterations"],
            save_plot=dict_input["save_plot"],
            show_plot=dict_input["show_plot"],
            separate_charts=dict_input["separate_charts"],
            output_directory=dict_input["output_directory"])
