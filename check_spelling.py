#!/usr/bin/env python3
"""Check the website's text for American spellings.

Every word on the site should be in British English. This scans site.json and
everything under content/, and lists any American spellings it finds with the
British spelling to use instead. It runs before every deploy, so a page with
"color" or "organize" in it will not go live until it is fixed.

Run it with:

    python3 check_spelling.py

It only knows common American spellings, so it is a safety net, not a full
spellchecker. Web addresses and email addresses are ignored.
"""

import re
import sys
from pathlib import Path

# American stem -> British stem. Endings such as s, ed, ing and ful are matched too.
WORDS = {
    "color": "colour", "favor": "favour", "favorite": "favourite", "honor": "honour",
    "labor": "labour", "neighbor": "neighbour", "behavior": "behaviour", "humor": "humour",
    "rumor": "rumour", "flavor": "flavour", "harbor": "harbour", "endeavor": "endeavour",
    "vapor": "vapour", "savor": "savour",
    "center": "centre", "theater": "theatre", "fiber": "fibre", "liter": "litre",
    "meager": "meagre", "somber": "sombre", "caliber": "calibre", "maneuver": "manoeuvre",
    "catalog": "catalogue", "dialog": "dialogue", "analog": "analogue",
    "defense": "defence", "offense": "offence", "pretense": "pretence",
    "gray": "grey", "skeptic": "sceptic", "skeptical": "sceptical", "mom": "mum",
    "jewelry": "jewellery", "aluminum": "aluminium", "fulfill": "fulfil",
    "enrollment": "enrolment", "skillful": "skilful", "willful": "wilful",
    "traveled": "travelled", "traveling": "travelling", "traveler": "traveller",
    "canceled": "cancelled", "canceling": "cancelling", "labeled": "labelled",
    "labeling": "labelling", "modeled": "modelled", "modeling": "modelling",
    "leveled": "levelled", "signaled": "signalled", "fueled": "fuelled",
    "counselor": "counsellor", "jeweler": "jeweller", "marvelous": "marvellous",
    "math": "maths", "airplane": "aeroplane",
}
SUFFIXES = r"(?:s|es|ed|d|ing|ful|ite|ites|ly|al)?"
WORD_RE = re.compile(r"\b(" + "|".join(sorted(WORDS, key=len, reverse=True)) + r")(" + SUFFIXES + r")\b", re.I)

# -ize / -yze words (organize, recognise...). These words really do end in -ize in British English.
IZE_OK = {"size", "prize", "seize", "capsize", "resize", "downsize", "oversize", "baize", "maize"}
IZE_RE = re.compile(r"\b([a-z]+?)(iz|yz)(e|es|ed|ing|er|ers|ation|ations|ational)\b", re.I)

IGNORE_RE = re.compile(r"(https?://\S+|www\.\S+|\S+@\S+|/assets/\S+|\]\(/\S*?\))")


def match_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def check_text(text: str) -> list:
    """Return [(american_word, british_word), ...] in the order they appear."""
    text = IGNORE_RE.sub(" ", text)
    found = []
    for m in WORD_RE.finditer(text):
        stem, suffix = m.group(1), m.group(2)
        british = WORDS[stem.lower()]
        if british.endswith("re") and suffix[:1] in ("e", "d"):
            suffix = "d" if suffix.startswith(("ed", "d")) else suffix
        found.append((m.start(), m.group(0), match_case(m.group(0), british + suffix)))
    for m in IZE_RE.finditer(text):
        root, z, ending = m.groups()
        word = m.group(0)
        if (root + z + "e").lower() in IZE_OK or len(root) < 2:
            continue
        british = root + ("is" if z.lower() == "iz" else "ys") + ending
        found.append((m.start(), word, match_case(word, british)))
    return [(w, b) for _, w, b in sorted(found)]


def files_to_check(root: Path) -> list:
    files = [root / "site.json"]
    for pattern in ("*.md", "*.json"):
        files += sorted((root / "content").rglob(pattern))
    return [f for f in files if f.exists()]


def check_project(root: Path) -> list:
    """Return [(file, line_number, american_word, british_word), ...] for the whole site."""
    problems = []
    for path in files_to_check(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for american, british in check_text(line):
                problems.append((str(path.relative_to(root)), number, american, british))
    return problems


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    problems = check_project(here)
    for file, line, american, british in problems:
        print(f"{file}, line {line}: '{american}' is American spelling. Use '{british}'.")
    if problems:
        sys.exit(f"{len(problems)} American spelling(s) found. Fix them and try again.")
    print("Spelling check passed: no American spellings found.")
