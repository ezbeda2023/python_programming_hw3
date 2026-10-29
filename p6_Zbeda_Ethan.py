"""Problem 6: storage entries, recursive traversal, and standard unit tests."""

from __future__ import annotations

import unittest


class Entry:
    """A named storage entry with an optional parent, accessed through parent()."""

    def __init__(self, name: str, parent: Entry | None = None) -> None:
        """Store a nonempty name and optional parent entry.

        Raise TypeError for incorrect types and ValueError for an empty name.
        Parent links must be acyclic. Use Folder.add to establish membership.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not name.strip():
            raise ValueError("Name must not be empty")
        if parent is not None and not isinstance(parent, Entry):
            raise TypeError("Parent must be an Entry or None")
        self.name = name
        self._parent = parent

    def parent(self) -> Entry | None:
        """Return the parent entry, or None for a root entry."""
        return self._parent

    def size(self) -> int:
        """Return storage bytes in subclasses; raise NotImplementedError here."""
        raise NotImplementedError("Subclasses must implement size()")

    def absolute_path(self) -> list[Entry]:
        """Recursively return entries from self through ancestors to the root.

        Require acyclic parent links. Return a new list, preserving the actual
        Entry objects. A root entry returns a one-element list containing self.
        """
        if self._parent is None:
            return [self]
        return [self] + self._parent.absolute_path()


class File(Entry):
    """A storage file whose size is a nonnegative integer number of bytes."""

    def __init__(
        self, name: str, bytes_used: int, parent: Entry | None = None
    ) -> None:
        """Initialize entry details and bytes_used.

        Raise TypeError for a noninteger byte count and ValueError for a
        negative count. Base constructor validation applies to name and parent.
        """
        super().__init__(name, parent)
        if type(bytes_used) is not int:
            raise TypeError("Bytes used must be an integer")
        if bytes_used < 0:
            raise ValueError("Bytes used must be nonnegative")
        self.bytes_used = bytes_used

    def size(self) -> int:
        """Return this file's bytes_used without changing the file."""
        return self.bytes_used


class Folder(Entry):
    """A storage folder owning an ordered list of child entries."""

    def __init__(self, name: str, parent: Entry | None = None) -> None:
        """Initialize entry details and a new empty child list."""
        super().__init__(name, parent)
        self._children: list[Entry] = []

    def add(self, entry: Entry) -> None:
        """Add entry once and set its parent to this folder.

        Require acyclic structures and an entry that is unattached or already
        names this folder as parent. Raise TypeError for nonentries and
        ValueError for self, duplicate children, or a different existing parent.
        """
        if not isinstance(entry, Entry):
            raise TypeError("Child must be an Entry")
        if entry is self:
            raise ValueError("A folder cannot contain itself")
        if entry in self._children:
            raise ValueError("Entry is already in this folder")
        if entry.parent() is not None and entry.parent() is not self:
            raise ValueError("Entry already belongs to another parent")
        self._children.append(entry)
        entry._parent = self

    def children(self) -> tuple[Entry, ...]:
        """Return an immutable snapshot of child references in insertion order."""
        return tuple(self._children)

    def size(self) -> int:
        """Return total bytes by calling every child's common size interface.

        Nested folders recursively supply their totals; empty folders return 0.
        """
        return sum(child.size() for child in self._children)


def find_large_files(entry: Entry, minimum_size: int) -> list[File]:
    """Recursively return files of at least minimum_size bytes, in child order.

    For a File, return [entry] if it qualifies, otherwise []. For a Folder,
    search every child, including nested folders; empty folders return [].
    Require a nonnegative integer threshold and acyclic structures. Raise
    TypeError for invalid argument types or unsupported Entry subclasses and
    ValueError for a negative threshold. Leave the hierarchy unchanged.
    """
    if type(minimum_size) is not int:
        raise TypeError("Minimum size must be an integer")
    if minimum_size < 0:
        raise ValueError("Minimum size must be nonnegative")
    if isinstance(entry, File):
        return [entry] if entry.size() >= minimum_size else []
    if isinstance(entry, Folder):
        matches: list[File] = []
        for child in entry.children():
            matches.extend(find_large_files(child, minimum_size))
        return matches
    raise TypeError("Entry must be a File or Folder")


def build_example() -> Folder:
    """Return a four-level university hierarchy with five files totaling 7100 bytes."""
    root = Folder("university")
    courses = Folder("courses")
    programming = Folder("programming")
    homework = Folder("homework")
    root.add(File("readme.txt", 100))
    root.add(courses)
    courses.add(File("catalog.pdf", 2000))
    courses.add(programming)
    programming.add(File("notes.txt", 800))
    programming.add(homework)
    homework.add(File("solution.py", 1200))
    homework.add(File("results.csv", 3000))
    return root


