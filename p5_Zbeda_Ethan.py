from __future__ import annotations

import argparse
from time import perf_counter
import turtle
from typing import TypeVar

from testif import testif


X = TypeVar("X")
Y = TypeVar("Y")


def _draw_branch(level: int, length: float, bend: float) -> None:
    position = turtle.position()
    heading = turtle.heading()
    turtle.forward(length)
    tip = turtle.position()
    if level == 0:
        turtle.backward(length)
        return
    turtle.left(48)
    _draw_branch(level - 1, length * 0.43, bend)
    turtle.setheading(heading - 48)
    _draw_branch(level - 1, length * 0.43, bend)
    turtle.setheading(heading + bend)
    _draw_branch(level - 1, length * 0.68, bend)
    turtle.penup()
    turtle.goto(tip)
    turtle.goto(position)
    turtle.setheading(heading)
    turtle.pendown()


def _draw_leaf(level: int, length: float, curved: bool) -> None:
    if type(level) is not int:
        raise TypeError("Recursion level must be an integer")
    if level < 1:
        raise ValueError("Recursion level must be positive")
    if isinstance(length, bool) or not isinstance(length, (int, float)):
        raise TypeError("Stem length must be a number")
    if not 0 < length < float("inf"):
        raise ValueError("Stem length must be positive and finite")
    screen = turtle.Screen()
    screen.setup(900, 850)
    screen.title("Ethan Zbeda | ezbeda2023 | " + ("Curved leaf" if curved else "Straight leaf"))
    screen.bgcolor("ivory")
    screen.tracer(0)
    turtle.reset()
    turtle.hideturtle()
    turtle.speed(0)
    turtle.delay(0)
    turtle.pencolor("forest green")
    turtle.pensize(1)
    extent = length / (1 - 0.68)
    screen.setworldcoordinates(-extent * 0.85, -extent * 0.1,
                               extent * 0.85, extent * 1.15)
    turtle.penup()
    turtle.goto(0, 0)
    turtle.setheading(90)
    turtle.pendown()
    _draw_branch(level, length, 12.0 if curved else 0.0)
    screen.update()


def draw_leaf_straight(level: int, length: float) -> None:
    _draw_leaf(level, length, False)


def draw_leaf_curved(level: int, length: float) -> None:
    _draw_leaf(level, length, True)


def strB(n: int, base: int = 10) -> str:
    if type(n) is not int or type(base) is not int:
        raise TypeError("Number and base must be integers")
    if n < 0 or not 2 <= base <= 26:
        raise ValueError("Require n >= 0 and 2 <= base <= 26")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < base:
        return digits[n]
    return strB(n // base, base) + digits[n % base]


def Cnk_m(n: int, k: int) -> int:
    if type(n) is not int or type(k) is not int:
        raise TypeError("n and k must be integers")
    if not 0 <= k <= n:
        raise ValueError("Require 0 <= k <= n")
    memo: dict[tuple[int, int], int] = {}

    def choose(row: int, column: int) -> int:
        """Recursively evaluate a valid Pascal entry, caching each computed value."""
        key = row, column
        if key not in memo:
            if column == 0 or column == row:
                memo[key] = 1
            else:
                memo[key] = choose(row - 1, column - 1) + choose(row - 1, column)
        return memo[key]

    return choose(n, min(k, n - k))


def run_Cnk(n: int = 100, k: int = 50) -> int:
    start = perf_counter()
    result = Cnk_m(n, k)
    print(f"Cnk_m({n}, {k}) = {result}")
    print(f"Elapsed time: {perf_counter() - start:.6f} seconds")
    return result


def make_pairs(
    seq1: list[X], seq2: list[Y], accumulator: list[tuple[X, Y]] | None = None,
    index: int = 0,
) -> list[tuple[X, Y]]:
    if not isinstance(seq1, list) or not isinstance(seq2, list):
        raise TypeError("Both sequences must be lists")
    if type(index) is not int:
        raise TypeError("Index must be an integer")
    if index < 0:
        raise ValueError("Index must be nonnegative")
    if accumulator is None:
        accumulator = []
    elif not isinstance(accumulator, list):
        raise TypeError("Accumulator must be a list")
    if index >= min(len(seq1), len(seq2)):
        return accumulator
    accumulator.append((seq1[index], seq2[index]))
    return make_pairs(seq1, seq2, accumulator, index + 1)


def test_strB() -> bool:
    results = [
        testif(strB(0, 26) == "0", "strB zero"),
        testif(strB(42, 2) == "101010", "strB binary"),
        testif(strB(255, 16) == "FF", "strB hexadecimal"),
        testif(strB(675, 26) == "PP", "strB base 26"),
    ]
    return all(results)


def test_Cnk_m() -> bool:
    results = [
        testif(Cnk_m(0, 0) == 1, "Cnk_m empty selection"),
        testif(Cnk_m(12, 12) == 1, "Cnk_m full selection"),
        testif(Cnk_m(30, 12) == 86493225, "Cnk_m 30 choose 12"),
        testif(Cnk_m(100, 50) == 100891344545564193334812497256,
               "Cnk_m 100 choose 50"),
    ]
    return all(results)


def test_make_pairs() -> bool:
    results = [
        testif(make_pairs([1, 2], ["a", "b"]) == [(1, "a"), (2, "b")],
               "make_pairs matching lengths"),
        testif(make_pairs([1, 2], [3]) == [(1, 3)], "make_pairs shorter second"),
        testif(make_pairs([1], [3, 4]) == [(1, 3)], "make_pairs shorter first"),
        testif(make_pairs([], [1]) == [], "make_pairs empty first"),
        testif(make_pairs([1], []) == [], "make_pairs empty second"),
    ]
    return all(results)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leaf", choices=("straight", "curved"), default="straight")
    parser.add_argument("--no-draw", action="store_true")
    args = parser.parse_args()
    print("Ethan Zbeda | FAU student ID: ezbeda2023")
    print("\nUnit tests:")
    results = (test_strB(), test_Cnk_m(), test_make_pairs())
    if not all(results):
        raise AssertionError("Some recursive function tests failed")
    print("All 13 unit tests passed.")
    print("\nBase conversion examples:")
    print(f"strB(42, 2) = {strB(42, 2)!r}")
    print(f"strB(2026, 16) = {strB(2026, 16)!r}")
    print(f"strB(675, 26) = {strB(675, 26)!r}")
    print("\nMemoized combinations:")
    run_Cnk(100, 50)
    run_Cnk(200, 80)
    print("\nMatching pairs:")
    print(make_pairs(["Ethan", "Alex", "Morgan"], [90, 85]))
    if not args.no_draw:
        if args.leaf == "straight":
            draw_leaf_straight(6, 120)
        else:
            draw_leaf_curved(6, 120)
        turtle.done()


if __name__ == "__main__":
    main()
