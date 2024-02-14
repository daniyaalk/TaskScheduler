
import time
from classes.client import Client
from classes.flow import Flow
from state.manager import init, refresh
from state.state import State
from threading import Thread


state: State = State()

def is_execution_allowed(client: Client, flow: Flow) -> bool:
    allow: bool = True

    for task in flow.tasks:
        state.increment_usage_counter(client.name, task.name)
        if state.is_quota_exhausted(client.name, task):
            # Setting value as false instead of returning
            # So that capacity planning can be done for all tasks in a flow.
            allow = False

    return allow


def schedule_state_init() -> None:
    init(state)
    # Scheduled thread that refreshes the state every second, will be a more elegant solution like cron based scheduler in a production system.
    while True:
        # refresh(state)
        time.sleep(1)


if __name__ == "__main__":
    
    Thread(target=schedule_state_init).start()

    while not state.initialized:
        pass

    fl01: Flow = state.flows["fl01"]
    fl02: Flow = state.flows["fl02"]
    cl01: Client = state.clients["cl01"]
    cl02: Client = state.clients["cl02"]

    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl02, fl02))
    print(is_execution_allowed(cl02, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    refresh(state)
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    refresh(state)
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
    print(is_execution_allowed(cl01, fl01))
