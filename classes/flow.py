from classes.task import Task

class Flow:

    def __init__(self, name: str, tasks: list[Task]):
        self.name = name # Unique name of current flow
        self.tasks = tasks # Ordered list of tasks that are to be invoked in current flow.