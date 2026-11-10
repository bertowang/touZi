#!/usr/bin/env bash
# 批量运行全书 Python 分析示例并生成 fig/*.svg；只用标准库，不需要安装任何依赖。
# 用法:
#   ./tools/run_python.sh
#   ./tools/run_python.sh part3/16-candlestick/code/16-candle.py
#   PYTHON=/usr/bin/python3 ./tools/run_python.sh
set -u
cd "$(dirname "$0")/.." || exit 1

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  printf '找不到 Python 解释器: %s\n' "$PYTHON" >&2
  exit 1
fi

list=()
if [ "$#" -gt 0 ]; then
  list=("$@")
else
  while IFS= read -r f; do
    list+=("$f")
  done < <(find . -path '*/code/*.py' -type f | sort)
fi

if [ "${#list[@]}" -eq 0 ]; then
  printf '没有找到 code/*.py，请先运行 python3 tools/build_book.py --force 与 python3 tools/extract_code.py\n' >&2
  exit 1
fi

pass=0
fail=0
for f in "${list[@]}"; do
  out=$("$PYTHON" "$f" 2>&1)
  if [ $? -eq 0 ]; then
    pass=$((pass + 1))
    last=$(printf '%s\n' "$out" | tail -n 1)
    printf 'OK   %-58s | %s\n' "$f" "$last"
  else
    fail=$((fail + 1))
    printf 'FAIL %s\n' "$f"
    printf '%s\n' "$out" | head -n 10
  fi
done

printf '\n共 %d 个脚本：通过 %d，失败 %d\n' "${#list[@]}" "$pass" "$fail"
[ "$fail" -eq 0 ]
