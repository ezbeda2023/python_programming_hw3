from __future__ import annotations

import random
from typing import ClassVar

import matplotlib.pyplot as plt


class Island:

    def __init__(
        self, n: int, prey_count: int = 0, predator_count: int = 0,
        count_humans: int = 0,
    ) -> None:
        if n <= 0:
            raise ValueError("Island size must be positive")
        self.grid_size = n
        self.grid: list[list[Animal | int]] = [[0] * n for _ in range(n)]
        self.init_animals(prey_count, predator_count, count_humans)

    def init_animals(
        self, prey_count: int, predator_count: int, count_humans: int
    ) -> None:
        counts = (prey_count, predator_count, count_humans)
        empty = [(x, y) for x in range(self.size())
                 for y in range(self.size()) if self.animal(x, y) == 0]
        if any(count < 0 for count in counts) or sum(counts) > len(empty):
            raise ValueError("Population counts must be nonnegative and fit")
        random.shuffle(empty)
        for species, count in zip((Prey, Predator, Human), counts):
            for _ in range(count):
                x, y = empty.pop()
                self.register(species(self, x, y))

    def animals(self) -> list[Animal]:
        return [cell for column in self.grid for cell in column
                if isinstance(cell, Animal)]

    def clear_all_moved_flags(self) -> None:
        for animal in self.animals():
            animal.clear_moved_flag()

    def size(self) -> int:
        return self.grid_size

    def register(self, animal: Animal) -> None:
        if animal.island is not self:
            raise ValueError("Animal belongs to another island")
        if not (0 <= animal.x < self.size() and 0 <= animal.y < self.size()):
            raise IndexError("Animal coordinates are outside the island")
        if self.animal(animal.x, animal.y) not in (0, animal):
            raise ValueError("Cell is occupied")
        self.grid[animal.x][animal.y] = animal

    def remove(self, animal: Animal) -> None:
        if self.animal(animal.x, animal.y) is animal:
            self.grid[animal.x][animal.y] = 0

    def animal(self, x: int, y: int) -> Animal | int:
        if 0 <= x < self.size() and 0 <= y < self.size():
            return self.grid[x][y]
        return -1

    def __str__(self) -> str:
        return "\n".join(
            " ".join(str(self.grid[x][y]) if self.grid[x][y] else "."
                     for x in range(self.size()))
            for y in range(self.size() - 1, -1, -1)
        )

    def count_prey(self) -> int:
        return sum(isinstance(animal, Prey) for animal in self.animals())

    def count_predators(self) -> int:
        return sum(isinstance(animal, Predator) for animal in self.animals())

    def count_humans(self) -> int:
        return sum(isinstance(animal, Human) for animal in self.animals())

    def step(self) -> None:
        self.clear_all_moved_flags()
        for animal in self.animals():
            if self.animal(animal.x, animal.y) is not animal:
                continue
            if isinstance(animal, (Predator, Human)):
                animal.eat()
            animal.move()
            animal.breed()
            animal.clock_tick()


class Animal:

    breed_time: ClassVar[int] = 3

    def __init__(self, island: Island, x: int = 0, y: int = 0, s: str = "A") -> None:
        self.island = island
        self.x = x
        self.y = y
        self.name = s
        self.moved = False
        self.breed_clock = self.breed_time

    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def __str__(self) -> str:
        return self.name

    def check_grid(self, type_looking_for: type = int) -> tuple[int, int] | int:
        offsets = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0),
                   (-1, -1), (0, -1), (1, -1)]
        for dx, dy in offsets:
            x, y = self.x + dx, self.y + dy
            if 0 <= x < self.island.size() and 0 <= y < self.island.size():
                if type(self.island.animal(x, y)) is type_looking_for:
                    return x, y
        return 0

    def move(self) -> None:
        if not self.moved:
            location = self.check_grid()
            if isinstance(location, tuple):
                self.island.remove(self)
                self.x, self.y = location
                self.island.register(self)
                self.moved = True

    def breed(self) -> None:
        if self.breed_clock <= 0:
            location = self.check_grid()
            if isinstance(location, tuple):
                self.breed_clock = self.breed_time
                self.island.register(type(self)(self.island, *location))

    def clear_moved_flag(self) -> None:
        self.moved = False

    def clock_tick(self) -> None:
        self.breed_clock -= 1

    def consume(self, species: type[Animal]) -> bool:
        if not self.moved:
            location = self.check_grid(species)
            if isinstance(location, tuple):
                victim = self.island.animal(*location)
                if isinstance(victim, Animal):
                    self.island.remove(victim)
                    self.island.remove(self)
                    self.x, self.y = location
                    self.island.register(self)
                    self.moved = True
                    return True
        return False


