from __future__ import annotations

from typing import List, Dict

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.graph.operational.operational_graph import OperationalNode
from common.math.angle import Angle, AngleUnit
from drop_envelope.arrival_envelope import PotentialArrivalEnvelope
from drop_envelope.delivery_request_envelope import DeliveryRequestPotentialEnvelope
from drop_envelope.envelope_collections import PotentialEnvelopeCollection
from drop_envelope.loading_dock_envelope import LoadingDockPotentialEnvelope
from drop_envelope.slide_service import MockSlidesServiceWrapper


# class MockPotentialEnvelopeService:
#     def __init__(self, potential_envelopes: Dict[DeliveryRequest | DroneLoadingDock, PotentialEnvelopeCollection]):
#         self._potential_envelopes = potential_envelopes
#
#     @classmethod
#     def from_internal_nodes(cls, internal_operational_nodes: List[DeliveryRequest | DroneLoadingDock]):
#         dr_potential_envelopes = {internal_node: DeliveryRequestPotentialEnvelope.from_delivery_request(internal_node)
#                                   for internal_node in
#                                   list(filter(lambda node: isinstance(node, DeliveryRequest),
#                                               internal_operational_nodes))}
#         ld_potential_envelopes = {internal_node: LoadingDockPotentialEnvelope(internal_node)
#                                   for internal_node in list(
#                 filter(lambda node: isinstance(node, DroneLoadingDock), internal_operational_nodes))}
#         potential_envelopes = dr_potential_envelopes.copy()
#         potential_envelopes.update(ld_potential_envelopes)
#         return MockPotentialEnvelopeService(potential_envelopes=potential_envelopes)
#
#     @classmethod
#     def from_operational_nodes(cls, operational_nodes: List[OperationalNode]):
#         dr_potential_envelopes = {
#             operational_node.internal_node: DeliveryRequestPotentialEnvelope.from_delivery_request(
#                 operational_node.internal_node)
#             for operational_node in
#             list(filter(lambda node: isinstance(node.internal_node, DeliveryRequest), operational_nodes))}
#         ld_potential_envelopes = {operational_node.internal_node: LoadingDockPotentialEnvelope(
#             operational_node.internal_node)
#             for operational_node in
#             list(filter(lambda node: isinstance(node.internal_node, DroneLoadingDock), operational_nodes))}
#         potential_envelopes = dr_potential_envelopes.copy()
#         potential_envelopes.update(ld_potential_envelopes)
#         return MockPotentialEnvelopeService(potential_envelopes=potential_envelopes)
#
#     @property
#     def potential_envelopes(self) -> Dict[DeliveryRequest | DroneLoadingDock, PotentialEnvelopeCollection]:
#         return self._potential_envelopes
#
#     def get_potential_arrival_envelope(self,
#                                        node: DeliveryRequest | DroneLoadingDock,
#                                        maneuver_angle=Angle(value=90, unit=AngleUnit.DEGREE)) \
#             -> PotentialArrivalEnvelope:
#         return self.potential_envelopes[node].get_potential_arrival_envelope(
#             MockSlidesServiceWrapper.get_drone_azimuth_level_values(),
#             maneuver_angle=maneuver_angle)


class MockPotentialArrivalEnvelopeService:
    def __init__(self, potential_arrival_envelopes: dict):
        self._potential_arrival_envelopes = potential_arrival_envelopes

    @staticmethod
    def filter_node_by_type(node: [OperationalNode | DeliveryRequest | DroneLoadingDock],
                            node_type: [DeliveryRequest | DroneLoadingDock]):
        if isinstance(node, OperationalNode):
            node = node.internal_node
        if isinstance(node, node_type):
            return node

    @classmethod
    def build_arrival_envelop_object_from_dr_node(cls, internal_node: [DeliveryRequest | DroneLoadingDock]):
        maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        drone_azimuth_level_values = MockSlidesServiceWrapper.get_drone_azimuth_level_values()
        potential_envelop_collection = DeliveryRequestPotentialEnvelope.from_delivery_request(internal_node)
        potential_arrival_env = potential_envelop_collection.get_potential_arrival_envelope(
            arrival_azimuths=drone_azimuth_level_values, maneuver_angle=maneuver_angle)
        return potential_arrival_env

    @classmethod
    def build_arrival_envelop_object_from_dld_node(cls, internal_node: [DeliveryRequest | DroneLoadingDock]):
        maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        drone_azimuth_level_values = MockSlidesServiceWrapper.get_drone_azimuth_level_values()
        potential_envelop_collection = LoadingDockPotentialEnvelope(internal_node)
        potential_arrival_env = potential_envelop_collection.get_potential_arrival_envelope(
            arrival_azimuths=drone_azimuth_level_values, maneuver_angle=maneuver_angle)
        return potential_arrival_env

    @classmethod
    def from_nodes(cls, operational_nodes: List[OperationalNode | DeliveryRequest | DroneLoadingDock]):
        dr_potential_envelopes = {
            (node, cls.build_arrival_envelop_object_from_dr_node(node))
            for node in [cls.filter_node_by_type(n, DeliveryRequest) for n in operational_nodes if
                         cls.filter_node_by_type(n, DeliveryRequest)]}
        ld_potential_envelopes = {
            (node, cls.build_arrival_envelop_object_from_dld_node(node))
            for node in [cls.filter_node_by_type(n, DroneLoadingDock) for n in operational_nodes if
                         cls.filter_node_by_type(n, DroneLoadingDock)]}
        potential_arrival_envelopes = dr_potential_envelopes.copy()
        potential_arrival_envelopes.update(ld_potential_envelopes)
        return MockPotentialArrivalEnvelopeService(potential_arrival_envelopes=dict(potential_arrival_envelopes))

    @property
    def potential_arrival_envelopes(self) -> Dict[DeliveryRequest | DroneLoadingDock, PotentialEnvelopeCollection]:
        return self._potential_arrival_envelopes

    def get_potential_arrival_envelope(self, node: DeliveryRequest | DroneLoadingDock) -> [PotentialArrivalEnvelope]:
        return self.potential_arrival_envelopes[node]
