# jp-social-transcreation

A multi-agent Claude skill that transcreates English social media copy into Japanese that reads as natively written. The structure follows [senshinji/claude-translation-skill](https://github.com/senshinji/claude-translation-skill), with the roles redesigned for short persuasive copy instead of long documents.

## Why it's built this way

Word-for-word output happens when the writer works through the English sentence by sentence. This pipeline breaks that habit: an **Intent Analyst** first records what every part of a post is *doing* (its job, facts, intended effect, the English-specific framing, and the vocabulary to keep). The **Transcreator** then writes Japanese from that map, so English sentence structure never becomes the template. The source's concrete words survive (laptop → ノートPC, snack → おやつ). Only the frame around them changes.

## Pipeline

| Phase | Agent | Model | Output |
|---|---|---|---|
| 0 | Team Lead | — | `brief.md`, `source.md` |
| 1 | Intent Analyst ∥ Term Researcher ∥ Voice Analyst | sonnet | `meaning-map.md`, `glossary.md`, `voice-profile.md` |
| 2 | Transcreator | opus | `first-pass.md` |
| 3 | Native Reviewer: blind read → fidelity → back-translation | opus | `review-feedback.md` |
| 4 | Transcreator (revision) | opus | `final.md` |
| 5 | Lead: checker + read-aloud + delivery | — | paste-ready copy + notes |

Jobs of 1–3 posts run in **Lite mode**: the lead does every step inline, but still writes the meaning map first.

## Matching your account's voice

Give it past Japanese posts from the account and the output will sound like that account: same endings, openers, CTA phrasing, emoji habits, punctuation and layout.

- **Paste them** into the request, separated by `---`, or
- **Attach a file:** .md/.txt (posts separated by `---`), or an X/Instagram analytics export (.csv/.xlsx with a "Post text"-style column), or
- **Keep them in your project** as `voice-samples/`. The profile is saved to `voice-profiles/<account>.md` and reused, and new samples refine it.

10–30 recent posts per platform works best. The samples set the tone only: their content, claims and sign-offs never get copied into new posts unless the source has the same element.

## Layout

```
SKILL.md                              orchestration (Team Lead)
agents/                               one prompt per role
references/english-framing-patterns.md  26 English framings → Japanese, with calques to avoid
references/japanese-social-conventions.md register, length guidance, hashtag mechanics, katakana policy, false friends
references/exemplar.md                one post worked end to end
references/*-schema.md, glossary-template.md, anti-fabrication-checklist.md
scripts/check_post.py                 invariant + translationese checker (URLs, @, #, numbers, length report, Never list)
scripts/voice_stats.py               measures house style from past posts; --compare flags off-voice copy
scripts/test-skill-integrity.sh       self-test
```

## Install

```bash
cp -r jp-social-transcreation ~/.claude/skills/
bash ~/.claude/skills/jp-social-transcreation/scripts/test-skill-integrity.sh
```

No Agent Teams flag is needed. It uses the standard Agent/subagent tool.

## Use

> Transcreate these 6 X posts into Japanese for our brand account: …

Keep a `glossary.md` in your project. Each job proposes new rows, and once you ratify them they bind every future job. The **Never** column turns past mistakes into automated checks.

## What was taken from which source

| Source | Kept | Dropped |
|---|---|---|
| transcreate skill | the native-reader test, the five traps, decide-before-writing, the glossary with a Never column, add/drop nothing, reporting new terms | document-structure parity, RTL notes |
| translating-marketing | invariant vs adaptable classification, claim strength, CTA = actual next action, no invented urgency, back-translation for sensitive claims | multi-skill routing and ownership apparatus |
| prompting tips | specifying register, connotation flags kept separate from the copy, back-translation, alternatives for wordplay, the "does this read translated?" self-check, a native review before publishing | the safety-content advice, the parenthetical source terms |
| translator skill | markdown and code preservation, a technical-term policy | MDX spacing, other languages; it had no Japanese guidance, so that was written fresh |
