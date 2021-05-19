import unittest
from pathlib import Path

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.operational_graph import OperationalGraph
from experiment_space.analyzer.quantitative_analyzers import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer, MatchingEfficiencyAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.imported_json_parser import ImportedJsonParser
from experiment_space.visualization.experiment_visualizer import draw_matched_scenario, draw_delivery_board
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import MapImage

SHOW_VISUALS = True
EXPORT_JSON = True


class BasicV05End2EndExperiment(unittest.TestCase):
    v05_json_path = Path('experiment_space/tests/jsons/test_e2e_v05_experiment.json')
    v05_json_export_graph_path = Path('experiment_space/tests/jsons/graph.json')
    v05_json_export_delivery_board_path = Path('experiment_space/tests/jsons/delivery_board.json')

    experiment_json_from_parser_path = Path(
        'experiment_space/tests/jsons/test_writing_experiment_from_parser.json')

    @classmethod
    def setUpClass(cls):

        parser_dict = ImportedJsonParser.json_to_dict(cls.v05_json_path)
        parser = ImportedJsonParser.dict_to_obj(parser_dict)
        parser.save_as_experiment(cls.experiment_json_from_parser_path)

        experiment_dict = Experiment.json_to_dict(cls.experiment_json_from_parser_path)
        cls.experiment = Experiment.dict_to_obj(experiment_dict)

    @classmethod
    def tearDownClass(cls):
        if cls.experiment_json_from_parser_path.exists():
            cls.experiment_json_from_parser_path.unlink()
        if cls.v05_json_export_graph_path.exists():
            cls.v05_json_export_graph_path.unlink()
        if cls.v05_json_export_delivery_board_path.exists():
            cls.v05_json_export_delivery_board_path.unlink()

    def test_calc_v05_visualization(self):

        map_image = MapImage(map_background_path=Path("visualization/basic/all_map.png"),
                             west_lon=33.65216, east_lon=36.60633, south_lat=29.52792, north_lat=33.84980)

        self._run_end_to_end_visual_experiment(self.experiment, SHOW_VISUALS, map_image, EXPORT_JSON)

    @classmethod
    def _run_end_to_end_visual_experiment(cls, experiment: Experiment, show_visuals: bool, map_image: MapImage = None,
                                          export_json=False):
        if experiment.delivery_board_path:
            result_drone_delivery_board = experiment.export_drone_delivery()
            cls.analysis_results(result_drone_delivery_board)
            if show_visuals:
                cls.draw_results(delivery_board=result_drone_delivery_board, experiment=experiment, map_image=map_image)
                return
        if experiment.operational_graph_path:
            graph = experiment.export_operational_graph()
        else:
            graph = experiment.graph_creation_algorithm.create(experiment.supplier_category)
        result_drone_delivery_board = experiment.run_match(graph=graph)
        if export_json:
            print(f'# Exporting Graph to {cls.v05_json_export_graph_path}')
            graph.to_json(cls.v05_json_export_graph_path)
            print(f'# Exporting Drone delivery to {cls.v05_json_export_delivery_board_path}')
            result_drone_delivery_board.to_json(cls.v05_json_export_delivery_board_path)
        print("# delivery_requests from json", len(experiment.supplier_category.delivery_requests))
        print("# drone_loading_docks from json", len(experiment.supplier_category.drone_loading_docks))
        print("# graph nodes including docks", len(graph.nodes))
        print(result_drone_delivery_board)

        cls.analysis_results(result_drone_delivery_board)
        if show_visuals:
            cls.draw_results(delivery_board=result_drone_delivery_board, graph=graph, experiment=experiment,
                             map_image=map_image)

    @classmethod
    def analysis_results(cls, delivery_board: DroneDeliveryBoard):
        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]
        analysis_results = Experiment.run_analysis_suite(delivery_board, analyzers_to_run)
        print(analysis_results)

    @classmethod
    def draw_results(cls, delivery_board: DroneDeliveryBoard, experiment: Experiment, map_image: MapImage,
                     graph: OperationalGraph = None):
        if graph:
            draw_matched_scenario(delivery_board=delivery_board, graph=graph,
                                  supplier_category=experiment.supplier_category, map_image=map_image,
                                  aggregate_by_delivering_drones=True, draw_zones=True,
                                  coordinate_sys=Drawer2DCoordinateSys.GEOGRAPHIC_UTM)
        else:
            draw_delivery_board(delivery_board=delivery_board,
                                supplier_category=experiment.supplier_category, map_image=map_image,
                                aggregate_by_delivering_drones=True,
                                coordinate_sys=Drawer2DCoordinateSys.GEOGRAPHIC_UTM)
