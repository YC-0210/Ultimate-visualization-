#!/usr/bin/env python3
"""Cache the Daylog into ./daylog/ so a teaching session can read it.

The Daylog is the dated account of the learning, written by hand on the
personal website and stored in Supabase. It is the source; ./daylog/ is a
disposable, gitignored copy. This script only ever reads.

    SUPABASE_URL=https://<ref>.supabase.co \
    SUPABASE_KEY=<key> \
    python3 bin/pull-daylog.py [--project Super-visualizer] [--since 2026-09-01]

The key decides what comes back. A Daylog Entry is a draft until it is
published, and the draft is usually the most recent day - the one worth
reading. An anon key is refused RLS on drafts and will silently return only
published days, so use a key that authenticates as the Owner.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

REST = "/rest/v1/"


# --- TipTap document -> Markdown -------------------------------------------
# A Daylog body is a ProseMirror doc: nested nodes, with the text carrying
# marks. Walk it. Do not reach for a JSON path expression - `$.**.text` matches
# at more than one depth and silently duplicates every paragraph.

MARK_WRAP = {"bold": "**", "italic": "*", "code": "`", "strike": "~~"}


def render_text(node):
    text = node.get("text", "")
    for mark in node.get("marks", []):
        kind = mark.get("type")
        if kind in MARK_WRAP:
            wrap = MARK_WRAP[kind]
            text = f"{wrap}{text}{wrap}"
        elif kind == "link":
            href = mark.get("attrs", {}).get("href", "")
            text = f"[{text}]({href})"
    return text


def render_inline(nodes):
    out = []
    for node in nodes or []:
        if node.get("type") == "text":
            out.append(render_text(node))
        elif node.get("type") == "hardBreak":
            out.append("\n")
        else:  # an inline node this script has not met yet
            out.append("".join(render_inline(node.get("content"))))
    return out


def render_block(node, depth=0):
    kind = node.get("type")
    content = node.get("content", [])
    pad = "  " * depth

    if kind in ("doc",):
        return "\n\n".join(b for b in (render_block(c, depth) for c in content) if b)
    if kind == "paragraph":
        return pad + "".join(render_inline(content))
    if kind == "heading":
        level = node.get("attrs", {}).get("level", 1)
        return "#" * level + " " + "".join(render_inline(content))
    if kind == "blockquote":
        inner = "\n\n".join(render_block(c, depth) for c in content)
        return "\n".join("> " + line for line in inner.splitlines())
    if kind == "codeBlock":
        lang = node.get("attrs", {}).get("language") or ""
        return f"```{lang}\n" + "".join(render_inline(content)) + "\n```"
    if kind == "horizontalRule":
        return "---"
    if kind in ("bulletList", "orderedList"):
        items = []
        for i, item in enumerate(content, start=1):
            bullet = "- " if kind == "bulletList" else f"{i}. "
            body = "\n\n".join(render_block(c, depth + 1) for c in item.get("content", []))
            body = body.strip()
            first, _, rest = body.partition("\n")
            items.append(pad + bullet + first + ("\n" + rest if rest else ""))
        return "\n".join(items)
    if kind == "listItem":
        return "\n\n".join(render_block(c, depth) for c in content)

    # Unknown block: keep whatever text it holds rather than dropping the day.
    return pad + "".join(render_inline(content))


def to_markdown(body):
    if not isinstance(body, dict):
        return ""
    return render_block(body).strip()


# --- Supabase ---------------------------------------------------------------


def get(url, key, path, **params):
    query = urllib.parse.urlencode(params, safe="*.,()")
    request = urllib.request.Request(
        f"{url.rstrip('/')}{REST}{path}?{query}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"Supabase said {error.code} for {path}: {error.read().decode()[:300]}")
    except urllib.error.URLError as error:
        sys.exit(f"Could not reach {url}: {error.reason}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="Super-visualizer")
    parser.add_argument("--since", help="only entries dated on or after YYYY-MM-DD")
    parser.add_argument("--out", default="daylog", type=pathlib.Path)
    args = parser.parse_args()

    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if not url or not key:
        sys.exit("Set SUPABASE_URL and SUPABASE_KEY (see the docstring).")

    projects = get(url, key, "projects", select="id,name", name=f"eq.{args.project}")
    if not projects:
        sys.exit(f"No Project named {args.project!r} came back. Wrong name, or the key cannot see it.")

    params = dict(select="entry_date,body,published_at", project_id=f"eq.{projects[0]['id']}", order="entry_date.asc,created_at.asc")
    if args.since:
        params["entry_date"] = f"gte.{args.since}"
    entries = get(url, key, "daylog_entries", **params)

    args.out.mkdir(parents=True, exist_ok=True)
    seen, written = {}, 0
    for entry in entries:
        date = entry["entry_date"]
        # Two Entries may share a day - you write in the morning and learn
        # something else at night (ADR-0011).
        seen[date] = seen.get(date, 0) + 1
        name = date if seen[date] == 1 else f"{date}-{seen[date]}"
        state = "published" if entry.get("published_at") else "draft"
        page = f"# {date}\n\n*{args.project} · {state}*\n\n{to_markdown(entry['body'])}\n"
        (args.out / f"{name}.md").write_text(page, encoding="utf-8")
        written += 1

    drafts = sum(1 for e in entries if not e.get("published_at"))
    print(f"{written} day(s) into {args.out}/ ({drafts} draft).")
    if not drafts:
        print("No drafts came back. If today's entry is unfinished, the key is not the Owner's.")


if __name__ == "__main__":
    main()
