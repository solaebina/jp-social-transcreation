---
name: jp-social-transcreation
description: "Multi-agent pipeline that transcreates English social media copy (X, Instagram, LinkedIn, Facebook, Threads, TikTok captions) into natural Japanese. Maps what each part of a post is doing before writing, re-authors it in Japanese while keeping the source's concrete vocabulary, then has a blind native-reader review. Adapts to the account's voice when given past Japanese posts (pasted, files, or X/IG analytics exports). Use for 'translate this post to Japanese', 'transcreate', 'make this sound natural in Japanese', '翻訳調にしないで', 'SNS投稿を日本語に', 'match our past posts', 'use our Japanese tone', or reviewing a JP post that reads translated."
---

# English → Japanese Social Transcreation

The output passes one test only:

> A Japanese reader scrolling past this post would never suspect it was written in English first.

The method in one line: **work out what every part of the post is doing, then write that in Japanese from scratch, keeping the source's concrete words but none of its English sentence shapes.**

- **Free to change:** sentence structure, word order, how the post addresses the reader, rhetorical devices, idioms, punctuation, line breaks, sentence endings.
- **Not free to change:** the facts, the claims and how strong they are, the call to action, names, numbers, URLs, @mentions, hashtags, and the source's **concrete vocabulary**. A laptop stays a ノートPC. It does not become a "device" or a "smartphone".

## Architecture

```
                         Team Lead (you)
              Phase 0: brief + workspace + source.md
          ┌─────────────────────┼─────────────────────┐
  Intent Analyst (sonnet)  Term Researcher (sonnet)  Voice Analyst (sonnet)   ← Phase 1, parallel
  meaning-map.md           glossary.md               voice-profile.md + voice-anchors.md
          └─────────────────────┬─────────────────────┘    (only when samples exist)
                     Transcreator (opus)                              ← Phase 2
                     first-pass.md (meaning map → content; voice profile + anchors → tone)
                                │
                     Native Reviewer (opus)                           ← Phase 3
                     Pass A blind + voice match → Pass B fidelity → Pass C back-translation
                     review-feedback.md
                                │
                     Transcreator revises → final.md                  ← Phase 4
                                │
                     Lead: check_post.py + read-aloud → deliver       ← Phase 5
```

| Role | Prompt file | Model | Owns |
|---|---|---|---|
| Intent Analyst | `agents/intent-analyst.md` | sonnet | `meaning-map.md` |
| Term Researcher | `agents/term-researcher.md` | sonnet | `glossary.md` |
| Voice Analyst | `agents/voice-analyst.md` | sonnet | `voice-profile.md`, `voice-anchors.md` |
| Transcreator | `agents/transcreator.md` | opus | `first-pass.md`, `final.md` |
| Native Reviewer | `agents/native-reviewer.md` | opus | `review-feedback.md` |

Spawn each role with the Agent tool. In the prompt, pass the role file's full text, the workspace path, and the brief. Agent Teams are not required. If `SendMessage` is available, continue the Transcreator for Phase 4 so it keeps its own reasoning. If not, spawn a new Transcreator with `first-pass.md` and `review-feedback.md`.

### Lite mode (1–3 short posts)

The full team costs more than a single tweet is worth. For small jobs, the lead plays every role inline but **still produces each artifact in order**: meaning map, then glossary rows, then a voice profile if samples exist (run `voice_stats.py` and pick the anchors), then the draft, then a blind read of the Japanese alone, then fidelity. Do not skip the meaning map. Skipping it is how word-for-word output gets back in.

### Voice adaptation

When past Japanese posts from the account exist, the output must sound like **that account**, not like a generic brand. The Voice Analyst turns the samples into `voice-profile.md` (register, endings, hooks, CTA forms, emoji, punctuation, vocabulary preferences, layout, habits, never-does) and picks 3–6 `voice-anchors.md` posts that match this job's post types. The Transcreator writes **content** from the meaning map and **tone** from the profile and anchors. The Reviewer checks voice match blind and with `scripts/voice_stats.py --compare`.

**Precedence:** glossary > voice profile > this skill's general style defaults. The invariants and add-nothing/drop-nothing rules outrank all three. A house habit such as a Friday sign-off is never inserted unless the source has that unit or the brief says to apply it.

**Where samples come from**, checked in this order:
1. Posts pasted or attached in the request
2. `voice-profiles/<account>.md` and `voice-samples/` in the project
3. An X/Instagram analytics export (.csv/.xlsx with a post-text column)
4. Nothing: ask once ("Do you have 10–20 past Japanese posts from this account?"). Without samples, use the defaults and say so.

