#!/usr/bin/env python3
"""Measure the house style of past Japanese posts, and compare new copy against it.

Usage:
  python3 voice_stats.py SAMPLES [SAMPLES ...]                 # profile only
  python3 voice_stats.py SAMPLES [...] --compare final.md      # profile + deviation check
  python3 voice_stats.py SAMPLES --json                        # machine-readable

SAMPLES can be:
  - .md/.txt with posts in ```copy blocks, or separated by lines of '---'
  - .csv with a text column (auto-detects: Post text, Tweet text, text, caption, 本文, 投稿, message)
  - .xlsx (same column detection; needs openpyxl)
Rows/posts with no Japanese are ignored (e.g. English-only posts in a mixed export).

Numbers describe habits; they are evidence for the voice profile, not targets to hit.
Exit code is always 0 unless the input can't be read (2).
"""
import argparse
import csv
import json
import re
import statistics as st
import sys
from collections import Counter

JA = re.compile(r"[぀-ヿ㐀-鿿]")
KATA = re.compile(r"[゠-ヿ]")
URL = re.compile(r"https?://\S+")
TAG = re.compile(r"[#＃][^\s#＃]+")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚⌛⏩-⏺]")
BLOCK = re.compile(r"```(?:copy)\s*\n(.*?)\n```", re.S)
TEXT_COLS = ["post text", "tweet text", "text", "caption", "本文", "投稿", "投稿本文", "message", "content"]


def load(path):
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        return from_rows(rows, path)
    if path.lower().endswith((".xlsx", ".xlsm")):
        try:
            import openpyxl
        except ImportError:
            print("xlsx needs openpyxl: pip install openpyxl (or export to CSV)")
            sys.exit(2)
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        it = ws.iter_rows(values_only=True)
        hdr = [str(h or "") for h in next(it)]
        return from_rows([dict(zip(hdr, r)) for r in it], path)
    text = open(path, encoding="utf-8").read()
    blocks = BLOCK.findall(text)
    if blocks:
        return blocks
    return [p.strip() for p in re.split(r"^\s*---+\s*$", text, flags=re.M) if p.strip()]


def from_rows(rows, path):
    if not rows:
        return []
    cols = {c.lower().strip(): c for c in rows[0].keys() if c}
    for want in TEXT_COLS:
        if want in cols:
            return [str(r[cols[want]]) for r in rows if r.get(cols[want])]
    print(f"No text column found in {path}. Columns: {list(rows[0].keys())}")
    sys.exit(2)


def sentences(body):
    return [s.strip() for s in re.split(r"(?<=[。！？!?])|\n", body) if s.strip()]


def ending_type(s):
    s = re.sub(r"[。！？!?…\s" + EMOJI.pattern[1:-1] + r"]+$", "", s)
    if not s:
        return None
    if re.search(r"(です|ます|ません|ました|でした|ください|ましょう|ませんか|でしょう)(ね|よ|よね)?$", s):
        return "polite"
    if re.search(r"(だ|である|だった|じゃない|してみた|だよ|だね|よね|かも|しよう|してね|ね|よ)$", s):
        return "plain/casual"
    if re.search(r"[一-鿿゠-ヿA-Za-z0-9）」』】]$", s):
        return "noun-ending (体言止め)"
    return "other"


def profile(posts):
    posts = [p for p in posts if JA.search(p)]
    if not posts:
        return None
    P = len(posts)
    bodies = [TAG.sub("", URL.sub("", p)).strip() for p in posts]
    ends, emo, tags, ctas, openers = Counter(), Counter(), Counter(), Counter(), Counter()
    emo_line_end = emo_total = 0
    for p, b in zip(posts, bodies):
        for s in sentences(b):
            t = ending_type(s)
            if t:
                ends[t] += 1
        for line in p.splitlines():
            found = EMOJI.findall(line)
            emo_total += len(found)
            emo.update(found)
            if found and re.search("(" + EMOJI.pattern + r")[\s！!？?]*$", line):
                emo_line_end += len(re.findall("(" + EMOJI.pattern + r")[\s]*$", line)) or 1
        tags.update(TAG.findall(p))
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if lines:
            openers[re.sub(r"\s.*", "", lines[0])[:10]] += 1
            ctas[lines[-1][:30]] += 1
    jp_chars = sum(len(JA.findall(b)) for b in bodies) or 1
    alltext = "\n".join(posts)
    jl_space = len(re.findall(r"[぀-鿿] [A-Za-z0-9]|[A-Za-z0-9] [぀-鿿]", alltext))
    jl_tight = len(re.findall(r"[぀-鿿][A-Za-z0-9]|[A-Za-z0-9][぀-鿿]", alltext))
    n_end = sum(ends.values()) or 1
    lens = [len(b) for b in bodies]
    linec = [len([l for l in p.splitlines() if l.strip()]) for p in posts]
    return {
        "posts": P,
        "chars_per_post_median": int(st.median(lens)),
        "chars_per_post_range": [min(lens), max(lens)],
        "lines_per_post_median": st.median(linec),
        "blank_line_posts_pct": round(100 * sum(1 for p in posts if re.search(r"\n\s*\n", p)) / P),
        "endings_pct": {k: round(100 * v / n_end) for k, v in ends.most_common()},
        "emoji_per_post": round(emo_total / P, 1),
        "emoji_at_line_end_pct": round(100 * emo_line_end / emo_total) if emo_total else None,
        "top_emoji": [e for e, _ in emo.most_common(8)],
        "exclaim_per_post": {"！": round(alltext.count("！") / P, 1), "!": round(alltext.count("!") / P, 1)},
        "question_per_post": {"？": round(alltext.count("？") / P, 1), "?": round(alltext.count("?") / P, 1)},
        "brackets_【】_pct": round(100 * sum(1 for p in posts if "【" in p) / P),
        "ellipsis_per_post": round((alltext.count("…") + alltext.count("...")) / P, 1),
        "wave_dash_per_post": round((alltext.count("〜") + alltext.count("～")) / P, 1),
        "anata_per_post": round(alltext.count("あなた") / P, 2),
        "katakana_ratio_pct": round(100 * sum(len(KATA.findall(b)) for b in bodies) / jp_chars),
        "jp_latin_spacing": "spaced" if jl_space > jl_tight else "tight" if jl_tight else "n/a",
        "hashtags_per_post": round(sum(len(TAG.findall(p)) for p in posts) / P, 1),
        "top_hashtags": [t for t, _ in tags.most_common(10)],
        "common_openers": [o for o, c in openers.most_common(5) if c > 1],
        "common_last_lines": [c for c, n in ctas.most_common(5) if n > 1],
    }


