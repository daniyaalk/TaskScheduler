
import typing
from classes.client import Client
from classes.flow import Flow
from classes.limit import Limit
from classes.task import Task
from state.state import State


def init(state: State):

    t01: Task = Task("t01", 10)
    t02: Task = Task("t02", 10)
    t03: Task = Task("t03", 10)

    fl01: Flow = Flow("fl01", [t01, t03])
    fl02: Flow = Flow("fl02", [t01, t02])
    fl03: Flow = Flow("fl02", [t02, t03])
    flows: list[Flow] = [fl01, fl02, fl03]

    for flow in flows:
        state.set_flow(flow)

    # taskName_limit
    t01_1tps: Limit = Limit(t01, 1)
    t01_2tps: Limit = Limit(t01, 2)
    t02_1tps: Limit = Limit(t02, 1)
    t03_1tps: Limit = Limit(t03, 1)

    cl01: Client = Client("cl01", [t01_1tps, t02_1tps, t03_1tps])
    cl02: Client = Client("cl02", [t01_2tps, t02_1tps, t03_1tps])
    clients: list[Client] = [cl01, cl02]

    for client in clients:
        state.set_client(client)
    
    state.initialized = True


def refresh(state: State) -> None:
    
    tasks: set[Task] = set()

    for flow in state.flows.values():
        for task in flow.tasks:
            tasks.add(task)
    
    for task in tasks:
        refresh_task_quotas(task, state)
    
    # Refresh counters in state:
    state.reset_counter()


def refresh_task_quotas(task: Task, state: State) -> None:

    task_name = task.name
    hit_count = state.get_counter()
    client_wise_usage: typing.Dict[str, int] = {}
    new_allocations: typing.Dict[str, int] = {}
    total_invocations = 0 # Number of times a task was invoked by any client
    total_clients_count = 0 # Number of clients that have invoked this task

    # Get usages of each client for given task
    for client in hit_count:
        if task_name in hit_count[client]:
            if client in client_wise_usage:
                client_wise_usage[client] += hit_count[client][task_name]
            else:
                client_wise_usage[client] = hit_count[client][task_name]
            
            total_invocations += client_wise_usage[client]
            total_clients_count += 1
    
    client_wise_invocation_list: list[tuple[int, str]] = [(count, name) for name, count in client_wise_usage.items()]
    client_wise_invocation_list.sort()
    # At this point we have a list like follows: [(2, CL01), (5, CL03), (10, CL02).... (requested_capacity, client_name)]

    available_capacity = task.max_allowed_invocatons
    remaining_clients_count = total_clients_count

    # First, we check the demand from each client. If the demand is low enough that it can be honoured for all clients,
    # it is allocated for all clients.
    while (len(client_wise_invocation_list) > 0 and 
           client_wise_invocation_list[0][0]*remaining_clients_count < available_capacity):
        
        for client in client_wise_usage:

            if client in new_allocations and new_allocations[client] == client_wise_usage[client]:
                # Skip increment if this client already has required allocation
                continue

            if client in new_allocations:
                new_allocations[client] += client_wise_invocation_list[0][0]
            else:
                new_allocations[client] = client_wise_invocation_list[0][0]
        
        client_wise_invocation_list.pop(0)
        remaining_clients_count-=1
    
    if remaining_clients_count != 0:
        # Once the minimum demand is no longer low enough that it can be honoured for all clients, the remaining 
        # capacity can be allocated equally to all remaining clients with unfulfilled demands.
        remaining_capacity_per_client = available_capacity // remaining_clients_count
        for client in client_wise_usage:
            if client in new_allocations and new_allocations[client] == client_wise_usage[client]:
                # Demand already fulfilled, continue to next client
                continue
            
            if client in new_allocations:
                new_allocations[client] += remaining_capacity_per_client
            else:
                new_allocations[client] = remaining_capacity_per_client
    
    # Reset state with new limits
    for client in new_allocations:
        state.set_limit(state.clients[client], Limit(task, new_allocations[client]))
    



