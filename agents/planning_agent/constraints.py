"""
Constraint definitions for the Planning Agent.
"""

from abc import ABC, abstractmethod
from typing import List
from .models import Task


class Constraint(ABC):
    """
    Base class for all planning constraints.
    """

    @abstractmethod
    def is_satisfied(self, tasks: List[Task]) -> bool:
        pass


class DependencyConstraint(Constraint):
    """
    Ensures task dependencies are present.
    """

    def is_satisfied(self, tasks: List[Task]) -> bool:
        task_ids = {task.id for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    return False

        return True
