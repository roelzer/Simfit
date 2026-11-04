from .. import config
from .base import DataSource


def get_source() -> DataSource:
    if config.SOURCE == "garmin":
        from .garmin import GarminCloudSource

        return GarminCloudSource()
    from .demo import DemoSource

    return DemoSource()
