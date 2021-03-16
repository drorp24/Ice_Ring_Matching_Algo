from ortools.constraint_solver.pywrapcp import RoutingModel, RoutingIndexManager
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput
from matching.monitor import Monitor
from matching.ortools.ortools_matcher_constraints import OrToolsDimensionDescription
from matching.ortools.ortools_solution_handler import ORToolsSolutionHandler


class ORToolsMatcherMonitor:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, index_manager: RoutingIndexManager,
                 routing_model: RoutingModel, search_parameters: RoutingSearchParameters, matcher_input: MatcherInput,
                 solution_handler: ORToolsSolutionHandler):

        self._graph_exporter = graph_exporter
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._search_parameters = search_parameters
        self._solution_handler = solution_handler
        self._monitor_config = matcher_input.config.monitor
        self._graph = matcher_input.graph
        self._monitor = Monitor()
        self._priority_dimension = self._routing_model.GetDimensionOrDie('priority')
        self.print_status = False

    @property
    def monitor(self):
        return self._monitor

    def add_search_monitor(self):
        # CloseModelWithParameters
        self._routing_model.CloseModelWithParameters(self._search_parameters)

        self._add_best_solution_collector()
        self._add_unmatched_delivery_requests_monitoring()
        self._add_priority_monitoring()
        # self._add_time_monitoring()
        self._add_vehicle_monitoring()
        self._add_route_monitoring()
        self._routing_model.AddSearchMonitor(self._routing_model.solver().CustomLimit(self.monitor_search))

    def _add_best_solution_collector(self):
        self.best_solution_collector = self._routing_model.solver().BestValueSolutionCollector(False)
        self.best_solution_collector.AddObjective(self._routing_model.CostVar())
        self._routing_model.AddSearchMonitor(self.best_solution_collector)

    def _add_unmatched_delivery_requests_monitoring(self):
        for i in range(self._index_manager.GetNumberOfNodes()):
            self.best_solution_collector.Add(self._routing_model.ActiveVar(i))

    def _add_vehicle_monitoring(self):
        for i in range(self._index_manager.GetNumberOfVehicles()):
            self.best_solution_collector.Add(self._routing_model.ActiveVehicleVar(i))

    def _add_route_monitoring(self):
        for i in range(self._index_manager.GetNumberOfNodes()+ self._index_manager.GetNumberOfVehicles() - 1):
            self.best_solution_collector.Add(self._routing_model.NextVar(i))

    def _add_priority_monitoring(self):
        for index in range(self._index_manager.GetNumberOfIndices()):
            cum_var = self._priority_dimension.CumulVar(index)
            self.best_solution_collector.Add(cum_var)

    def _add_time_monitoring(self):
        time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.time.value)
        for index in range(self._index_manager.GetNumberOfIndices()):
            cum_var = time_dimension.CumulVar(index)
            self.best_solution_collector.Add(cum_var)

    def _add_best_priority_solution_collector(self):
        self.best_priority_solution_collector = self._routing_model.solver().BestValueSolutionCollector(False)
        for i in range(self._index_manager.GetNumberOfIndices()):
            cum_var = self._priority_dimension.CumulVar(i)
            self.best_priority_solution_collector.Add(cum_var)
        self.best_priority_solution_collector.AddObjective(self._routing_model.CostVar())
        self._routing_model.AddSearchMonitor(self.best_priority_solution_collector)

    def _add_unmatched_delivery_requests_collector(self):
        self.unmatched_delivery_requests_solution_collector = self._routing_model.solver().BestValueSolutionCollector(
            False)
        for i in range(self._index_manager.GetNumberOfNodes()):
            self.unmatched_delivery_requests_solution_collector.Add(self._routing_model.ActiveVar(i))
        self.unmatched_delivery_requests_solution_collector.AddObjective(self._routing_model.CostVar())
        self._routing_model.AddSearchMonitor(self.unmatched_delivery_requests_solution_collector)

    def _add_last_solution_collector(self):
        self.last_solution_collector = self._routing_model.solver().LastSolutionCollector()
        self.last_solution_collector.AddObjective(self._routing_model.CostVar())
        self._routing_model.AddSearchMonitor(self.last_solution_collector)

    def _add_all_solutions_collector(self):
        self.all_solutions_collector = self._routing_model.solver().AllSolutionCollector()
        self._routing_model.AddSearchMonitor(self.all_solutions_collector)

    def monitor_search(self):
        self._monitor.increase_iterations()
        if self.best_solution_collector.SolutionCount() == 0:
            if self._monitor.num_of_iterations % 1000 == 0:
                self._monitor.update_data()
                if self.print_status:
                    print(f"iteration {self._monitor.num_of_iterations} : No Solution")

            return False



        # last_objective_value = self.last_solution_collector.ObjectiveValue(0)
        # current_objective_value = self.best_solution_collector.ObjectiveValue(0) if self.best_solution_collector.SolutionCount() > 0 else last_objective_value


        if self._monitor.num_of_iterations % self._monitor_config.iterations_between_monitoring == 0:
            # dr = self._solution_handler.create_drone_delivery_board(self.best_solution_collector.Solution(0))
            best_objective_value = self.best_solution_collector.ObjectiveValue(0)
            total_priority_value = self._calc_total_priority()
            total_unmatched_delivery_requests, unmatched_delivery_requests_total_priority = self._calc_total_unmatched_delivery_requests()
            self._monitor.update_data(best_objective_value, total_priority_value, total_unmatched_delivery_requests, unmatched_delivery_requests_total_priority)
        # if self.print_status and self._monitor.num_of_iterations % 1000 == 0:
        #     print(
        #         f"iteration {self._monitor.num_of_iterations} current objective value {best_objective_value}, total priority {total_priority_value}, unmatched delivery requests {total_unmatched_delivery_requests}, unmatched delivery requests total priority {unmatched_delivery_requests_total_priority}")
        if self._monitor.num_of_iterations == self._monitor_config.min_iterations:
            # todo choose conditions for stopping?
            return True
        # print (1)
        return False

    def _calc_total_priority(self):
        total_priority = 0
        for vehicle_index in range(self._routing_model.GetMaximumNumberOfActiveVehicles()):
            end_node_index = self._routing_model.End(vehicle_index)
            priority_cumu_var = self._priority_dimension.CumulVar(end_node_index)
            total_priority += self.best_solution_collector.Solution(0).Value(priority_cumu_var)
        return total_priority

    def _calc_total_unmatched_delivery_requests(self):
        unmatched_delivery_requests = 0
        unmatched_delivery_requests_total_priority = 0
        for node_index in range(self._routing_model.Size()):
            if self._routing_model.IsStart(node_index) or self._routing_model.IsEnd(node_index):
                continue
            if not self.best_solution_collector.Solution(0).Value(self._routing_model.ActiveVar(node_index)):
                unmatched_delivery_requests += 1
                unmatched_delivery_requests_total_priority += self._get_priority(node_index)

        return unmatched_delivery_requests, unmatched_delivery_requests_total_priority

    def _get_priority(self, from_index):
        from_node = self._index_manager.IndexToNode(from_index)
        return self._graph_exporter.export_priorities(self._graph)[from_node]
