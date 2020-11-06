from datetime import timedelta, date, time

from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOptionDistribution
from common.entities.delivery_request import PriorityDistribution
from common.entities.package import PackageDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.entities.temporal import TimeWindowDistribution, DateTimeExtension, TimeDeltaExtension, TimeWindowExtension, \
    TimeDeltaDistribution, DateTimeDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.geo_distribution import PointDistribution

# --- base entity default distributions --

DEFAULT_DROP_POINT_DISTRIB = PointDistribution(30, 40, 35, 45)
DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))
DEFAULT_PITCH_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))
DEFAULT_PACKAGE_DISTRIB = PackageDistribution()
DEFAULT_PDP_DISTRIB = PackageDeliveryPlanDistribution(DEFAULT_DROP_POINT_DISTRIB,
                                                       DEFAULT_AZI_DISTRIB,
                                                       DEFAULT_PITCH_DISTRIB,
                                                       DEFAULT_PACKAGE_DISTRIB)
DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution([DEFAULT_PDP_DISTRIB])
DEFAULT_DO_DISTRIB = DeliveryOptionDistribution([DEFAULT_CD_DISTRIB])


# --- date time default distributions ---

DEFAULT_DATE_TIME_MORNING = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
DEFAULT_DATE_TIME_NIGHT = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))
DEFAULT_TIME_DELTA_DISTRIB = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3)),
                                                    TimeDeltaExtension(timedelta(minutes=30))])
DEFAULT_DT_OPTIONS = [DEFAULT_DATE_TIME_MORNING, DEFAULT_DATE_TIME_NIGHT]
DEFAULT_TW_DISTRIB = TimeWindowDistribution(DateTimeDistribution(DEFAULT_DT_OPTIONS), DEFAULT_TIME_DELTA_DISTRIB)

DEFAULT_TIME_WINDOW = TimeWindowExtension(DEFAULT_DATE_TIME_MORNING, DEFAULT_DATE_TIME_NIGHT)
DEFAULT_PRIORITY_DISTRIB = PriorityDistribution(list(range(0, 100, 3)))