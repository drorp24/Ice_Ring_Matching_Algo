from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.basic.pltgantt_drawer import create_gantt_drawer
from visualization.operational import operational_drawer2d, operational_gantt_drawer


def draw_matched_scenario(delivery_board, graph, supplier_category, map_image):
    dr_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
    operational_drawer2d.add_operational_graph(dr_drawer, graph, draw_internal=True,
                                               draw_edges=False)
    dr_drawer.draw(False)
    board_map_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
    operational_drawer2d.add_delivery_board(board_map_drawer, delivery_board, draw_unmatched=True)
    board_map_drawer.draw(False)
    row_names = ["Unmatched Out"] + \
                ["[" + str(delivery.drone_formation.drone_formation_type.name) + "] * " +
                 str(delivery.drone_formation.drone_package_configuration.package_type_map)
                 for delivery in delivery_board.drone_deliveries]
    board_gantt_drawer = create_gantt_drawer(zero_time=supplier_category.zero_time,
                                             hours_period=24,
                                             row_names=row_names,
                                             rows_title='Formation Type x Package Type Amounts'
                                             )
    operational_gantt_drawer.add_delivery_board(board_gantt_drawer, delivery_board, True)
    board_gantt_drawer.draw(True)