class Prey(Animal):

    def __init__(self, island: Island, x: int = 0, y: int = 0, s: str = "O") -> None:
        """Initialize a prey animal with the default symbol O."""
        super().__init__(island, x, y, s)


class Predator(Animal):

    breed_time: ClassVar[int] = 6
    starve_time: ClassVar[int] = 3

    def __init__(self, island: Island, x: int = 0, y: int = 0, s: str = "X") -> None:
        super().__init__(island, x, y, s)
        self.starve_clock = self.starve_time

    def clock_tick(self) -> None:
        super().clock_tick()
        self.starve_clock -= 1
        if self.starve_clock <= 0:
            self.island.remove(self)

    def eat(self) -> None:
        if self.consume(Prey):
            self.starve_clock = self.starve_time


class Human(Animal):

    breed_time: ClassVar[int] = 10
    starve_time: ClassVar[int] = 12
    hunt_time: ClassVar[int] = 3

    def __init__(self, island: Island, x: int = 0, y: int = 0, s: str = "H") -> None:
        super().__init__(island, x, y, s)
        self.starve_clock = self.starve_time
        self.hunt_clock = self.hunt_time

    def eat(self) -> None:
        if self.hunt_clock == 1:
            if self.consume(Predator):
                self.starve_clock = self.starve_time

    def clock_tick(self) -> None:
        super().clock_tick()
        self.hunt_clock -= 1
        if self.hunt_clock <= 0:
            self.hunt_clock = self.hunt_time
        self.starve_clock -= 1
        if self.starve_clock <= 0:
            self.island.remove(self)


def main(
    predator_breed_time: int = 6, predator_starve_time: int = 5,
    initial_predators: int = 35, prey_breed_time: int = 3,
    initial_prey: int = 180, size: int = 25, ticks: int = 1000,
    human_hunt_time: int = 2, human_starve_time: int = 20,
    human_breed_time: int = 12, initial_humans: int = 8,
    seed: int = 42, convergence_window: int = 50,
    show_plot: bool = True, verbose: bool = True,
) -> tuple[list[int], list[int], list[int]]:
    times = (predator_breed_time, predator_starve_time, prey_breed_time,
             human_hunt_time, human_starve_time, human_breed_time, ticks)
    if any(not isinstance(value, int) or value <= 0 for value in times):
        raise ValueError("Time parameters must be positive integers")
    if not isinstance(convergence_window, int) or convergence_window < 2:
        raise ValueError("Convergence window must be an integer of at least two")
    Predator.breed_time = predator_breed_time
    Predator.starve_time = predator_starve_time
    Prey.breed_time = prey_breed_time
    Human.hunt_time = human_hunt_time
    Human.starve_time = human_starve_time
    Human.breed_time = human_breed_time
    random.seed(seed)
    isle = Island(size, initial_prey, initial_predators, initial_humans)
    prey_list = [isle.count_prey()]
    predator_list = [isle.count_predators()]
    human_list = [isle.count_humans()]
    if verbose:
        print("Ethan Zbeda | FAU student ID: ezbeda2023")
        print(f"Seed: {seed} | O = prey, X = predator, H = human")
        print("\nInitial island at tick 0:")
        print(isle)
        print("\nTick   Prey   Predators   Humans")
        print(f"{0:4d} {prey_list[0]:6d} {predator_list[0]:11d} {human_list[0]:8d}")
    reason = "Maximum requested time reached"
    for tick in range(1, min(ticks, 1000) + 1):
        isle.step()
        prey_list.append(isle.count_prey())
        predator_list.append(isle.count_predators())
        human_list.append(isle.count_humans())
        if verbose and tick % 25 == 0:
            print(f"{tick:4d} {prey_list[-1]:6d} {predator_list[-1]:11d} {human_list[-1]:8d}")
        histories = (prey_list, predator_list, human_list)
        if len(prey_list) >= convergence_window and all(
            len(set(history[-convergence_window:])) == 1 for history in histories
        ):
            reason = f"All populations constant for {convergence_window} observations"
            break
    final_tick = len(prey_list) - 1
    if verbose:
        print(f"\nFinal island at tick {final_tick}:")
        print(isle)
        print(f"Prey: {prey_list[-1]}, predators: {predator_list[-1]}, humans: {human_list[-1]}")
        print(reason)
    if show_plot:
        fig, ax = plt.subplots(figsize=(10, 6))
        for history, label in zip(
            (prey_list, predator_list, human_list), ("Prey", "Predators", "Humans")
        ):
            ax.plot(range(len(history)), history, label=label)
        ax.set(title=f"Island populations over time (seed {seed})",
               xlabel="Time (ticks)", ylabel="Population")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        plt.show()
    return prey_list, predator_list, human_list


if __name__ == "__main__":
    main()
