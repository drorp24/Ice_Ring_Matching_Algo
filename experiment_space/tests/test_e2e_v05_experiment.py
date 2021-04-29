import unittest
from pathlib import Path

from experiment_space.analyzer.quantitative_analyzers import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer, MatchingEfficiencyAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.imported_json_parser import ImportedJsonParser
from experiment_space.visualization.experiment_visualizer import draw_matched_scenario
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import MapImage

SHOW_VISUALS = True


class BasicV05End2EndExperiment(unittest.TestCase):
    v05_json_path = Path('experiment_space/tests/jsons/test_e2e_v05_experiment.json')

    experiment_json_from_parser_path = Path(
        'experiment_space/tests/jsons/test_writing_experiment_from_parser.json')

    @classmethod
    def setUpClass(cls):

        parser_dict = ImportedJsonParser.json_to_dict(cls.v05_json_path)
        parser = ImportedJsonParser.dict_to_obj(parser_dict)
        parser.save_as_experiment(cls.experiment_json_from_parser_path)

        experiment_dict = Experiment.json_to_dict(cls.experiment_json_from_parser_path)
        cls.experiment = Experiment.dict_to_obj(experiment_dict)

        print("#delivery_requests", len(cls.experiment.supplier_category.delivery_requests))
        print("#drone_loading_docks", len(cls.experiment.supplier_category.drone_loading_docks))

    @classmethod
    def tearDownClass(cls):
        if cls.experiment_json_from_parser_path.exists():
            cls.experiment_json_from_parser_path.unlink()

    def test_calc_north_scenario_visualization(self):

        map_image = MapImage(map_background_path=Path("visualization/basic/all_map.png"),
                             west_lon=34.31, east_lon=36.135, south_lat=29.5, north_lat=33.78)

        self._run_end_to_end_visual_experiment(self.experiment, SHOW_VISUALS, map_image)

    @staticmethod
    def _run_end_to_end_visual_experiment(experiment: Experiment, show_visuals: bool, map_image: MapImage = None):
        graph = experiment.graph_creation_algorithm.create(experiment.supplier_category)
        result_drone_delivery_board = experiment.run_match()
        print(result_drone_delivery_board)
        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]
        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board, analyzers_to_run)
        print(analysis_results)
        if show_visuals:
            draw_matched_scenario(delivery_board=result_drone_delivery_board, graph=graph,
                                  supplier_category=experiment.supplier_category, map_image=map_image,
                                  aggregate_by_delivering_drones=True,
                                  coordinate_sys=Drawer2DCoordinateSys.GEOGRAPHIC_UTM
                                  )
        return analysis_results
