import random
import unittest
from random import Random

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit, ChoicesAngleDistribution
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.delivery_request_envelope import DeliveryRequestPotentialEnvelope
from drop_envelope.slide_service import MockSlidesServiceWrapper
from geometry.distribution.geo_distribution import NormalPointDistribution
from geometry.geo_factory import create_point_2d
from visualization.basic.color import Color
from visualization.basic.pltdrawer2d import create_drawer_2d


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
    azimuths_choices = [Angle(value=value, unit=AngleUnit.DEGREE)
                        for value in [0, 30, 60, 90, 180]]
    return ChoicesAngleDistribution(angles=azimuths_choices)


class BasicDeliveryRequestEnvelope(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.dr_distribution = create_delivery_request_distribution(center_point=create_point_2d(x=0, y=0), sigma_x=20,
                                                                   sigma_y=20)

    def potential_arrival_envelope_plot(self):
        drawer = create_drawer_2d()
        dr = self.dr_distribution.choose_rand(random=Random(),
                                              amount={DeliveryRequest: 1, DeliveryOption: 1, CustomerDelivery: 1,
                                                      PackageDeliveryPlan: 2})
        dr_potential_envelope = DeliveryRequestPotentialEnvelope.from_delivery_request(dr[0])
        potential_drop_envelopes = dr_potential_envelope.potential_drop_envelopes
        legend_names = []
        legend_colors = []
        for i, potential_drop_envelope in enumerate(potential_drop_envelopes):
            envelopes = potential_drop_envelope.envelopes
            drop_direction = potential_drop_envelope.drop_azimuth.get().calc_reverse().to_direction() * 10
            color = random.choice(list(Color))
            legend_names.append("pdp_{}".format(i))
            legend_colors.append(color)
            drawer.add_point2d(potential_drop_envelope.drop_point, facecolor=color, facecolor_alpha=1, edgecolor=color,
                               radius=2)
            drawer.add_arrow2d(tail=potential_drop_envelope.drop_point.add_vector(drop_direction),
                               head=potential_drop_envelope.drop_point, facecolor=color, edgecolor=color)

            for envelope in envelopes:
                drawer.add_polygon2d(envelope.internal_envelope, facecolor=color, facecolor_alpha=1, edgecolor=color)
        maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        potential_arrival_envelope = dr_potential_envelope.get_potential_arrival_envelope(
            get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount),
            maneuver_angle=maneuver_angle)
        drawer.add_point2d(potential_arrival_envelope.get_centroid())
        arrival_envelopes = list(potential_arrival_envelope.potential_envelopes.values())
        for arrival_envelope in arrival_envelopes:
            arrival_direction = arrival_envelope.arrival_azimuth.calc_reverse().to_direction() * 20
            drawer.add_polygon2d(arrival_envelope.maneuver_polygon, edgecolor=Color.Red, facecolor=Color.White,
                                 facecolor_alpha=0)
            drawer.add_arrow2d(tail=arrival_envelope.repr_point.add_vector(arrival_direction),
                               head=arrival_envelope.repr_point, facecolor=Color.Red, edgecolor=Color.Red)
        legend_names.append("maneuvering angle = {}".format(maneuver_angle.degrees))
        legend_colors.append(Color.Red)
        drawer.add_legend(new_labels=legend_names, new_label_colors=legend_colors)
        drawer.draw()

    def test_delivery_request_envelope_creation(self):
        dr = self.dr_distribution.choose_rand(random=Random(10),
                                              amount={DeliveryRequest: 1, DeliveryOption: 1, CustomerDelivery: 1,
                                                      PackageDeliveryPlan: 2})
        dr_potential_envelope = DeliveryRequestPotentialEnvelope.from_delivery_request(dr[0])
        potential_drop_envelopes = dr_potential_envelope.potential_drop_envelopes
        self.assertEqual(len(potential_drop_envelopes), 2)
        self.assertAlmostEqual(dr_potential_envelope.get_centroid().x, 12.735, delta=0.001)
        self.assertAlmostEqual(dr_potential_envelope.get_centroid().y, 14.955, delta=0.001)

    def test_delivery_request_arrival_envelope(self):
        dr = self.dr_distribution.choose_rand(random=Random(12),
                                              amount={DeliveryRequest: 1, DeliveryOption: 1, CustomerDelivery: 1,
                                                      PackageDeliveryPlan: 2})
        dr_potential_envelope = DeliveryRequestPotentialEnvelope.from_delivery_request(dr[0])
        maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        potential_arrival_envelope = dr_potential_envelope.get_potential_arrival_envelope(
            get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount),
            maneuver_angle=maneuver_angle)
        self.assertEqual(len(potential_arrival_envelope.arrival_envelopes), 2)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[0].repr_point.x, -92.147071,
                               delta=0.1)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[0].repr_point.y, -108.24997,
                               delta=0.1)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[1].repr_point.x, -4.52819,
                               delta=0.1)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[1].repr_point.y, -144.542896,
                               delta=0.1)