**Profiles persist.** Save the profile to `voice-profiles/<account>.md` in the project. Later jobs start from it, and new samples update it. 10–30 recent posts per platform is the sweet spot; fewer than 5 gives a low-confidence profile.

### Scaling

| Posts in job | Transcreators | Term Researchers | Reviewers |
|---|---|---|---|
| 1–3 | Lite mode | — | — |
| 4–15 | 1 | 1 | 1 |
| 16–40 | 1 per platform (max 3) | 1 | 1 |
| 40+ | 1 per platform/campaign (max 4) | 2 (names/products + platform language) | 1 |

Never split one campaign on one platform across transcreators, because the register drifts at the seams. Give every transcreator the same glossary and `references/exemplar.md`.

## Phase 0: Lead Preparation

### 0.1 Settle the brief

Infer everything you can from the request, the copy, and any project files: `CLAUDE.md`, brand voice guides, existing glossaries, `voice-profiles/`, `voice-samples/`, and earlier `*.ja.*` posts. Past Japanese posts from the account outrank everything else as a voice reference. When they exist, the register and spacing questions below are usually answered by them; don't ask. Ask in **one** compact question only about what you can't infer and what changes the output:

1. **Platform(s).** This decides the default register and conventions. Length follows the message, not the platform cap (`references/japanese-social-conventions.md`).
2. **Register.** One of: friendly です・ます (default for brand accounts), formal です・ます with 当社 (corporate LinkedIn), or plain/casual だ・である (persona accounts). One register per platform per campaign.
3. **Audience.** Consumer or B2B/tech. This decides how far katakana loanwords can go.
4. **What stays in English.** Product and brand names, hashtags, acronyms. Default: brand and product names, existing hashtags, and SSD/AI-type acronyms stay as written.
5. **Hashtags.** Default: keep the source hashtags exactly and list suggested Japanese hashtags separately. Never add them into the copy unasked.
6. **Spacing between Japanese and Latin text.** Default: no forced spaces, except where a hashtag, URL, or @mention needs one to work.
7. **Voice samples.** Past Japanese posts from this account? See Voice adaptation. Also record the account name for `voice-profiles/<account>.md`.

Write the answers to `brief.md`. If no one can answer, use the defaults, put them at the top of the final report, and continue.

### 0.2 Workspace

```
transcreation-work/<slug>/
  brief.md
  source.md          ← every post, in the post format below
  meaning-map.md     ← Intent Analyst
  glossary.md        ← Term Researcher (copy of the project glossary + new rows)
  voice-samples.md   ← past JP posts, separated by lines of ---
  voice-profile.md   ← Voice Analyst
  voice-anchors.md   ← Voice Analyst (3–6 model posts)
  first-pass.md      ← Transcreator
  review-feedback.md ← Native Reviewer
  final.md           ← Transcreator (revision)
```

**Post format.** Every copy file uses the same format so `scripts/check_post.py` can pair posts by ID:

````
### P1 [x]
```copy
<exact post text, line breaks preserved>
```
````

