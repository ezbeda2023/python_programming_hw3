from __future__ import annotations

from collections.abc import Sequence
from numbers import Real
from types import NotImplementedType
from typing import Callable

from testif import testif


class NVector:

    def __init__(self, *args: Real | Sequence[Real]) -> None:
        elements = list(args[0]) if len(args) == 1 else list(args)
        if any(not isinstance(value, Real) for value in elements):
            raise TypeError("Vector elements must be real numbers")
        self._elements: list[Real] = elements

    def __len__(self) -> int:
        return len(self._elements)

    def __getitem__(self, index: int) -> Real:
        if not isinstance(index, int):
            raise TypeError("Vector indices must be integers")
        return self._elements[index]

    def __setitem__(self, index: int, value: Real) -> None:
        if not isinstance(index, int):
            raise TypeError("Vector indices must be integers")
        if not isinstance(value, Real):
            raise TypeError("Vector elements must be real numbers")
        self._elements[index] = value

    def __str__(self) -> str:
        return f"NVector({self._elements})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NVector) and self._elements == other._elements

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __add__(self, other: object) -> NVector | NotImplementedType:
        if isinstance(other, NVector):
            if len(self) != len(other):
                raise ValueError("Vector dimensions must match")
            return NVector([a + b for a, b in zip(self._elements, other._elements)])
        if isinstance(other, Real):
            return NVector([value + other for value in self._elements])
        return NotImplemented

    def __radd__(self, other: object) -> NVector | NotImplementedType:
        return self.__add__(other)

    def __mul__(self, other: object) -> Real | NotImplementedType:
        if isinstance(other, NVector):
            if len(self) != len(other):
                raise ValueError("Vector dimensions must match")
            return sum(a * b for a, b in zip(self._elements, other._elements))
        if isinstance(other, Real):
            return sum(value * other for value in self._elements)
        return NotImplemented

    def __rmul__(self, other: object) -> Real | NotImplementedType:
        return self.__mul__(other)

    @classmethod
    def zeros(cls, n: int) -> NVector:
        if not isinstance(n, int):
            raise TypeError("Dimension must be an integer")
        if n < 0:
            raise ValueError("Dimension must be nonnegative")
        return cls([0] * n)


def raises(expected: type[Exception], action: Callable[[], object]) -> bool:
    try:
        action()
    except expected:
        return True
    return False


def main() -> None:
    source = [3, 0, 1, -1]
    vector = NVector(source)
    source[0] = 99
    changed = NVector(1, 2, 3, 4)
    changed[3] = 10
    changed[-2] = 5
    result = vector + 10
    checks: list[tuple[str, bool]] = [
        ("list constructor copies input", vector == NVector(3, 0, 1, -1)),
        ("tuple constructor", vector == NVector((3, 0, 1, -1))),
        ("length", len(vector) == 4),
        ("positive indexing", vector[1] == 0),
        ("negative indexing", vector[-2] == 1),
        ("indexed assignment", changed[3] == 10),
        ("negative indexed assignment", changed[-2] == 5),
        ("string representation", str(vector) == "NVector([3, 0, 1, -1])"),
        ("equal vectors", vector == NVector(3, 0, 1, -1)),
        ("unequal elements", vector != NVector(3, 0, 2, -1)),
        ("unequal dimensions", vector != NVector(3, 0)),
        ("different object type", vector != [3, 0, 1, -1]),
        ("vector addition", vector + NVector(1, 2, 3, 4) == NVector(4, 2, 4, 3)),
        ("number addition", result == NVector(13, 10, 11, 9)),
        ("reflected addition", 10 + vector == result),
        ("addition preserves original", vector == NVector(3, 0, 1, -1)),
        ("dot product", vector * NVector(1, 2, 3, 4) == 2),
        ("number multiplication sums products", vector * 10 == 30),
        ("reflected multiplication", 10 * vector == 30),
        ("real-valued elements", NVector([1.5, -0.5]) * 2 == 2.0),
        ("zeros", NVector.zeros(4) == NVector(0, 0, 0, 0)),
        ("empty vector", len(NVector.zeros(0)) == 0),
        ("one-dimensional vector", NVector([7])[0] == 7),
        ("empty product", NVector([]) * NVector([]) == 0),
        ("single scalar rejected", raises(TypeError, lambda: NVector(3))),
        ("non-real element rejected", raises(TypeError, lambda: NVector([1, "x"]))),
        ("out-of-range indexing", raises(IndexError, lambda: vector[4])),
        ("out-of-range negative index", raises(IndexError, lambda: vector[-5])),
        ("out-of-range assignment", raises(IndexError, lambda: vector.__setitem__(4, 2))),
        ("invalid index type", raises(TypeError, lambda: vector[1.5])),
        ("invalid assignment value", raises(TypeError, lambda: vector.__setitem__(0, "x"))),
        ("addition dimension mismatch", raises(ValueError, lambda: vector + NVector([1]))),
        ("product dimension mismatch", raises(ValueError, lambda: vector * NVector([1]))),
        ("unsupported addition", raises(TypeError, lambda: vector + "x")),
        ("unsupported multiplication", raises(TypeError, lambda: vector * "x")),
        ("negative dimension", raises(ValueError, lambda: NVector.zeros(-1))),
        ("noninteger dimension", raises(TypeError, lambda: NVector.zeros(1.5))),
    ]
    passed = sum(bool(testif(ok, name, "passed", "failed")) for name, ok in checks)
    print(f"\n{passed}/{len(checks)} tests passed.")
    if passed != len(checks):
        raise AssertionError("Some NVector tests failed")


if __name__ == "__main__":
    main()
