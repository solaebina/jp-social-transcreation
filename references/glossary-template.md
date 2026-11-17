# glossary.md template

The **Never** column is what makes this work. It records rejected renderings so they can't creep back in, and `check_post.py --glossary` fails if any of them appear in the copy. Write each banned form as `❌ form`, separated by `、`.

`status`: `ratified` = approved by a human, binding. `proposed` = decided during this job; list it in the final report for ratification.

```markdown
| Source term | Japanese | Never | Confidence | Source | Status |
|---|---|---|---|---|---|
| Northwind | Northwind | ❌ ノースウィンド | high | https://example.com/jp | ratified |
| X1 SSD | X1 SSD | ❌ X1エスエスディー | high | official JP product page | ratified |
| laptop | ノートPC | ❌ ラップトップ、❌ ノートブック | high | dominant JP retail usage | proposed |
| storage | ストレージ | ❌ 貯蔵 | high | JP PC media | proposed |
| read speed | 読み込み速度 | ❌ 読む速度、❌ リードスピード | high | JP SSD spec pages | proposed |
| link in bio | 詳しくはプロフィールのリンクから | ❌ バイオのリンク | high | JP IG convention | ratified |
| unlock (potential) | 引き出す | ❌ 解き放つ、❌ アンロック | medium | — | proposed |
| claim (assert) | うたう / 主張 | ❌ クレーム | high | false friend | ratified |
```

Notes:
- Keep banned terms out of changelogs and report prose inside the workspace, or the guard will flag itself.
- One row per term. If the rendering depends on context (B2B vs consumer), write both in the Japanese column with the condition, e.g. `ソリューション (B2B) / 解決策 (consumer)`.