The tag in brackets is the platform: `x`, `instagram`, `linkedin`, `facebook`, `threads`, or `tiktok`. In `first-pass.md` and `final.md`, each post may also have one ```` ```alt ```` block and a `Notes:` paragraph after its `copy` block.

### 0.3 Contracts (pass these to every agent)

- **Add nothing.** No new claims, benefits, urgency, scarcity, emotions, or hashtags.
- **Drop nothing.** Every proposition in the meaning map appears in the Japanese.
- **Invariants are byte-exact:** URLs, @mentions, source hashtags, product and brand names, prices, dates, numbers, promo codes, and disclosures (#PR, #ad, 提供, and so on).
- **Claim strength is preserved.** "up to" → 最大, "may" → 場合があります. Never 必ず for "helps".
- **The CTA names the real next action.** "Sign up" is not 購入する.

## Phase 1: Parallel (Intent Analyst ∥ Term Researcher ∥ Voice Analyst)

Spawn all of them in the same turn. Skip the Voice Analyst only if there are no samples, or if a current `voice-profiles/<account>.md` exists and no new samples came with this job (then copy it, and its anchors, into the workspace).

- **Intent Analyst** → `meaning-map.md`: one entry per unit (hook, claim, proof, CTA, disclosure, and so on) with its information payload, intended effect, any English framing detected, the vocabulary to keep close, and the invariants.
- **Voice Analyst** → `voice-profile.md` + `voice-anchors.md`, grounded in `voice_stats.py` numbers and quoted examples.
- **Term Researcher** → `glossary.md`: brand, product, and feature names checked against official Japanese sources, platform-standard UI language, katakana-versus-native decisions, false friends, and a **Never** column.

## Phase 2: Transcreator

Spawn after all Phase 1 agents finish. It writes Japanese from the meaning map, not by working through the English sentences, and in the voice of the profile and anchors. It writes `first-pass.md` with the copy for each post, at most one alternative (only where a hook, pun, or idiom genuinely forks), and short decision notes.

## Phase 3: Native Reviewer

The reviewer runs three passes in this order:

- **Pass A, blind:** it reads only the Japanese and marks every pause, every "this sounds translated" moment, every あなた, every abstract noun subject, every mismatched sentence ending. Then it reads the voice anchors and asks whether each new post could sit in the same feed unnoticed, and runs `voice_stats.py --compare`.
- **Pass B, fidelity:** it checks against the meaning map and glossary for additions, omissions, claim strength, the CTA, and invariants, and runs `scripts/check_post.py`.
- **Pass C, back-translation:** for every quantified, comparative, health, financial, or guarantee claim, it back-translates the Japanese literally into English next to the source.

If the `jp-sns-copy-checker` skill is installed, the reviewer may run it as an extra opinion during Pass A. Its findings feed the review, but it does not replace the review.

Output: `review-feedback.md` with Critical, Major, and Minor issues per post (`references/review-feedback-schema.md`).

## Phase 4: Revision

The Transcreator applies every Critical and Major fix, and the Minor fixes it agrees with. Where it disagrees, it says why in the post's `Notes:`. It writes `final.md`. A second review round happens only if there were Critical issues.

## Phase 5: Lead Validation and Delivery

1. If there is a voice profile: `python3 scripts/voice_stats.py transcreation-work/<slug>/voice-samples.md --compare transcreation-work/<slug>/final.md`. Every deviation is either fixed or intended (the source asked for it).
2. `python3 scripts/check_post.py transcreation-work/<slug>/source.md transcreation-work/<slug>/final.md --glossary transcreation-work/<slug>/glossary.md` must exit 0, or every remaining warning must be explained.
3. Read each final post aloud in your head **without looking at the English**. Rewrite any sentence that makes you pause.
4. Spot-check every number and URL against the source by eye.
5. Deliver. Lead with the paste-ready copy:

```
P1 (X)
<final Japanese copy>

Alt (if any): <alt> — when to prefer it

Notes: connotation or tone flags, separate from the copy (e.g. "おやつ reads playful; use 軽食 if the brand is more serious")
```

Then list:

- Glossary terms decided in this job that need ratifying. This is the most valuable part of the report.
- Register and defaults assumed, if they weren't specified.
- Voice: which profile was used (samples, confidence), any house habits deliberately left out, and changes saved to `voice-profiles/<account>.md`.
- Back-translation table for sensitive claims.
- Anything in the source that looked wrong or self-contradictory. Fix it in neither language without asking, and flag it.
- Suggested Japanese hashtags, listed as optional and kept out of the copy.

Recommend a native-speaker check before publishing customer-facing posts. Say it in one line, not as a disclaimer paragraph.

## References

- `references/english-framing-patterns.md`: the core playbook of English-specific framings, why they read as translated, and what to write instead
- `references/japanese-social-conventions.md`: platform registers, limits, punctuation, line breaks, hashtag mechanics, katakana policy, false friends
- `references/meaning-map-schema.md`: Intent Analyst output format
- `references/glossary-template.md`: glossary with the Never column
- `references/review-feedback-schema.md`: Reviewer output format
- `references/anti-fabrication-checklist.md`: additions and omissions to hunt for
- `references/exemplar.md`: one fully worked post from source to final, given to every Transcreator
- `references/voice-profile-schema.md`: Voice Analyst output format and precedence
- `scripts/voice_stats.py`: measures house style from samples (md/txt/csv/xlsx); `--compare` flags off-voice copy

## Rules

- Map meaning first, write second. Never edit English word order into Japanese.
- Keep the source's concrete nouns and key terms. Change only the frame around them.
- Never invent a katakana term or a Japanese coinage. Keep the English word or describe it.
- One register per platform per campaign, held to the last line.
- Length fits the message: as long as the content needs, never padded, never compressed to hit a count.
- Nothing added, nothing dropped, every invariant byte-exact.
- The project glossary outranks this skill. Add a term to it before using it.
- When past posts exist, sound like the account: profile and anchors decide tone, the meaning map decides content.
- `check_post.py` passing is the floor. The blind read is the real check.