def compare(base, new):
    flags = []

    def ratio(a, b):
        return (b + 0.5) / (a + 0.5)

    for k in ["emoji_per_post", "ellipsis_per_post", "hashtags_per_post"]:
        r = ratio(base[k], new[k])
        if r > 2 or r < 0.5:
            flags.append(f"{k}: samples {base[k]} vs new {new[k]}")
    for sym, fw, hw in [("exclaim", "！", "!"), ("question", "？", "?")]:
        b, n = base[f"{sym}_per_post"], new[f"{sym}_per_post"]
        if b[fw] > b[hw] and n[hw] > n[fw]:
            flags.append(f"{sym}: samples use full-width {fw}, new copy uses half-width {hw}")
        if b[hw] > b[fw] and n[fw] > n[hw]:
            flags.append(f"{sym}: samples use half-width {hw}, new copy uses full-width {fw}")
        r = ratio(b[fw] + b[hw], n[fw] + n[hw])
        if r > 2 or r < 0.5:
            flags.append(f"{sym} density: samples {b[fw] + b[hw]}/post vs new {n[fw] + n[hw]}/post")
    bt = max(base["endings_pct"], key=base["endings_pct"].get) if base["endings_pct"] else None
    nt = max(new["endings_pct"], key=new["endings_pct"].get) if new["endings_pct"] else None
    if bt and nt and bt != nt and {bt, nt} >= {"polite", "plain/casual"}:
        flags.append(f"register: samples mostly {bt}, new copy mostly {nt}")
    if base["anata_per_post"] == 0 and new["anata_per_post"] > 0:
        flags.append("あなた: never used in samples, used in new copy")
    if base["jp_latin_spacing"] != "n/a" and new["jp_latin_spacing"] not in ("n/a", base["jp_latin_spacing"]):
        flags.append(f"JP/Latin spacing: samples {base['jp_latin_spacing']}, new {new['jp_latin_spacing']}")
    if abs(base["katakana_ratio_pct"] - new["katakana_ratio_pct"]) > 10:
        flags.append(f"katakana ratio: samples {base['katakana_ratio_pct']}% vs new {new['katakana_ratio_pct']}%")
    if base["emoji_at_line_end_pct"] and new["emoji_at_line_end_pct"] is not None \
            and abs(base["emoji_at_line_end_pct"] - new["emoji_at_line_end_pct"]) > 30:
        flags.append(f"emoji placement: samples {base['emoji_at_line_end_pct']}% at line end vs new {new['emoji_at_line_end_pct']}%")
    if base["brackets_【】_pct"] >= 50 and new["brackets_【】_pct"] == 0:
        flags.append("【】 headers: common in samples, absent in new copy (only add if the post type matches)")
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("samples", nargs="+")
    ap.add_argument("--compare")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    posts = [p for f in a.samples for p in load(f)]
    base = profile(posts)
    if not base:
        print("No Japanese posts found in samples.")
        sys.exit(2)
    out = {"samples": base}
    if a.compare:
        new = profile(load(a.compare))
        out["new"] = new
        out["flags"] = compare(base, new) if new else ["no Japanese copy found in --compare file"]
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    print(f"== Voice stats: {base['posts']} sample posts ==")
    for k, v in base.items():
        line = f"  {k:26} {v}"
        if a.compare and out.get("new"):
            line += f"    | new: {out['new'].get(k)}"
        print(line)
    if a.compare:
        print("\n== Deviations (look here; small samples are noisy) ==")
        for f in out["flags"] or ["none"]:
            print("  •", f)
    if base["posts"] < 8:
        print(f"\nNote: only {base['posts']} samples. Treat stats as weak evidence; lean on reading the posts.")


if __name__ == "__main__":
    main()
