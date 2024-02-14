from classes.task import Task


class Limit:

    def __init__(self, task: Task, max_count: int):
        self.max_count: int = max_count # Max number of invocations allowed per time slice
        self.task: Task = task # Task for which this limit is applicable