import uuid
from random import Random
from typing import List

from common.entities.base_entities.entity_id import EntityID
from common.entities.distribution.distribution import UniformChoiceDistribution


class EntityIDDistribution(UniformChoiceDistribution):
    def __init__(self, entity_id_list: List[EntityID]):
        super().__init__(entity_id_list)

    def choose_rand(self, random: Random, amount: int = 1) -> List[EntityID]:
        return super().choose_rand(random, amount)

    def distribution_class(self) -> type:
        return EntityID

DEFAULT_SINGLE_ID_DISTRIB = EntityIDDistribution([EntityID(uuid.uuid4()), EntityID(uuid.uuid4())])
