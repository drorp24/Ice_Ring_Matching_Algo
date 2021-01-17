from typing import Dict

from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverConfig, SolverVendor


def create_solver_config(solver_config: Dict) -> SolverConfig:
    solver_vendor = SolverVendor.dict_to_obj(solver_config["vendor"])
    if solver_vendor == SolverVendor.OR_TOOLS:
        return ORToolsSolverConfig.dict_to_obj(solver_config)

    raise TypeError(f"Solver vendor do not supported")
