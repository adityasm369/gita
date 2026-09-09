#!/usr/bin/env python3
"""Add a one-line English summary to every shloka, and list them on the chapter page.

The summaries live in summaries/*.json, one file per chapter, keyed "c.v" — kept
outside dashboard.html because the file is a 1.4 MB single-page app and a 701-key
edit is far easier to review as data than as a diff of a minified array.

Idempotent: run it again after editing a summary file and it rewrites the `su`
fields in place.
"""
import glob
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "dashboard.html")


def load_summaries():
    out = {}
    # ch*.json only: speakers.json lives in the same directory and is a
    # different kind of thing entirely. Globbing "*.json" merged it in and
    # silently replaced fourteen summaries with their speaker labels.
    for f in sorted(glob.glob(os.path.join(HERE, "summaries", "ch*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for k, v in d.items():
            out[k] = " ".join(str(v).split())
    return out


def blob_span(s, name):
    """Byte span of a top-level array/object literal assigned to `name`."""
    m = re.search(r'(?:const|let|var)\s+%s\s*=\s*' % name, s)
    i = m.end()
    o = s[i]
    c = {"[": "]", "{": "}"}[o]
    depth = j = 0
    instr = esc = False
    j = i
    while j < len(s):
        ch = s[j]
        if instr:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                instr = False
        else:
            if ch == '"':
                instr = True
            elif ch == o:
                depth += 1
            elif ch == c:
                depth -= 1
                if depth == 0:
                    return i, j + 1
        j += 1
    raise SystemExit("could not find the %s literal" % name)


# Who addresses whom, by recorded speaker. The Gita is a dialogue inside a
# dialogue -- Sanjaya narrating to the blind king what Krishna and Arjuna said --
# and a first-time reader cannot tell from the verse alone.
VOICE = {
    "Dhritarashtra": "Dhritarashtra → Sanjaya",
    "Sanjaya": "Sanjaya → Dhritarashtra",
    "Arjuna": "Arjuna → Krishna",
    "Krishna": "Krishna → Arjuna",
}


def load_overrides():
    path = os.path.join(HERE, "summaries", "speakers.json")
    if not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_")}


def main():
    su = load_summaries()
    over = load_overrides()
    s = io.open(PAGE, encoding="utf-8").read()
    a, b = blob_span(s, "V")
    V = json.loads(s[a:b])

    have = missing = 0
    for v in V:
        key = "%d.%d" % (v["c"], v["v"])
        if key in su:
            v["su"] = su[key]
            have += 1
        else:
            v.pop("su", None)
            missing += 1
        voice = over.get(key) or VOICE.get(v.get("sp", ""))
        if voice:
            v["wh"] = voice
        else:
            v.pop("wh", None)

    s = s[:a] + json.dumps(V, ensure_ascii=False, separators=(",", ":")) + s[b:]
    io.open(PAGE, "w", encoding="utf-8").write(s)

    done = {}
    for v in V:
        done.setdefault(v["c"], [0, 0])
        done[v["c"]][1] += 1
        if v.get("su"):
            done[v["c"]][0] += 1
    for c in sorted(done):
        n, t = done[c]
        flag = "" if n == t else "   <-- %d missing" % (t - n)
        print("  ch %2d  %3d / %3d%s" % (c, n, t, flag))
    print("\n  %d summarised, %d still to write" % (have, missing))


if __name__ == "__main__":
    main()
