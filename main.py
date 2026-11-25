#!/usr/bin/env python3
"""Unsent: The Micro-Confession Sprint - make.fun entry.

The program writes one unsent confession to entry.txt: a "To: ..."
address line followed by the message itself, exactly one line as typed.
Output goes to $MAKEFUN_OUTPUT_DIR/entry.txt. Pure stdlib, fully
deterministic, and it never touches the network. The entry is a
constant in this file, so every run produces the same two lines.
"""
import os
import sys

ENTRY = "To: Dad\nI still rehearse the call where I tell you I quit the degree you paid for, then hang up on the third ring because your pride is the only thing I haven't broken yet."
MAX_CHARS = 260
MESSAGE_LIMIT = 200


def validate(text):
    """Check a candidate entry against the sprint's character gates."""
    if not text or not text.strip():
        raise ValueError("entry is empty or whitespace-only")
    # The file holds the entry plus one trailing newline, so the gate
    # counts that extra byte as well.
    if len(text) + 1 > MAX_CHARS:
        raise ValueError(
            "entry file would be %d chars, over the %d-char gate"
            % (len(text) + 1, MAX_CHARS)
        )
    lines = text.split("\n")
    if len(lines) != 2:
        raise ValueError("entry must be exactly two lines")
    if not lines[0].startswith("To: "):
        raise ValueError("first line must be a \"To: ...\" line")
    if len(lines[1]) > MESSAGE_LIMIT:
        raise ValueError(
            "message line is %d chars, over the %d-char limit"
            % (len(lines[1]), MESSAGE_LIMIT)
        )
    return text


def validate_written(path):
    """Read entry.txt back from disk and re-check the artifact itself."""
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("entry.txt is not valid UTF-8: %s" % exc)
    validate(text.rstrip("\n"))
    if text.count("\n") > 2:
        raise ValueError("entry.txt must be two lines")
    return text


def write_entry():
    """Write the validated entry to entry.txt and confirm the round trip."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    target = os.path.join(out_dir, "entry.txt")
    os.makedirs(out_dir, exist_ok=True)
    data = (validate(ENTRY) + "\n").encode("utf-8")
    with open(target, "wb") as f:
        f.write(data)
    with open(target, "rb") as f:
        if f.read() != data:
            raise ValueError("entry.txt round-trip mismatch")
    validate_written(target)
    return target


def main(argv):
    if "--self-test" in argv:
        validate(ENTRY)
        print("self-test ok: %d chars" % len(ENTRY))
        return 0
    if "--check" in argv:
        validate(ENTRY)
        print("check ok: %d chars, within %d" % (len(ENTRY), MAX_CHARS))
        return 0
    try:
        write_entry()
    except ValueError as exc:
        print("invalid entry: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
