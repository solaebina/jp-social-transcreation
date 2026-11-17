# Exemplar: one post, source to final

Brief: X, brand account, R1 friendly です・ます, consumer PC gamers, keep brand/product names and hashtags in English.

## Source

```copy
Ever wondered why your laptop slows down after a year? 🤔
It's not you — it's your storage.

Meet the Northwind X1 SSD: up to 7,300MB/s read speeds, so your games load before you can grab a snack. 🎮

Upgrade today → https://example.com/x1

#Northwind #PCGaming
```

## ❌ What word-for-word output looks like (fails the checker)

```
なぜあなたのラップトップが1年後に遅くなるのか疑問に思ったことはありますか？🤔
それはあなたではありません — それはあなたのストレージです。

Northwind X1 SSDに会いましょう：最大７，３００MB/sの読み込み速度で、あなたがスナックを取る前にあなたのゲームがロードされます。🎮
```

Every sentence is English structure wearing Japanese words: あなた five times, 疑問に思ったことはありますか (#4), それはXではありません—それはYです (#19), に会いましょう (#11), full-width digits, ラップトップ where Japanese retail says ノートPC, and a passive ロードされます.

## Meaning map (abridged)

| Unit | Function | Payload | Effect | Framing | Keep close |
|---|---|---|---|---|---|
| U1 | hook | laptops slow down after about a year; there's a reason | "that's me, why?" | #4, #1 | laptop, slow down, year |
| U2 | reframe | not the user's fault; storage is the cause | relief + curiosity | #19, #1 | storage |
| U3 | claim + proof | X1 SSD; **up to** 7,300MB/s **read**; games load before you can grab a snack | "that's fast", playful | #11, #1 | SSD, read speed, games, load, snack |
| U4 | cta + link | go upgrade (soft immediacy, "today") | click | arrow | upgrade |
| U5 | hashtags | #Northwind #PCGaming | — | — | invariant |

## ✅ Final (checker passes)

```copy
ノートPC、買って1年ほどで重くなってきていませんか？🤔
実はその原因、使い方ではなくストレージなんです。

そこで、Northwind X1 SSD。
最大7,300MB/sの読み込み速度で、おやつを取りに行く前にゲームのロードが完了🎮

さっそくアップグレード👇
https://example.com/x1

#Northwind #PCGaming
```

## Why each choice

- **U1:** "Ever wondered why…" became a situational question, 〜ていませんか？. The "why" moves into U2 as 実はその原因, so the hook still sets up an answer. 買って makes explicit what "after a year" means (a year of ownership). No new claim.
- **U2:** "It's not you" → 使い方ではなく. In Japanese, "it's not you" lands as "it's not how you use it". The em-dash reveal became 〜ではなく + 〜なんです, the Japanese way to reveal a cause.
- **U3:** "Meet X:" → そこで、X。, a native pivot from problem to product. 最大 keeps "up to". 読み込み速度 keeps "read" (not just 速度, which would imply write speed too). snack → おやつ keeps the source's image, because it works in Japan. "before you can grab" → 取りに行く前に. The line closes on the 体言止め 完了 instead of a third ます.
- **U4:** "today" → さっそく gives the soft immediacy without the invented urgency of 今だけ or 今がチャンス. → became 👇 with the URL on its own line (Japanese X convention). The checker warns that the emoji count went from 2 to 3; that warning is expected and explained here.
- **Vocabulary kept:** laptop (ノートPC), slow (重く), year (1年), storage, SSD, read speed, games, load, snack (おやつ), upgrade. Only the frames changed.
- **Length:** sized to the message. Two lines of problem, one pivot, one proof line, a CTA. Nothing padded to match the English, nothing squeezed out to hit a count.

## Notes that would go to the client

- おやつ is playful. If the brand is more premium, 軽食 is the fallback, but it's stiffer.
- Suggested optional Japanese hashtag: #PCゲーム (not added to the copy).
