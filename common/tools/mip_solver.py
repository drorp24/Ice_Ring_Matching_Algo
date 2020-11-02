from ortools.linear_solver import pywraplp
from dataclasses import dataclass
from enum import Enum


class MIPParameters(Enum):
    equality_constraints_coeffs = 1
    inequality_constraints_coeffs = 2
    equality_bounds = 3
    inequality_bounds = 4
    objective_coeffs = 5
    num_variables = 6


@dataclass
class MIPData:
    data: {MIPParameters, list}


class MIPSolver:
    solver: pywraplp.Solver = pywraplp.Solver.CreateSolver('SCIP')

    @classmethod
    def set_variables(cls, parameters: MIPData, lower_bound=0.0, upper_bound=solver.infinity()) -> {}:
        variables = {j: cls.solver.IntVar(lower_bound, upper_bound, 'x[%i]' % j)
                     for j in range(parameters.data[MIPParameters.num_variables])}
        return variables

    @classmethod
    def set_inequalities_constraints(cls, parameters: MIPData, variables: {}):
        constraints_coeffs = parameters.data[MIPParameters.inequality_constraints_coeffs]
        bounds = parameters.data[MIPParameters.inequality_bounds]
        for k in range(len(constraints_coeffs)):
            constraint_expr = [constraints_coeffs[k][l] * variables[l] for l in range(len(variables))]
            cls.solver.Add(sum(constraint_expr) <= bounds[k])

    def set_equalities_constraints(cls, parameters: MIPData, variables: {}):
        constraints_coeffs = parameters.data[MIPParameters.equality_constraints_coeffs]
        bounds = parameters.data[MIPParameters.equality_bounds]
        for k in range(len(constraints_coeffs)):
            constraint_expr = [constraints_coeffs[k][l] * variables[l] for l in range(len(variables))]
            cls.solver.Add(sum(constraint_expr) == bounds[k])

    @classmethod
    def set_objective_coeffs(cls, parameters: MIPData, variables: {}):
        objective_coeffs = parameters.data[MIPParameters.objective_coeffs]
        for j in range(parameters.data[MIPParameters.num_variables]):
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
