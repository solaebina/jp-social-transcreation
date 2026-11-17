#!/usr/bin/env python3
"""Structural and invariant checks for EN→JA social transcreation.

Usage:
  python3 check_post.py source.md target.md [--glossary glossary.md]

Both files use the post format:
  ### P1 [x]
  ```copy
  ...post text...
  ```
(target may also contain ```alt blocks and Notes; alt blocks are checked too).

Exit code 0 = no errors (warnings may exist). 1 = errors. 2 = usage/parse error.
Warnings mean "look here", not "fix this".
"""
import argparse
import re
import sys
import unicodedata
from collections import Counter

POST_RE = re.compile(r"^###\s+(P\d+)\s*(?:\[([a-z]+)\])?", re.M)
BLOCK_RE = re.compile(r"```(copy|alt)\s*\n(.*?)\n```", re.S)
URL_RE = re.compile(r"https?://[^\s　<>「」）)]+")
MENTION_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9_]{1,30}")
HASHTAG_RE = re.compile(r"(?<![\w&])[#＃]([^\s#＃.,!?、。！？「」()（）]+)")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⭐⭕⌚-⌛⏩-⏺]"
)
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
JA_CHAR = r"[぀-ヿ㐀-鿿ｦ-ﾟ]"

LIMITS = {"x": 280, "threads": 500, "instagram": 2200, "linkedin": 3000, "tiktok": 4000}


def parse_posts(path):
    text = open(path, encoding="utf-8").read()
    posts = {}
    matches = list(POST_RE.finditer(text))
    if not matches:
        print(f"PARSE ERROR: no '### P<n>' posts found in {path}")
        sys.exit(2)
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        blocks = BLOCK_RE.findall(body)
        copy = [b for k, b in blocks if k == "copy"]
        alts = [b for k, b in blocks if k == "alt"]
        if not copy:
            print(f"PARSE ERROR: {m.group(1)} in {path} has no ```copy block")
            sys.exit(2)
        posts[m.group(1)] = {"platform": m.group(2), "copy": copy[0], "alts": alts}
    return posts


def strip_urls(s):
    return URL_RE.sub(" ", s)


def numbers(s):
    """Extract numeric values, normalising full-width digits and thousands separators."""
    s = unicodedata.normalize("NFKC", strip_urls(s))
    out = []
    for n in NUM_RE.findall(s):
        # treat ',' followed by exactly 3 digits as thousands grouping
        if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", n):
            n = n.replace(",", "")
        out.append(n)
    return Counter(out)


def x_weight(s):
    """Approximate X weighted length: URLs=23, emoji=2, CJK/full-width=2, else 1."""
    total = 0
    for _ in URL_RE.findall(s):
        total += 23
    s = URL_RE.sub("", s)
    for ch in s:
        cp = ord(ch)
        if (0x0000 <= cp <= 0x10FF or 0x2000 <= cp <= 0x200D
                or 0x2010 <= cp <= 0x201F or 0x2032 <= cp <= 0x2037):
            total += 1
        elif 0xFE00 <= cp <= 0xFE0F or cp == 0x200D:
            total += 0  # variation selectors / ZWJ
        else:
            total += 2
    return total


def load_never(path):
    banned = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|") or "❌" not in line:
            continue
        for m in re.finditer(r"❌\s*([^、,|❌]+)", line):
            term = m.group(1).strip()
            if term:
                banned.append(term)
    return banned


