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


class EnvelopesService:
    def __init__(self, potential_envelopes: dict):
        self._potential_envelopes = potential_envelopes
        self._potential_arrival_envelopes = self.build_arrival_envelopes_from_potential_collection()

    @staticmethod
    def filter_node_by_type(node: [OperationalNode | DeliveryRequest | DroneLoadingDock],
                            node_type: [DeliveryRequest | DroneLoadingDock]):
        if isinstance(node, OperationalNode):
            node = node.internal_node
        if isinstance(node, node_type):
            return node

    def build_arrival_envelopes_from_potential_collection(self):
        maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        drone_azimuth_level_values = MockSlidesServiceWrapper.get_drone_azimuth_level_values()
        dr_arrival_envelopes = {
            (node, self.build_arrival_envelop_object_from_dr_node(node, maneuver_angle, drone_azimuth_level_values))
            for node in [self.filter_node_by_type(n, DeliveryRequest) for n in self._potential_envelopes.keys() if
                         self.filter_node_by_type(n, DeliveryRequest)]}

        ld_arrival_envelopes = {
            (node, self.build_arrival_envelop_object_from_dld_node(node, maneuver_angle, drone_azimuth_level_values))
            for node in [self.filter_node_by_type(n, DroneLoadingDock) for n in self._potential_envelopes.keys() if
                         self.filter_node_by_type(n, DroneLoadingDock)]}

        potential_arrival_envelopes = dr_arrival_envelopes.copy()
        potential_arrival_envelopes.update(ld_arrival_envelopes)
        return dict(potential_arrival_envelopes)

    def build_arrival_envelop_object_from_dr_node(self, internal_node: DeliveryRequest, maneuver_angle: Angle,
                                                  drone_azimuth_level_values):
        potential_envelop_collection = self._potential_envelopes[internal_node]
        potential_arrival_env = potential_envelop_collection.get_potential_arrival_envelope(
            arrival_azimuths=drone_azimuth_level_values, maneuver_angle=maneuver_angle)
        return potential_arrival_env

    def build_arrival_envelop_object_from_dld_node(self, internal_node: DroneLoadingDock, maneuver_angle: Angle,
                                                   drone_azimuth_level_values):
        potential_envelop_collection = self._potential_envelopes[internal_node]
        potential_arrival_env = potential_envelop_collection.get_potential_arrival_envelope(
            arrival_azimuths=drone_azimuth_level_values, maneuver_angle=maneuver_angle)
        return potential_arrival_env

    @classmethod
    def from_nodes(cls, operational_nodes: List[OperationalNode | DeliveryRequest | DroneLoadingDock]):
        dr_potential_envelopes = {
            (node, DeliveryRequestPotentialEnvelope.from_delivery_request(node))
            for node in [cls.filter_node_by_type(n, DeliveryRequest) for n in operational_nodes if
                         cls.filter_node_by_type(n, DeliveryRequest)]}
        ld_potential_envelopes = {
            (node, LoadingDockPotentialEnvelope(node))
            for node in [cls.filter_node_by_type(n, DroneLoadingDock) for n in operational_nodes if
                         cls.filter_node_by_type(n, DroneLoadingDock)]}

        potential_envelopes = dr_potential_envelopes.copy()
        potential_envelopes.update(ld_potential_envelopes)
        return EnvelopesService(potential_envelopes=dict(potential_envelopes))

    @property
    def potential_envelopes(self) -> Dict[DeliveryRequest | DroneLoadingDock, PotentialEnvelopeCollection]:
        return self._potential_envelopes

    @property
    def potential_arrival_envelopes(self) -> Dict[DeliveryRequest | DroneLoadingDock, PotentialEnvelopeCollection]:
        return self._potential_arrival_envelopes

    def get_potential_envelope(self, node: DeliveryRequest | DroneLoadingDock) -> [PotentialArrivalEnvelope]:
        return self.potential_envelopes[node]

    def get_potential_arrival_envelope(self, node: DeliveryRequest | DroneLoadingDock) -> [PotentialArrivalEnvelope]:
        return self.potential_arrival_envelopes[node]
