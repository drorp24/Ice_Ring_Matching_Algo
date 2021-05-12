from typing import Dict

from ortools.linear_solver import pywraplp
from dataclasses import dataclass
from enum import Enum


class LPParameters(Enum):
    equality_constraints_coefficients = 1
    inequality_constraints_coefficients = 2
    equality_bounds = 3
    inequality_bounds = 4
    objective_coefficients = 5
    num_variables = 6


@dataclass
class LPData:
    data: {LPParameters, list}


class LPSolver:
    solver: pywraplp.Solver = pywraplp.Solver.CreateSolver('GLOP')

    @classmethod
    def set_variables(cls, parameters: LPData, lower_bound=0.0, upper_bound=solver.infinity()) -> {}:
        variables = {j: cls.solver.NumVar(lower_bound, upper_bound, 'x[%i]' % j)
                     for j in range(parameters.data[LPParameters.num_variables])}
        return variables

    @classmethod
    def set_inequalities_constraints(cls, parameters: LPData, variables: {}):
        constraints_coeffs = parameters.data[LPParameters.inequality_constraints_coefficients]
        bounds = parameters.data[LPParameters.inequality_bounds]
        for k in range(len(constraints_coeffs)):
            constraint_expr = [constraints_coeffs[k][l] * variables[l] for l in range(len(variables))]
            cls.solver.Add(sum(constraint_expr) <= bounds[k])

    def set_equalities_constraints(cls, parameters: LPData, variables: {}):
        constraints_coeffs = parameters.data[LPParameters.equality_constraints_coefficients]
        bounds = parameters.data[LPParameters.equality_bounds]
        for k in range(len(constraints_coeffs)):
            constraint_expr = [constraints_coeffs[k][l] * variables[l] for l in range(len(variables))]
            cls.solver.Add(sum(constraint_expr) == bounds[k])

    @classmethod
    def set_objective_coeffs(cls, parameters: LPData, variables: {}):
        objective_coeffs = parameters.data[LPParameters.objective_coefficients]
        for j in range(parameters.data[LPParameters.num_variables]):
            cls.solver.Objective().SetCoefficient(variables[j], objective_coeffs[j])

    @classmethod
    def set_maximization(cls):
        cls.solver.Objective().SetMaximization()

    @classmethod
    def set_minimization(cls):
        cls.solver.Objective().SetMinimization()

    @classmethod
    def solve(cls):
        cls.solver.Solve()


def solve_mip(lp_data: LPData) -> Dict:
    lp_solver = LPSolver()
    variables = lp_solver.set_variables(parameters=lp_data)
    lp_solver.set_equalities_constraints(parameters=lp_data, variables=variables)
    lp_solver.set_inequalities_constraints(parameters=lp_data, variables=variables)
    lp_solver.set_objective_coeffs(parameters=lp_data, variables=variables)
    lp_solver.set_minimization()
    lp_solver.solve()
    return variables
