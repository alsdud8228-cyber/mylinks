"""멀티링크 페이지에 상품 링크 블럭을 추가한다 (최신이 맨 위, 품번 자동 증가).

사용:
    python add_link.py --title "갤럭시 Z 폴드8" --url "https://link.coupang.com/a/xxxx" --note "한줄 코멘트" --thumb "https://...jpg"

--num 을 생략하면 기존 최대 품번+1 (001, 002, ...) 자동 부여.
--push 를 붙이면 git commit + push까지 수행 (GitHub Pages 자동 반영).
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

LINKS = Path(__file__).parent / "links.json"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--thumb", default="", help="상품 썸네일 이미지 URL")
    p.add_argument("--num", default="", help="품번 (생략 시 자동 증가)")
    p.add_argument("--push", action="store_true", help="git commit + push")
    args = p.parse_args()

    data = json.loads(LINKS.read_text(encoding="utf-8"))

    if any(l["url"] == args.url for l in data["links"]):
        print(f"이미 등록된 링크: {args.url}")
        sys.exit(0)

    num = args.num
    if not num:
        nums = [int(l["num"]) for l in data["links"] if str(l.get("num", "")).isdigit()]
        num = f"{(max(nums) + 1) if nums else 1:03d}"

    data["links"].insert(0, {
        "num": num,
        "title": args.title,
        "url": args.url,
        "note": args.note,
        "thumb": args.thumb,
        "date": datetime.date.today().isoformat(),
    })
    LINKS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"추가됨: [{num}] {args.title} (총 {len(data['links'])}개)")

    if args.push:
        repo = Path(__file__).parent
        subprocess.run(["git", "add", "links.json"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", f"link: [{num}] {args.title}"], cwd=repo, check=True)
        subprocess.run(["git", "push"], cwd=repo, check=True)
        print("push 완료 — GitHub Pages에 곧 반영됩니다.")


if __name__ == "__main__":
    main()
