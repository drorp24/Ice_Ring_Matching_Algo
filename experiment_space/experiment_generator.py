from random import Random
from typing import List

from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from experiment_space.distribution.supplier_category_distribution import SupplierCategoryDistribution
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import DeliveryRequest, DroneLoadingDock, \
    FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class MultiExperimentOptionsBasedGenerator:

    def __init__(self, base_experiment: Experiment):
        print('!')

        # within supply category
        # self._delivery_request_override_options: List[List[DeliveryRequest]] = []
        # self._zero_time_override_options: List[DateTimeExtension] = []
        # self._drone_loading_lock_override_options: List[List[DroneLoadingDock]] = []
        # self._zones_list_options: List[List[Zone]] = []
        #
        # # within generation of EmptyDroneDeliveryBoard
        # # within DroneSetProperties used to generate the EmptyDroneDeliveryBoard
        # self.drone_type_options: List[DroneType] = []
        # self.drone_formation_policy_options: List[DroneFormationTypePolicy] = []
        # self.package_configuration_policy_options: List[PackageConfigurationPolicy] = []
        # self.drone_amount_options: List[int] = []
        # self.max_route_time_entire_board_options: int = []
        # self.velocity_entire_board_options: float = []

        # # within MatcherConfig
        # self._zero_time_options: List[] = zero_time
        # self._solver = solver
        # self._constraints = constraints
        # self._unmatched_penalty = unmatched_penalty
        #
        # self._capacity_constraints = capacity_constraints
        # self._time_constraints = time_constraints
        # self._priority_constraints = priority_constraints


def extract_properties_from_class(base_instance, hierarchical_classes: List[str] = []):
    return {k: [calc_internal_extract(base_instance.__getattribute__(k), hierarchical_classes)] for k, v in
            type(base_instance).__dict__.items() if k[:1] != '_' and not callable(getattr(type(base_instance), k))}


def calc_internal_extract(base_instance, hierarchical_classes: List[str]):
    if type(base_instance).__name__ in hierarchical_classes:
        return extract_properties_from_class(base_instance, hierarchical_classes)
    return base_instance


# def extract_properties_from_class(base_instance):
#     return {k: [base_instance.__getattribute__(k)] for k, v in type(base_instance).__dict__.items() if k[:1] != '_'
#             and not callable(getattr(type(base_instance), k))}


def create_options_class(base_instance: object):
    return type(type(base_instance).__name__ + 'Options', (), extract_properties_from_class(base_instance))


supplier_category_path = '/Users/gilbaz/Code/Ice_Ring/experiment_space/tests/jsons/test_supplier_category.json'
supplier_category = SupplierCategory.from_json(SupplierCategory, supplier_category_path)
matcher_config_path = '/Users/gilbaz/Code/Ice_Ring/experiment_space/tests/jsons/test_matcher_config.json'
matcher_config = MatcherConfig.from_json(MatcherConfig, matcher_config_path)
drone_set_properties_path = '/Users/gilbaz/Code/Ice_Ring/experiment_space/tests/jsons/test_drone_set_properties.json'
drone_set_properties = DroneSetProperties.from_json(DroneSetProperties, drone_set_properties_path)
empty_drone_delivery_board = build_empty_drone_delivery_board(drone_set_properties, max_route_time_entire_board=400,
                                                              velocity_entire_board=10.0)
default_graph_creation_algorithm = FullyConnectedGraphAlgorithm()

if __name__ == '__main__':
    base_experiment = Experiment(supplier_category=supplier_category,
                                 matcher_config=matcher_config,
                                 empty_drone_delivery_board=empty_drone_delivery_board,
                                 graph_creation_algorithm=default_graph_creation_algorithm)

    supplier_category = SupplierCategoryDistribution().choose_rand(random=Random(42),
                                                                   amount={DeliveryRequest: 10,
                                                                           DroneLoadingDock: 1})[0]

    class_props = extract_properties_from_class(supplier_category)
    print(class_props)

    class_props = extract_properties_from_class(base_experiment, ['SupplierCategory'])
    print(class_props)

    sco = create_options_class(supplier_category)
    print(sco)

    beo = create_options_class(base_experiment)
    print(beo)

