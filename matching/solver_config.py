from enum import Enum

from common.entities.base_entities.base_entity import JsonableBaseEntity


class SolverVendor(JsonableBaseEntity, Enum):
    OR_TOOLS = "or_tools"

    @classmethod
    def dict_to_obj(cls, dict_input):
        split_vendor = dict_input['__enum__'].split('.')
        assert (split_vendor[0] == 'SolverVendor')
        return SolverVendor[split_vendor[1]]

    def __dict__(self):
        return {'__enum__': str(self)}


class SolverConfig(JsonableBaseEntity):

    def __init__(self, vendor: SolverVendor, first_solution_strategy: str, local_search_strategy: str,
                 timeout_sec: int):
        self._vendor = vendor
        self._first_solution_strategy = first_solution_strategy
        self._local_search_strategy = local_search_strategy
        self._timeout_sec = timeout_sec

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return SolverConfig(
            vendor=SolverVendor.dict_to_obj(dict_input["vendor"]),
            first_solution_strategy=dict_input["first_solution_strategy"],
            local_search_strategy=dict_input["local_search_strategy"],
            timeout_sec=dict_input["timeout_sec"])

    @property
    def vendor(self) -> SolverVendor:
        return self._vendor

    @property
    def first_solution_strategy(self) -> str:
        return self._first_solution_strategy

    @property
    def local_search_strategy(self) -> str:
        return self._local_search_strategy

    @property
    def timeout_sec(self) -> int:
        return self._timeout_sec

    def get_first_solution_strategy_as_int(self) -> int:
        raise NotImplementedError()

    def get_local_search_strategy_as_int(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other):
        return (self.vendor == other.vendor) and \
               (self.first_solution_strategy == other.first_solution_strategy) and \
               (self.local_search_strategy == other.local_search_strategy) and \
               (self.timeout_sec == other.timeout_sec)
