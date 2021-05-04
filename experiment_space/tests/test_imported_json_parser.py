import unittest
from pathlib import Path

from common.entities.base_entities.fleet.fleet_property_sets import BoardLevelProperties
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.imported_json_parser import ImportedJsonParser


class ImportedJsonParserTest(unittest.TestCase):
    parser_json_path = Path('experiment_space/tests/jsons/test_writing_imported_json_parser.json')
    experiment_from_parser_path = Path(
        'experiment_space/tests/jsons/test_writing_experiment_from_parser.json')

    @classmethod
    def setUpClass(cls):
        delivery_requests_file_path = "experiment_space/tests/jsons/exported/DeliveryRequests.json"
        drone_loading_docks_file_path = "experiment_space/tests/jsons/exported/DroneLoadingDocks.json"
        zones_file_path = "experiment_space/tests/jsons/exported/Zones.json"
        drone_set_properties_list_path = "experiment_space/tests/jsons/exported/fleet_allocations_input.json"
        matcher_config_path = "experiment_space/tests/jsons/exported/configuration_file.json"

        cls.expected_parser_obj = ImportedJsonParser(delivery_requests_file_path=delivery_requests_file_path,
                                                     drone_loading_docks_file_path=drone_loading_docks_file_path,
                                                     zones_file_path=zones_file_path,
                                                     drone_set_properties_list_path=drone_set_properties_list_path,
                                                     matcher_config_path=matcher_config_path,
                                                     graph_creation_algorithm=FullyConnectedGraphAlgorithm(),
                                                     board_level_properties=BoardLevelProperties())

        cls.supplier_category = cls.expected_parser_obj.export_supplier_category()
        cls.matcher_config = cls.expected_parser_obj.export_matcher_config()
        cls.drone_set_properties = cls.expected_parser_obj.export_drone_set_properties()
        cls.default_graph_creation_algorithm = FullyConnectedGraphAlgorithm()

        cls.expected_experiment = Experiment(supplier_category=cls.supplier_category,
                                             matcher_config=cls.matcher_config,
                                             drone_set_properties_list=cls.drone_set_properties,
                                             graph_creation_algorithm=cls.default_graph_creation_algorithm)

    @classmethod
    def tearDownClass(cls):
        if cls.parser_json_path.exists():
            cls.parser_json_path.unlink()
        if cls.experiment_from_parser_path.exists():
            cls.experiment_from_parser_path.unlink()

    def test_writing_parser_json(self):
        self.expected_parser_obj.to_json(self.parser_json_path)

        parser_json_to_dict = ImportedJsonParser.json_to_dict(self.parser_json_path)
        parser_obj = ImportedJsonParser.dict_to_obj(parser_json_to_dict)

        self.assertEqual(parser_obj, self.expected_parser_obj)

    def test_save_as_experiment(self):
        self.expected_parser_obj.save_as_experiment(self.experiment_from_parser_path)

        experiments_to_dict = Experiment.json_to_dict(self.experiment_from_parser_path)
        loaded_experiment = Experiment.dict_to_obj(experiments_to_dict)

        self.assertEqual(loaded_experiment, self.expected_experiment)
