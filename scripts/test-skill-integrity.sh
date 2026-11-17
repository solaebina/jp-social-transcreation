#!/usr/bin/env bash
# Integrity checks for the jp-social-transcreation skill. No external deps beyond python3.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"
pass=0; fail=0
ok()  { echo "  ok   $1"; pass=$((pass+1)); }
bad() { echo "  FAIL $1"; fail=$((fail+1)); }
chk() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }

echo "Files"
for f in SKILL.md README.md \
         agents/intent-analyst.md agents/term-researcher.md agents/transcreator.md agents/native-reviewer.md \
         references/english-framing-patterns.md references/japanese-social-conventions.md \
         references/meaning-map-schema.md references/glossary-template.md references/review-feedback-schema.md \
         references/anti-fabrication-checklist.md references/exemplar.md scripts/check_post.py \
         agents/voice-analyst.md references/voice-profile-schema.md scripts/voice_stats.py; do
  chk "$f exists" "[ -s '$DIR/$f' ]"
done

echo "SKILL.md"
chk "frontmatter name" "head -5 '$DIR/SKILL.md' | grep -q '^name: jp-social-transcreation'"
chk "frontmatter description" "head -5 '$DIR/SKILL.md' | grep -q '^description:'"
chk "under 500 lines" "[ \$(wc -l < '$DIR/SKILL.md') -lt 500 ]"
for ref in $(grep -oE '(agents|references|scripts)/[a-z_-]+\.(md|py|sh)' "$DIR/SKILL.md" | sort -u); do
  chk "referenced $ref exists" "[ -e '$DIR/$ref' ]"
done

echo "Checker behaviour"
T=$(mktemp -d)
cat > "$T/s.md" <<'EOF'
### P1 [x]
```copy
Meet X1. Up to 7,300MB/s. https://example.com/x1 #Northwind
```
EOF
cat > "$T/good.md" <<'EOF'
### P1 [x]
```copy
X1が登場。最大7,300MB/s。
https://example.com/x1
#Northwind
```
EOF
cat > "$T/bad.md" <<'EOF'
### P1 [x]
```copy
あなたのX1に会いましょう。最大7,300MB/s。
https://example.com/x2
#Northwindで検索
```
EOF
printf '| a | b | Never |\n|---|---|---|\n| meet | 登場 | ❌ に会いましょう |\n' > "$T/g.md"
chk "good copy exits 0" "python3 -I '$DIR/scripts/check_post.py' '$T/s.md' '$T/good.md' --glossary '$T/g.md' >/dev/null"
out=$(python3 -I "$DIR/scripts/check_post.py" "$T/s.md" "$T/bad.md" --glossary "$T/g.md"; echo "rc=$?")
chk "bad copy exits 1"            "echo \"\$out\" | grep -q 'rc=1'"
chk "detects URL change"          "echo \"\$out\" | grep -q 'URL mismatch'"
chk "detects glued hashtag"       "echo \"\$out\" | grep -q 'absorb'"
chk "detects Never term"          "echo \"\$out\" | grep -q 'Never term'"
chk "warns on あなた"              "echo \"\$out\" | grep -q 'あなた'"
echo "Voice stats behaviour"
printf '新色が登場です！✨\n詳しくはこちら👇\n---\n今週もお疲れさまでした！😊\n---\nイベント開催決定です！🎉\n' > "$T/v.md"
vout=$(python3 -I "$DIR/scripts/voice_stats.py" "$T/v.md" --compare "$T/bad.md")
chk "profiles samples"            "echo \"\$vout\" | grep -q 'Voice stats: 3 sample posts'"
chk "flags off-voice あなた"       "echo \"\$vout\" | grep -q 'あなた: never used'"
rm -rf "$T"

echo; echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
