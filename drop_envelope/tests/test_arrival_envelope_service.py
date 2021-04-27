import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.package import PackageType
from common.graph.operational.operational_graph import OperationalGraph
from common.math.angle import ChoicesAngleDistribution, Angle, AngleUnit
from drop_envelope.arrival_envelope_service import MockPotentialEnvelopeService, MockPotentialArrivalEnvelopeService
from drop_envelope.delivery_request_envelope import DeliveryRequestPotentialEnvelope
from drop_envelope.loading_dock_envelope import LoadingDockPotentialEnvelope
from drop_envelope.slide_service import MockSlidesServiceWrapper
from geometry.distribution.geo_distribution import NormalPointDistribution
from geometry.geo_factory import create_point_2d


def create_delivery_request_distribution(center_point, sigma_x: float, sigma_y: float) -> DeliveryRequestDistribution:
    package_distribution = create_single_package_distribution()
    return build_delivery_request_distribution(package_type_distribution=package_distribution,
                                               relative_pdp_location_distribution=NormalPointDistribution(center_point,
                                                                                                          sigma_x,
                                                                                                          sigma_y),
                                               azimuth_distribution=create_azimuth_choice_distribution())


def create_single_package_distribution() -> PackageDistribution:
    package_type_distribution_dict = {PackageType.LARGE: 1}
    package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
    return package_distribution


def create_azimuth_choice_distribution() -> ChoicesAngleDistribution:
    azimuths_choices = [Angle(value=0, unit=AngleUnit.DEGREE), Angle(value=30, unit=AngleUnit.DEGREE),
                        Angle(value=60, unit=AngleUnit.DEGREE), Angle(value=90, unit=AngleUnit.DEGREE),
                        Angle(value=180, unit=AngleUnit.DEGREE)]
    return ChoicesAngleDistribution(angles=azimuths_choices)


class BasicArrivalEnvelopeService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = create_delivery_request_distribution(center_point=create_point_2d(x=0, y=0), sigma_x=20,
                                                                     sigma_y=20).choose_rand(random=Random(100),
                                                                                             amount={
                                                                                                 DeliveryRequest: 10})
        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=3)

    def test_arrival_envelope_service_creation(self):
        dr_envelope = {dr: DeliveryRequestPotentialEnvelope.from_delivery_request(dr) for dr in self.dr_dataset_random}
        dld_envelope = {dld: LoadingDockPotentialEnvelope(drone_loading_dock=dld) for dld in self.dld_dataset_random}
        envelopes = dict(list(dr_envelope.items()) + list(dld_envelope.items()))
        service = MockPotentialEnvelopeService(envelopes)
        drs = list(filter(lambda node: isinstance(node, DeliveryRequest), list(service.potential_envelopes.keys())))
        dlds = list(filter(lambda node: isinstance(node, DroneLoadingDock), list(service.potential_envelopes.keys())))
        self.assertEqual(len(service.potential_envelopes), 13)
        self.assertEqual(len(drs), 10)
        self.assertEqual(len(dlds), 3)

    def test_from_nodes_creation(self):
        graph = OperationalGraph()
        graph.add_delivery_requests(self.dr_dataset_random)
        graph.add_drone_loading_docks(self.dld_dataset_random)
        service = MockPotentialEnvelopeService.from_operational_nodes(graph.nodes)
        drs = list(filter(lambda node: isinstance(node, DeliveryRequest), list(service.potential_envelopes.keys())))
        dlds = list(filter(lambda node: isinstance(node, DroneLoadingDock), list(service.potential_envelopes.keys())))
        self.assertEqual(len(service.potential_envelopes), 13)
        self.assertEqual(len(drs), 10)
        self.assertEqual(len(dlds), 3)

    def test_arrival_envelope(self):
        graph = OperationalGraph()
        graph.add_delivery_requests(self.dr_dataset_random)
        graph.add_drone_loading_docks(self.dld_dataset_random)
        # service = MockPotentialEnvelopeService.from_operational_nodes(graph.nodes)
        service = MockPotentialArrivalEnvelopeService.from_operational_nodes(graph.nodes)
        sdr_arrival_envelopes = list(map(lambda dr: service.get_potential_arrival_envelope(dr), self.dr_dataset_random))
        dr_arrival_envelopes = list(map(lambda dr: DeliveryRequestPotentialEnvelope.from_delivery_request(dr).
                                        get_potential_arrival_envelope(MockSlidesServiceWrapper.
                                                                       get_drone_azimuth_level_values(),
                                                                       Angle(value=90, unit=AngleUnit.DEGREE)),
                                        self.dr_dataset_random))
        self.assertEqual(sdr_arrival_envelopes, dr_arrival_envelopes)
        sdld_arrival_envelopes = list(
            map(lambda dld: service.get_potential_arrival_envelope(dld), self.dld_dataset_random))
        dld_arrival_envelopes = list(
            map(lambda dld: LoadingDockPotentialEnvelope(dld).
                get_potential_arrival_envelope(MockSlidesServiceWrapper.get_drone_azimuth_level_values(),
                                               Angle(value=90, unit=AngleUnit.DEGREE)),
                self.dld_dataset_random))
        self.assertEqual(sdld_arrival_envelopes, dld_arrival_envelopes)
