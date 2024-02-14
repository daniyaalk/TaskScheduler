import typing
from classes.client import Client
from classes.flow import Flow
from classes.limit import Limit
from classes.task import Task

MAX_LIMIT: int = 100_000

class State:
    
    def __init__(self):
        self.initialized: bool = False
        self.flows: typing.Dict[str, Flow] = {}
        self._clientLimits: typing.Dict[str, typing.Dict[str, int]] = {} # {"client_name": {"task_name": limit}}
        self.clients: typing.Dict[str, Client] = {}
        self._counter: typing.Dict[str, typing.Dict[str, int]] = {} # {"client_name": {"task_name": invocation_count}}
        pass

    
    def set_flow(self, flow: Flow) -> None:
        self.flows[flow.name] = flow
        pass


    def set_limit(self, client: Client, limit: Limit) -> None:
        if client.name not in self._clientLimits:
            self._clientLimits[client.name] = {}
        
        self._clientLimits[client.name][limit.task.name] = limit.max_count
        pass


    def set_client(self, client: Client) -> None:
        self.clients[client.name] = client

        for limit in client.limits.values():
            self.set_limit(client, limit)
        pass
    

    def get_used_quota_for_client(self, client_name: str, task_name: str) -> int:
        self._initialize_first_quota_fetch(client_name, task_name)
        return self._counter[client_name][task_name]
    
    def get_used_quota_for_task(self, task_name: str) -> int:
        ret = 0
        for client in self._counter:
            if task_name in self._counter[client]:
                ret += self._counter[client][task_name]
        return ret
    

    def increment_usage_counter(self, client_name: str, task_name: str) -> None:
        self._initialize_first_quota_fetch(client_name, task_name)
        self._counter[client_name][task_name] += 1
        pass


    def get_configured_limit(self, client_name: str, task_name: str) -> int:
        """
            Get the current limit for a particular client and task. If it is not defined beforehand, return MAX_LIMIT.
        """

        if client_name not in self._clientLimits or task_name not in self._clientLimits[client_name]:
            return MAX_LIMIT
        
        return self._clientLimits[client_name][task_name]


    def is_quota_exhausted(self, client_name: str, task: Task) -> bool:
        task_name: str = task.name
        client_quota_exhausted: bool = self.get_used_quota_for_client(client_name, task_name) > self.get_configured_limit(client_name, task_name)
        task_quota_exhausted: bool = self.get_used_quota_for_task(task_name) > task.max_allowed_invocatons
        
        return client_quota_exhausted or task_quota_exhausted


    def _initialize_first_quota_fetch(self, client_name: str, task_name: str) -> None:
        if client_name not in self._counter:
            self._counter[client_name] = {task_name: 0}
        
        client_usage = self._counter[client_name]
        if task_name not in client_usage:
            client_usage[task_name] = 0
        pass

    def get_counter(self) -> typing.Dict[str, typing.Dict[str, int]]:
        return self._counter;

    def reset_counter(self) -> None:
        self._counter = {}

    def get_client_limits(self) ->  typing.Dict[str, typing.Dict[str, int]]:
        return self._clientLimits
    
    
        


