"""Admission checks stop new work; they cannot retroactively undo a remote call."""

from dataclasses import dataclass
from time import monotonic


@dataclass
class Budget:
    remaining_steps: int
    remaining_units: int
    deadline: float

    def reserve(self, upper_bound_units: int) -> None:
        if upper_bound_units < 0:
            raise ValueError("Reservation cannot be negative")
        if monotonic() >= self.deadline or self.remaining_steps <= 0:
            raise TimeoutError("Runtime budget exhausted")
        if upper_bound_units > self.remaining_units:
            raise ValueError("Cost reservation exceeds budget")
        self.remaining_steps -= 1
        self.remaining_units -= upper_bound_units


# Use a conservative call bound, then reconcile usage. Deadline checks need cancellable adapters.
