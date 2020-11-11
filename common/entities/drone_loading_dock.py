from common.entities.drone import PlatformType
from common.entities.drone_loading_station import LoadingStations
from time_window import TimeWindow


class DroneLoadingDock:

    def __init__(self, drone_loading_station: LoadingStations, platform_type: PlatformType, time_window: TimeWindow):
        self.drone_loading_station = drone_loading_station
        self.platform_type = platform_type
        self.time_window = time_window

    @property
    def drone_loading_station(self) -> LoadingStations:
        return self.drone_loading_station

    @property
    def platform_type(self) -> PlatformType:
        return self.platform_type

    @property
    def time_window(self) -> TimeWindow:
        return self.time_window
