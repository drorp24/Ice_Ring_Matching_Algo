from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.temporal import TimeWindowExtension
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer


def generate_matched_request_bar_colors() -> [Color]:
    matched_request_bar_colors = list(Color)
    matched_request_bar_colors = sorted(matched_request_bar_colors,
                                        key=lambda color: color.name)
    matched_request_bar_colors.remove(Color.White)
    matched_request_bar_colors.remove(Color.Red)
    matched_request_bar_colors.remove(Color.Grey)
    matched_request_bar_colors.remove(Color.Orange)
    return matched_request_bar_colors


UNMATCHED_ROW_NUMBER = 1
MATCHED_REQUEST_BAR_COLORS = generate_matched_request_bar_colors()
OPERATING_TIME_WINDOW_COLOR = Color.Red
ROW_BACKGROUND_ALPHA = 0.5
DISPLAY_NAME_CHAR_AMOUNT = 10


def add_delivery_board_with_row_per_delivering_drones(drawer: GanttDrawer, board: DroneDeliveryBoard,
                                                      draw_unmatched=True):
    delivering_drones_list = list(set(delivery.delivering_drones for delivery in board.drone_deliveries))
    _set_row_color_per_dock(delivering_drones_list, drawer)
    for i, delivery in enumerate(board.drone_deliveries):
        delivery_row = delivering_drones_list.index(delivery.delivering_drones) + 1 + UNMATCHED_ROW_NUMBER
        max_inner_rows = max(
            delivery.delivering_drones.drone_formation.get_package_type_amount_map().get_package_type_amounts())
        if len(delivery.matched_requests) == 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_dock.delivery_time_window.since,
                                            delivery.end_drone_loading_dock.delivery_time_window.since),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request_index, request in enumerate(delivery.matched_requests):
            bar_color = Color.White
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_time_window.since,
                side_text=str(request.delivery_request.priority),
                color=bar_color,
                inner_row=request_index,
                max_inner_rows=max_inner_rows
            )

    if draw_unmatched:
        _add_unmatched_requests(board, drawer)


def _set_row_color_per_dock(delivering_drones_list, drawer):
    docks_colors = {}
    for i, delivering_drones in enumerate(delivering_drones_list):
        row_number = i + 1 + UNMATCHED_ROW_NUMBER
        row_color = MATCHED_REQUEST_BAR_COLORS[(_convert_id_to_int(delivering_drones.start_loading_dock.id)
                                                + 20)
                                               % len(MATCHED_REQUEST_BAR_COLORS)]
        drawer.set_row_color(row_number, row_color, ROW_BACKGROUND_ALPHA)
        docks_colors[delivering_drones.start_loading_dock.id] = row_color
    drawer.add_legend([dock_id.display_name(DISPLAY_NAME_CHAR_AMOUNT)
                       for dock_id in list(docks_colors.keys())], list(docks_colors.values()),
                      ROW_BACKGROUND_ALPHA, title="Docks")


def _convert_id_to_int(id):
    return int("".join([str(ord(c)) for c in str(id.uuid)]))


def _add_unmatched_requests(board, drawer):
    num_of_unmatched_delivery_requests = len(board.unmatched_delivery_requests)
    max_inner_rows = num_of_unmatched_delivery_requests if num_of_unmatched_delivery_requests > 3 else 3
    for i, unmatched in enumerate(board.unmatched_delivery_requests):
        drawer.add_bar(
            row=UNMATCHED_ROW_NUMBER,
            time_window=unmatched.delivery_request.time_window,
            name="unmatched" + str(i),
            time_mark=None,
            side_text=str(unmatched.delivery_request.priority),
            color=Color.Red,
            inner_row=i,
            max_inner_rows=max_inner_rows
        )


def add_delivery_board_with_row_per_drone_delivery(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_unmatched=True):
    for i, delivery in enumerate(board.drone_deliveries):
        delivery_row = i + 1 + UNMATCHED_ROW_NUMBER
        max_inner_rows = max(

            delivery.delivering_drones.drone_formation.get_package_type_amount_map().get_package_type_amounts())
        if len(delivery.matched_requests) == 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_dock.delivery_time_window.since,
                                            delivery.end_drone_loading_dock.delivery_time_window.since),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request_index, request in enumerate(delivery.matched_requests):
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_time_window.since,
                side_text=str(request.delivery_request.priority),
                color=MATCHED_REQUEST_BAR_COLORS[request.graph_index % len(MATCHED_REQUEST_BAR_COLORS)],
                inner_row=request_index,
                max_inner_rows=max_inner_rows
            )

    if draw_unmatched:
        _add_unmatched_requests(board, drawer)
