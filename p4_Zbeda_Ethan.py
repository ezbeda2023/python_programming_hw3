from __future__ import annotations

import os
from pathlib import Path
import tempfile

from testif import testif


def _read_text(filename: str) -> str:
    with open(filename, "r", encoding="utf-8", newline="") as source:
        return source.read()


def _write_text(filename: str, text: str) -> None:
    path = Path(filename).absolute()
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            delete=False,
        ) as output:
            temporary = Path(output.name)
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _validate_search(search_str: str) -> None:
    if not isinstance(search_str, str):
        raise TypeError("Search text must be a string")
    if not search_str:
        raise ValueError("Search text must not be empty")


def _positions(text: str, search_str: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while True:
        index = text.find(search_str, start)
        if index == -1:
            return positions
        positions.append(index)
        start = index + 1


def ed_read(filename: str, from_: int = 0, to: int = -1) -> str:
    if type(from_) is not int or type(to) is not int:
        raise TypeError("Read bounds must be integers")
    text = _read_text(filename)
    end = len(text) if to == -1 else to
    if not 0 <= from_ <= end <= len(text):
        raise IndexError(f"Invalid read range [{from_}, {end}) for {len(text)} characters")
    return text[from_:end]


def ed_find(filename: str, search_str: str) -> list[int]:
    _validate_search(search_str)
    return _positions(_read_text(filename), search_str)


def ed_replace(
    filename: str, search_str: str, replace_with: str, occurrence: int = -1
) -> int:
    _validate_search(search_str)
    if not isinstance(replace_with, str):
        raise TypeError("Replacement must be a string")
    if type(occurrence) is not int:
        raise TypeError("Occurrence must be an integer")
    if occurrence < -1:
        raise ValueError("Occurrence must be -1 or nonnegative")
    text = _read_text(filename)
    if occurrence == -1:
        count = text.count(search_str)
        updated = text.replace(search_str, replace_with)
    else:
        positions = _positions(text, search_str)
        if occurrence >= len(positions):
            return 0
        index = positions[occurrence]
        updated = text[:index] + replace_with + text[index + len(search_str):]
        count = 1
    if count:
        _write_text(filename, updated)
    return count


def ed_append(filename: str, string: str) -> int:
    if not isinstance(string, str):
        raise TypeError("Appended content must be a string")
    text = _read_text(filename) if Path(filename).exists() else ""
    _write_text(filename, text + string)
    return len(string)


def test_ed_find() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        filename = str(Path(directory) / "find.txt")
        original = "01234567890123456789 banana café café"
        ed_append(filename, original)
        checks = [
            ("find repeated matches", ed_find(filename, "345") == [3, 13]),
            ("find absent text", ed_find(filename, "356") == []),
            ("find overlapping matches", ed_find(filename, "ana") == [22, 24]),
            ("find Unicode", ed_find(filename, "café") == [28, 33]),
            ("find preserves file", ed_read(filename) == original),
        ]
        ed_replace(filename, original, "")
        checks.append(("find in empty file", ed_find(filename, "x") == []))
        results = [testif(ok, name, "passed", "failed") for name, ok in checks]
        return all(results)


def test_ed_replace() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        filename = str(Path(directory) / "replace.txt")
        original = "01234567890123456789"
        ed_append(filename, original)
        count = ed_replace(filename, "345", "ABCDE", 1)
        checks = [("replace selected occurrence", count == 1 and
                   ed_read(filename) == "0123456789012ABCDE6789")]
        _write_text(filename, original)
        count = ed_replace(filename, "345", "ABCDE")
        checks.append(("replace all occurrences", count == 2 and
                       ed_read(filename) == "012ABCDE6789012ABCDE6789"))
        _write_text(filename, original)
        count = ed_replace(filename, "345", "X", 0)
        checks.append(("replace first occurrence", count == 1 and
                       ed_read(filename) == "012X67890123456789"))
        before = ed_read(filename)
        checks.append(("excess occurrence", ed_replace(filename, "345", "X", 9) == 0
                       and ed_read(filename) == before))
        checks.append(("absent replacement", ed_replace(filename, "missing", "X") == 0
                       and ed_read(filename) == before))
        _write_text(filename, "café café")
        checks.append(("Unicode deletion", ed_replace(filename, "café", "") == 2
                       and ed_read(filename) == " "))
        _write_text(filename, "aaaa")
        checks.append(("all matches do not overlap", ed_replace(filename, "aa", "X") == 2
                       and ed_read(filename) == "XX"))
        _write_text(filename, "aaaa")
        checks.append(("selected overlapping match", ed_replace(filename, "aa", "X", 1) == 1
                       and ed_read(filename) == "aXa"))
        _write_text(filename, original)
        try:
            ed_replace(filename, "345", "X", -2)
        except ValueError:
            invalid_rejected = True
        else:
            invalid_rejected = False
        checks.append(("invalid occurrence preserves file", invalid_rejected
                       and ed_read(filename) == original))
        try:
            ed_replace(filename, "", "X")
        except ValueError:
            empty_rejected = True
        else:
            empty_rejected = False
        checks.append(("empty search preserves file", empty_rejected
                       and ed_read(filename) == original))
        results = [testif(ok, name, "passed", "failed") for name, ok in checks]
        return all(results)


def main() -> None:
    print("Ethan Zbeda | FAU student ID: ezbeda2023")
    with tempfile.TemporaryDirectory() as directory:
        filename = str(Path(directory) / "file1.txt")
        print("\nCreating and appending:")
        print("Characters written:", ed_append(filename, "0123456789"))
        print("Characters written:", ed_append(filename, "0123456789"))
        print("Full content:", ed_read(filename))
        print("Read [3, 9):", ed_read(filename, 3, 9))
        print("Read [3, end):", ed_read(filename, 3))
        print("Find '345':", ed_find(filename, "345"))
        print("Find '356':", ed_find(filename, "356"))
        print("Replace occurrence 1:", ed_replace(filename, "345", "ABCDE", 1))
        print("Content:", ed_read(filename))
        _write_text(filename, "01234567890123456789")
        print("Replace all:", ed_replace(filename, "345", "ABCDE"))
        print("Content:", ed_read(filename))
    print("\nUnit tests:")
    find_passed = test_ed_find()
    replace_passed = test_ed_replace()
    if not (find_passed and replace_passed):
        raise AssertionError("Editor unit tests failed")
    print("\nAll editor unit tests passed.")


if __name__ == "__main__":
    main()
