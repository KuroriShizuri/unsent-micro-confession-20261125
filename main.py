#!/usr/bin/env python3
"""Unsent in two lines: a "To:" line, then the message itself, kept short enough for the 260-character gate.
Unsent micro-confession: a text that was drafted, never sent.

The entry is a two-line draft message. Line one names the recipient,
line two is the confession itself — the call the author keeps rehearsing
and never makes. This script exists only to protect that wording: it
checks the draft against the competition's limits and hands the exact
bytes to the make.fun harness as entry.txt.

Usage:
    python3 main.py              write entry.txt (default: current dir)
    python3 main.py --check      validate the draft, write nothing
    python3 main.py --self-test  validate, write, then re-read the file
                                 from disk and confirm it matches

The output directory comes from MAKEFUN_OUTPUT_DIR; when that variable
is unset the current directory is used. Only the standard library is
used and no network access happens.
"""

import os
import sys

ENTRY = (
    "To: Dad\n"
    "I still rehearse the call where I tell you I quit the degree you paid "
    "for, then hang up on the third ring because your pride is the only "
    "thing I haven't broken yet."
)

MAX_TOTAL_CHARS = 260
MAX_MESSAGE_CHARS = 200
EXPECTED_LINE_COUNT = 2
OUTPUT_FILENAME = "entry.txt"


def complain(message):
    """Print a failure to stderr and stop with a non-zero status."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def inspect(draft):
    """Return a list of every rule the draft breaks (empty means valid)."""
    faults = []
    if not draft:
        faults.append("the entry is empty")
        return faults
    lines = draft.split("\n")
    if len(lines) != EXPECTED_LINE_COUNT:
        faults.append(
            "expected %d lines, found %d" % (EXPECTED_LINE_COUNT, len(lines))
        )
    if len(draft) > MAX_TOTAL_CHARS:
        faults.append(
            "entry is %d characters, over the %d limit"
            % (len(draft), MAX_TOTAL_CHARS)
        )
    if len(lines) > 1 and len(lines[1]) > MAX_MESSAGE_CHARS:
        faults.append(
            "the message line is %d characters, over the %d limit"
            % (len(lines[1]), MAX_MESSAGE_CHARS)
        )
    if "\r" in draft:
        faults.append("carriage returns are not allowed")
    return faults


def render(draft):
    """Encode the draft exactly as it must appear on disk."""
    return (draft + "\n").encode("utf-8")


def destination():
    """Resolve the output folder, creating it when it does not exist."""
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, OUTPUT_FILENAME)


def write_entry():
    """Validate, write, then re-read and re-validate the artifact."""
    faults = inspect(ENTRY)
    if faults:
        complain("; ".join(faults))
    target = destination()
    payload = render(ENTRY)
    with open(target, "wb") as handle:
        handle.write(payload)
    with open(target, "rb") as handle:
        on_disk = handle.read()
    if on_disk != payload:
        complain("entry.txt on disk does not match the validated entry")
    round_tripped = on_disk.decode("utf-8")
    if round_tripped != ENTRY + "\n":
        complain("entry.txt decoded back to different text")
    recheck = inspect(round_tripped.rstrip("\n"))
    if recheck:
        complain("written artifact fails validation: " + "; ".join(recheck))
    print("wrote %s (%d bytes)" % (target, len(payload)))


def main(argv):
    flags = set(argv[1:])
    unknown = flags - {"--check", "--self-test"}
    if unknown:
        complain("unknown option(s): " + ", ".join(sorted(unknown)))
    if "--check" in flags:
        faults = inspect(ENTRY)
        if faults:
            complain("; ".join(faults))
        print(
            "check ok: %d lines, %d characters"
            % (len(ENTRY.split("\n")), len(ENTRY))
        )
        return 0
    write_entry()
    if "--self-test" in flags:
        print("self-test ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
