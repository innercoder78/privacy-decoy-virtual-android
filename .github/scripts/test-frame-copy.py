#!/usr/bin/env python3
"""Desktop-only ownership/coherence witnesses; no Android or hostile process.

Original PDVA research. Two mappings of one 4096-byte synthetic temporary file.
This is not a display receiver, authentication protocol, or Android mmap test.
"""

import contextlib
import mmap
import tempfile
import threading
import unittest


@contextlib.contextmanager
def mappings():
    with tempfile.TemporaryFile() as backing:
        backing.write(b"\0" * 4096)
        backing.flush()
        with mmap.mmap(backing.fileno(), 4096, access=mmap.ACCESS_WRITE) as writer:
            with mmap.mmap(backing.fileno(), 4096, access=mmap.ACCESS_READ) as reader:
                yield writer, reader


def split_copy(writer, reader, mutate):
    """Force a legal interleaving, not a probabilistic bulk-memcpy race.

    Byte 2 is an untrusted producer counter. The writer deliberately leaves it
    unchanged. Only bytes 0 and 1 are the tiny payload; no graphics assumed.
    """
    writer[:3] = b"AA\x02"
    begin = threading.Event()
    finished = threading.Event()
    states = [bytes(reader[:2])]
    errors = []

    def produce():
        try:
            if not begin.wait(2):
                raise RuntimeError("reader barrier timed out")
            if mutate:
                writer[0] = ord("B")
                states.append(bytes(reader[:2]))
                writer[1] = ord("B")
                states.append(bytes(reader[:2]))
        except BaseException as error:
            errors.append(error)
        finally:
            finished.set()

    producer = threading.Thread(target=produce)
    producer.start()
    try:
        before = reader[2]
        first = reader[0]
        begin.set()
        if not finished.wait(3):
            raise RuntimeError("producer barrier timed out")
        if errors:
            raise errors[0]
        owned = bytes((first, reader[1]))
        after = reader[2]
        # Intentionally incorrect certificate under a compromised producer.
        counter_accepts = before == after and before % 2 == 0
        return owned, states, counter_accepts
    finally:
        begin.set()
        producer.join(3)
        if producer.is_alive():
            raise RuntimeError("producer did not finish")


class CopyControls(unittest.TestCase):
    def test_readonly_alias_is_not_an_owned_copy(self):
        with mappings() as (writer, reader):
            writer[:2] = b"AA"
            with self.assertRaises(TypeError):
                reader[0] = ord("X")
            incorrect_retained_frame = memoryview(reader)[:2]
            try:
                writer[:2] = b"BB"
                self.assertEqual(bytes(incorrect_retained_frame), b"BB")
                self.assertNotEqual(bytes(incorrect_retained_frame), b"AA")
            finally:
                incorrect_retained_frame.release()

    def test_owned_copy_survives_later_writes_and_unmapping(self):
        with mappings() as (writer, reader):
            writer[:2] = b"BA"  # Mutation before copying is visible.
            owned = bytes(reader[:2])
            writer[:2] = b"BB"
            self.assertEqual(reader[:2], b"BB")
            self.assertEqual(owned, b"BA")
        self.assertEqual(owned, b"BA")

    def test_quiescent_copy_positive_control(self):
        with mappings() as (writer, reader):
            owned, states, accepted = split_copy(writer, reader, False)
            self.assertEqual(states, [b"AA"])
            self.assertEqual(owned, b"AA")
            self.assertTrue(accepted)

    def test_unchanged_counter_falsely_accepts_never_existing_frame(self):
        with mappings() as (writer, reader):
            owned, states, accepted = split_copy(writer, reader, True)
            self.assertEqual(states, [b"AA", b"BA", b"BB"])
            self.assertEqual(owned, b"AB")
            self.assertNotIn(owned, states)
            self.assertTrue(accepted)  # Wrong certificate demonstrably accepts.
            writer[:2] = b"CC"
            self.assertEqual(owned, b"AB")  # Stable still does not mean coherent.


if __name__ == "__main__":
    unittest.main(verbosity=2)
