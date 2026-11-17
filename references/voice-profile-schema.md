# voice-profile.md schema

Save it in the project as `voice-profiles/<account>.md` so later jobs reuse it. Each job copies it into the workspace, and the Voice Analyst updates the project copy when new samples arrive.

```markdown
# Voice profile: <account> (<platforms>)
Samples: 24 posts (X 18, Instagram 6), 2026-03 → 2026-11. Confidence: high.
Last updated: 2026-11-17

## Persona and register
- Speaker: the brand's social team, friendly and slightly playful (中の人 feel on X, more polished on IG)
- Register: R1 friendly です・ます. Casual particles 〜ね／〜よ in about 1 in 3 posts. Never plain だ.
- Addresses followers as: 皆さん (sometimes); usually no address at all

## Sentence endings
- Mix: polite 55% / 体言止め 30% / question 15%
- Favourite forms: 〜です！ / 〜ですよね / 〜しました🎉 / noun + ！
- e.g. 「新色、ついに登場です！」「もう試しましたか？」

## Hooks and openers
- Announcements open with 【】: 【新発売】【お知らせ】 (9/10 announcements)
- Tips open with a question: 「〜って知ってましたか？」

## CTA
- Default: 詳しくはこちら👇 + URL on its own line
- IG: プロフィールのリンクからチェックしてね✨
- Never: 今すぐ, ぜひ more than once

## Emoji
- 1–3 per post, almost always at the end of a line
- Uses: ✨🎉👇📣😊  Never: 🔥💯🙏, kaomoji

## Punctuation and spacing
- Full-width ！？. Uses … (1 in 4 posts). Uses 〜 for ranges only.
- No space between Japanese and Latin text: 「X1 SSDが登場」

## Vocabulary
- Prefers native words: 更新 (not アップデート), 体験, お知らせ
- Product names in English, followed by が/を directly
- Recurring phrases: 「ぜひチェックしてみてください」

## Layout
- 4–7 lines; one idea per line; blank line before the CTA and before hashtags
- Hashtags: 1–2, always on the last line, brand tag first

## Account habits (not auto-inserted)
- Friday posts end with 「今週もお疲れさまでした！」
- Always includes #BrandName

## House exceptions to skill defaults
- none / "uses あなた in beauty-tip posts (5/6): allowed in that post type only"

## Never does
- あなた (outside the exception above), 私たち, ！！, ALL CAPS English, em dashes

## Evidence (voice_stats.py)
<pasted output>
```

Precedence when writing: **glossary > voice profile > english-framing-patterns.md / japanese-social-conventions.md defaults.** None of these override the invariants or the add-nothing / drop-nothing rules.
