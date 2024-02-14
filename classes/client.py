import typing
from classes.limit import Limit


class Client:
    def __init__(self, name: str, limits: list[Limit]):
        self.name: str= name
        self.limits: typing.Dict[str, Limit] = {}
        self.add_limits(limits)
    
    def add_limits(self, limits: list[Limit]):
        for limit in limits:
            self.limits[limit.task.name] = limit