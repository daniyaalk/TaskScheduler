class Task:

    def __init__(self, name: str, max_allowed_invocations: int):
        self.name: str = name
        self.max_allowed_invocatons: int = max_allowed_invocations;