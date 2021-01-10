from drop_envelope.abstract_envelope_collections import PotentialEnvelopeCollection


def calc_cost(potential_envelope_collection_1: PotentialEnvelopeCollection,
              potential_envelope_collection_2: PotentialEnvelopeCollection) -> int:
    shapeable_collection_1 = potential_envelope_collection_1.get_potential_envelopes()
    shapeable_collection_2 = potential_envelope_collection_2.get_potential_envelopes()
    if (len(shapeable_collection_1) == 1 and len(shapeable_collection_1.get_shapeable_collection()) == 1) \
            or (len(shapeable_collection_2) == 1 and len(shapeable_collection_2.get_shapeable_collection())) == 1:
        return int(potential_envelope_collection_1.get_centroid().calc_distance_to_point(
                potential_envelope_collection_2.get_centroid()))
