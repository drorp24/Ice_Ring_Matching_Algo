import enum
import time

import pandas as pd


class MonitorData(enum.Enum):
    objective = 1
    total_priority = 2
    total_unmatched_delivery_requests = 3
    unmatched_delivery_requests_total_priority = 4
    iterations = 5
    runtime = 6


current_milli_time = lambda: int(round(time.time() * 1000))


class Monitor:

    def __init__(self):
        # data - DataFrame of MonitorData
        self._data = pd.DataFrame([], columns=[MonitorData.objective.name,
                                               MonitorData.total_priority.name,
                                               MonitorData.total_unmatched_delivery_requests.name,
                                               MonitorData.unmatched_delivery_requests_total_priority.name,
                                               MonitorData.iterations.name,
                                               MonitorData.runtime.name,
                                               ])
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None

        self._data = self._data.astype(dtype={MonitorData.objective.name: "int64",
                                              MonitorData.total_priority.name: "int64",
                                              MonitorData.total_unmatched_delivery_requests.name: "int64",
                                              MonitorData.unmatched_delivery_requests_total_priority.name: "int64",
                                              MonitorData.iterations.name: "int64",
                                              MonitorData.runtime.name: "int64"
                                              })

        # create best_solution
        self._num_of_iterations = 0
        self._start_time = current_milli_time()
        self._best_objective_value = None
        self._prev_objective_value = None

    @property
    def data(self):
        return self._data

    @property
    def best_objective_value(self):
        return self._best_objective_value

    @property
    def prev_objective_value(self):
        return self._prev_objective_value

    @property
    def num_of_iterations(self):
        return self._num_of_iterations

    def add_monitor(self, objective, total_priority, total_unmatched_delivery_requests,
                    unmatched_delivery_requests_total_priority, iterations, runtime):

        to_append = [objective,
                     total_priority,
                     total_unmatched_delivery_requests,
                     unmatched_delivery_requests_total_priority,
                     iterations,
                     runtime]

        a_series = pd.Series(to_append, index=self._data.columns)

        self._data = self._data.append(a_series, ignore_index=True)

    def update_data(self, current_objective_value: int = None, total_priority_value: int = None,
                    total_unmatched_delivery_requests: int = None,
                    unmatched_delivery_requests_total_priority: int = None):

        self._prev_objective_value = self._best_objective_value
        self._best_objective_value = current_objective_value
        self.add_monitor(current_objective_value, total_priority_value, total_unmatched_delivery_requests,
                         unmatched_delivery_requests_total_priority, self.num_of_iterations,
                         current_milli_time() - self._start_time)

    def increase_iterations(self):
        self._num_of_iterations += 1

    def __repr__(self):
        return repr(self._data)