def check_text(pid, label, src, tgt, platform, banned, errs, warns):
    tag = f"{pid}/{label}"
    # URLs
    su, tu = Counter(URL_RE.findall(src)), Counter(URL_RE.findall(tgt))
    if su != tu:
        errs.append(f"{tag}: URL mismatch. source={sorted(su)} target={sorted(tu)}")
    # mentions
    sm, tm = Counter(MENTION_RE.findall(src)), Counter(MENTION_RE.findall(tgt))
    if sm != tm:
        errs.append(f"{tag}: @mention mismatch. source={sorted(sm)} target={sorted(tm)}")
    # hashtags: every source tag must survive byte-exact
    sh = Counter(HASHTAG_RE.findall(strip_urls(src)))
    th = Counter(HASHTAG_RE.findall(strip_urls(tgt)))
    missing = sh - th
    extra = th - sh
    if missing:
        errs.append(f"{tag}: source hashtags missing/altered: {sorted(missing)}")
    if extra:
        warns.append(f"{tag}: hashtags not in source (added?): {sorted(extra)}")
    # hashtag glued to following Japanese text
    for m in re.finditer(r"[#＃][A-Za-z0-9_]+(" + JA_CHAR + ")", tgt):
        errs.append(f"{tag}: hashtag runs into Japanese text and will absorb it: '{m.group(0)}…'")
    # numbers
    sn, tn = numbers(src), numbers(tgt)
    if sn != tn:
        warns.append(
            f"{tag}: number set differs. source-only={sorted((sn - tn).elements())} "
            f"target-only={sorted((tn - sn).elements())} (spelled-out numbers are OK)"
        )
    # emoji
    se, te = len(EMOJI_RE.findall(src)), len(EMOJI_RE.findall(tgt))
    if se != te:
        warns.append(f"{tag}: emoji count {se} → {te}")
    # translationese tells
    if "—" in tgt or "–" in tgt:
        warns.append(f"{tag}: em/en dash in Japanese copy (pattern #19)")
    n_anata = tgt.count("あなた")
    if n_anata:
        warns.append(f"{tag}: あなた ×{n_anata} (pattern #1). OK only if brand voice uses it")
    if "私たちは" in tgt:
        warns.append(f"{tag}: 私たちは (pattern #2)")
    for calque in ("を可能にします", "を可能にする", "たことはありますか", "準備はできていますか", "に会いましょう", "に値します"):
        if calque in tgt:
            warns.append(f"{tag}: calque shape '{calque}'")
    # register mixing (rough heuristic)
    sentences = re.split(r"[。！？!?\n]", tgt)
    polite = sum(1 for s in sentences if re.search(r"(です|ます|ません|ました|でした|ください)\s*$", s.strip()))
    plain = sum(1 for s in sentences if re.search(r"(だ|である|だった|じゃない|してみた)\s*$", s.strip()))
    if polite and plain:
        warns.append(f"{tag}: possible register mix ({polite} polite / {plain} plain endings)")
    # full-width digits
    if re.search(r"[０-９]", tgt):
        warns.append(f"{tag}: full-width digits present; use half-width")
    # Never list
    for term in banned:
        if term in tgt:
            errs.append(f"{tag}: glossary Never term used: '{term}'")
    # length
    if platform == "x":
        w = x_weight(tgt)
        if w > 280:
            warns.append(f"{tag}: X weighted length {w}/280 (info only; fine if the message needs it)")
        return w
    if platform in LIMITS and len(tgt) > LIMITS[platform]:
        warns.append(f"{tag}: {len(tgt)} chars > {platform} cap {LIMITS[platform]} (info only)")
    return len(tgt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("target")
    ap.add_argument("--glossary")
    ap.add_argument("--platform", help="override platform for all posts")
    a = ap.parse_args()

    src, tgt = parse_posts(a.source), parse_posts(a.target)
    banned = load_never(a.glossary) if a.glossary else []
    errs, warns = [], []

    for pid in sorted(set(src) - set(tgt), key=lambda p: int(p[1:])):
        errs.append(f"{pid}: missing from target")
    for pid in sorted(set(tgt) - set(src), key=lambda p: int(p[1:])):
        errs.append(f"{pid}: in target but not in source")

    for pid in sorted(set(src) & set(tgt), key=lambda p: int(p[1:])):
        platform = a.platform or tgt[pid]["platform"] or src[pid]["platform"]
        n = check_text(pid, "copy", src[pid]["copy"], tgt[pid]["copy"], platform, banned, errs, warns)
        print(f"{pid} [{platform or '?'}] copy length: {n}" + (" (X weighted)" if platform == "x" else " chars"))
        for i, alt in enumerate(tgt[pid]["alts"], 1):
            check_text(pid, f"alt{i}", src[pid]["copy"], alt, platform, banned, errs, warns)

    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    print(f"\n{len(src)} posts checked: {len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