class EntryTests(unittest.TestCase):
    """Unit tests for recursive search, absolute paths, and hierarchy behavior."""

    def setUp(self) -> None:
        """Create a fresh nested hierarchy and retain references for assertions."""
        self.root = Folder("root")
        self.middle = Folder("middle")
        self.inner = Folder("inner")
        self.small = File("small.txt", 10)
        self.large = File("large.bin", 100)
        self.zero = File("empty.txt", 0)
        self.root.add(self.small)
        self.root.add(self.middle)
        self.middle.add(self.inner)
        self.inner.add(self.large)
        self.inner.add(self.zero)

    def test_search_two_thresholds(self) -> None:
        """Search all nested levels at two thresholds and preserve traversal order."""
        self.assertEqual(find_large_files(self.root, 10), [self.small, self.large])
        self.assertEqual(find_large_files(self.root, 50), [self.large])

    def test_search_file_boundary(self) -> None:
        """Include a file exactly at the threshold and exclude a smaller file."""
        self.assertEqual(find_large_files(self.large, 100), [self.large])
        self.assertEqual(find_large_files(self.large, 101), [])

    def test_search_zero_threshold(self) -> None:
        """A zero threshold includes zero-byte files."""
        self.assertEqual(find_large_files(self.root, 0),
                         [self.small, self.large, self.zero])

    def test_search_empty_folder(self) -> None:
        """An empty folder has no qualifying files."""
        self.assertEqual(find_large_files(Folder("empty"), 0), [])

    def test_search_no_matches(self) -> None:
        """A threshold larger than all files returns an empty list."""
        self.assertEqual(find_large_files(self.root, 1000), [])

    def test_search_validation(self) -> None:
        """Invalid thresholds and unsupported entries raise standard exceptions."""
        with self.assertRaises(ValueError):
            find_large_files(self.root, -1)
        with self.assertRaises(TypeError):
            find_large_files(self.root, 1.5)
        with self.assertRaises(TypeError):
            find_large_files(Entry("base"), 0)

    def test_absolute_path_root(self) -> None:
        """A root path contains only the root object."""
        self.assertEqual(self.root.absolute_path(), [self.root])
        self.assertIsNone(self.root.parent())

    def test_absolute_path_nested_file(self) -> None:
        """A nested file path runs from the file up to the root."""
        self.assertEqual(self.large.absolute_path(),
                         [self.large, self.inner, self.middle, self.root])

    def test_absolute_path_folder(self) -> None:
        """A nested folder path contains its ancestors in the required order."""
        self.assertEqual(self.inner.absolute_path(),
                         [self.inner, self.middle, self.root])

    def test_absolute_path_independent_list(self) -> None:
        """Changing a returned path list does not change the hierarchy."""
        path = self.large.absolute_path()
        path.clear()
        self.assertEqual(len(self.large.absolute_path()), 4)
        self.assertIs(self.large.parent(), self.inner)

    def test_polymorphic_size(self) -> None:
        """The base interface handles files and nested folders with one call."""
        entry: Entry = self.root
        self.assertEqual(entry.size(), 110)
        self.assertEqual(Folder("empty").size(), 0)

    def test_children_snapshot(self) -> None:
        """Children returns a tuple unaffected by later additions."""
        snapshot = self.root.children()
        self.assertIsInstance(snapshot, tuple)
        self.root.add(File("extra", 1))
        self.assertEqual(snapshot, (self.small, self.middle))

    def test_invalid_file_size(self) -> None:
        """Negative and noninteger byte counts are rejected."""
        with self.assertRaises(ValueError):
            File("bad", -1)
        with self.assertRaises(TypeError):
            File("bad", 1.5)

    def test_add_validation(self) -> None:
        """Duplicate children and children with different parents are rejected."""
        with self.assertRaises(ValueError):
            self.root.add(self.small)
        with self.assertRaises(ValueError):
            self.inner.add(self.small)
        self.assertIs(self.small.parent(), self.root)


def print_tree(entry: Entry, depth: int = 0) -> None:
    """Recursively display entry names and sizes, indenting child entries."""
    print(f"{'  ' * depth}{entry.name}: {entry.size()} bytes")
    if isinstance(entry, Folder):
        for child in entry.children():
            print_tree(child, depth + 1)


def main() -> None:
    """Demonstrate polymorphic storage totals, two searches, paths, and tests."""
    print("Ethan Zbeda | FAU student ID: ezbeda2023", flush=True)
    root = build_example()
    print("\nFolder hierarchy:")
    print_tree(root)
    entry: Entry = root
    print(f"\nOne size() call on the outer folder: {entry.size()} bytes")
    for threshold in (1000, 2500):
        print(f"\nFiles with at least {threshold} bytes:")
        for file in find_large_files(root, threshold):
            print(f"{file.name}: {file.size()} bytes")
    target = find_large_files(root, 2500)[0]
    print("\nAbsolute path from file to root:")
    print(" -> ".join(part.name for part in target.absolute_path()))
    print("\nAbsolute path of the root:")
    print(" -> ".join(part.name for part in root.absolute_path()))
    print("\nUnit tests:", flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EntryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
