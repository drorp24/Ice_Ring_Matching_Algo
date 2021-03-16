import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from drop_envelope.arrival_envelope_service import MockPotentialEnvelopeService
from drop_envelope.delivery_request_envelope import DeliveryRequestPotentialEnvelope
from drop_envelope.loading_dock_envelope import LoadingDockPotentialEnvelope


class BasicArrivalEnvelopeService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100),
                                                                          amount={DeliveryRequest: 10})
        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=3)

    def test_arrival_envelope_service_creation(self):
        dr_envelope = {dr: DeliveryRequestPotentialEnvelope.from_delivery_request(dr) for dr in self.dr_dataset_random}
        dld_envelope = {dld: LoadingDockPotentialEnvelope(drone_loading_dock=dld) for dld in self.dld_dataset_random}
        envelopes = dict(list(dr_envelope.items()) + list(dld_envelope.items()))
        service = MockPotentialEnvelopeService(envelopes)
        self.assertEqual(len(service.potential_envelopes), 13)

