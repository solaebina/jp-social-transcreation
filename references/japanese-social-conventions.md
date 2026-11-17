# Japanese Social Conventions

## 1. Register (choose one per platform per campaign, then hold it)

| Register | Feel | Default for | Example ending |
|---|---|---|---|
| **R1 friendly です・ます** | warm, polite, approachable; mixes in 体言止め and 〜ね / 〜よ | brand accounts on X, Instagram, Threads, Facebook | 〜しました！ / 〜ですよね / チェックしてみてください |
| **R2 formal です・ます** | corporate; 〜いたします, 当社, お知らせいたします | corporate LinkedIn, IR, partnership news | 〜を締結いたしました。 |
| **R3 plain だ・である / casual** | persona voice, peer-to-peer | personal or persona accounts, TikTok | 〜だった / 〜してみた / 〜じゃない？ |

CTAs follow the register: R1 〜してね / 〜してみてください, R2 〜ください, R3 〜してみて.
Mixing registers inside one post is the loudest tell of machine output.

## 2. Length (informational)

Length follows the message. These caps are reference only: the checker reports length and never fails a post for it.

| Platform | Limit | Notes |
|---|---|---|
| X (free) | **280 weighted**: Japanese characters count 2, so about 140 Japanese characters. Each URL counts 23. Each emoji counts 2. | `check_post.py --platform x` computes this. |
| Instagram | 2,200 characters; about the first 2 lines show before "…続きを読む" | Front-load the hook in line 1. Maximum 30 hashtags. |
| LinkedIn | 3,000 characters; about 2–3 lines show before "…もっと見る" | |
| Threads | 500 characters | |
| Facebook | effectively unlimited; about 3 lines visible | |
| TikTok caption | 4,000 characters; the first line or so is visible | |

Japanese is denser than English, so a natural Japanese post is often shorter than its source. That's expected. Don't pad to match, and don't compress to hit a count.

## 3. Punctuation and characters
- Japanese punctuation is full-width: 、。！？「」『』【】（）. Pick one style for ！？ (full-width is the default) and use it throughout.
- Digits and Latin letters are **half-width**: 7,300MB/s, 50%OFF, AI, SSD. Never ７，３００.
- Use 「」 for quoted or named things and 『』 for titles of works. Use 【】 for label headers (【新発売】, 【お知らせ】).
- Range: 〜. Prices: 1,980円 (in JP-market copy), or keep $ if the offer is in USD. **Never convert currency.** It's an invariant.
- No em dashes (—). Use 、, a line break, or 〜ではなく.
- Ellipsis: … (not ...). Use it sparingly, typically after a relatable situation.

## 4. Line breaks and layout
- Japanese posts break lines at meaning boundaries more often than English posts do. One idea per line is normal on X and Instagram.
- Put a blank line before the CTA block and before the hashtag block.
- Put the URL on its own line.
- Emoji usually go **at the end of a line or clause**, not mid-clause.

## 5. Hashtags, URLs, @mentions: the mechanics
- **A hashtag absorbs any Japanese text that directly follows it.** `#Northwindで検索` becomes the tag "Northwindで検索". Always follow a hashtag with a space, a line break, or the end of the post. (`check_post.py` flags this.)
- Japanese hashtags work (#PCゲーム). Suggest them separately, and never add them to the copy unasked.
- Put a space or line break before a URL that follows Japanese text. Some clients mis-link URLs glued to full-width characters.
- Keep @mentions byte-exact, with a space or line break after.

## 6. Katakana policy (keeping close to the English vocabulary)
Keep the source's word, rendered in the form Japanese readers of **this platform and category** actually use. Decide in this order:

1. **The glossary says** → use it.
2. **Brand or product name** → keep it as the brand writes it in Japan (usually English).
3. **An established loanword in everyday use** → katakana: アップグレード, ストレージ, イベント, キャンペーン, アプリ, チーム, ツール, クリエイター, ワークフロー (B2B), スタートアップ.
4. **The katakana would be jargon for this audience** → a native word or kanji compound: experience → 体験 (not エクスペリエンス), solution → 解決策 (consumer) / ソリューション (B2B is fine), insight → 気づき (consumer) / インサイト (marketing B2B), journey → 道のり / 過程.
5. **Acronyms and terms of art the audience reads in English** → keep English: AI, SSD, SaaS, API, NFT.
6. **No settled form** → keep the English, or describe it in plain Japanese. **Never coin a katakana phrase** (アンロック・ユア・ポテンシャル ❌).

Overusing katakana is its own kind of translationese. Two or three unfamiliar katakana words in one line → rewrite the line.

## 7. False friends (wasei-eigo and shifted meanings)
These are where "keep close to the English" goes wrong. Check every katakana word against this list.

| English | Katakana | What it means in Japanese | Use instead |
|---|---|---|---|
| claim (assert) | クレーム | a **complaint** | 主張 / うたう |
| smart (clever) | スマート | slim, stylish, sleek | 賢い / スマート only for devices (スマート家電) |
| tension (stress) | テンション | energy, hype level (テンション上がる = excited) | 緊張 / 張り |
| naive | ナイーブ | sensitive, delicate (positive) | 世間知らず / 甘い |
| mansion | マンション | condo/apartment | 豪邸 |
| challenge (problem) | チャレンジ | a positive attempt | 課題 (for "a challenge we face") |
| unique | ユニーク | quirky, funny | 唯一の / 独自の |
| fight! (cheer) | ファイト | fine as a cheer, never "combat" | — |
| consent | コンセント | electrical **outlet** | 同意 |
| reform (policy) | リフォーム | home renovation | 改革 |
| cunning | カンニング | cheating on a test | ずる賢い |
| campaign (political) | キャンペーン | usually a sales promotion | 選挙運動 (if political) |
| service | サービス | can mean free / on the house | 提供 / サービス (context) |
| viking | バイキング | all-you-can-eat buffet | — |

## 8. Things Japanese social copy does that English doesn't
- 【】 headers for announcements: 【新発売】【本日発売】【お知らせ】
- Softening devices such as 〜してみてください, 〜かも, ぜひ. Use ぜひ at most once per post.
- 体言止め as a rhetorical close: 毎日のワークフローを、もっとスムーズに。
- Seasonal awareness (季節感). Use it only when the source has a seasonal element; don't add it.
