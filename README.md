# dsu-gapyeong.github.io
DSU 한국가평분교(두나미스 소피아 대학원) 공식 홈페이지

- 주소: https://dsu-gapyeong.github.io/
- 소식 글: `posts/` 폴더의 .md 파일
- 갤러리: `gallery/` 폴더의 .md 파일 + `images/` 사진

## 세미나·집회 일정
`posts/` 글의 머리말에 아래 줄을 넣으면 홈페이지 '세미나 · 집회 일정' 칸에 나옵니다. 날짜가 지나면 자동으로 '지난 행사'로 내려갑니다.

```
event_date: 2027-01-12
event_end: 2027-01-15
event_time: "오전 10:00 ~ 오후 5:00"
event_place: "가평 드림힐링하우스"
```
- `event_date`: 행사 날짜 (필수)
- `event_end`: 여러 날 행사일 때 마지막 날 (선택)
- `event_time`, `event_place`: 시간, 장소 (선택)

## 유튜브 게시물 자동 수집
- `.github/workflows/sync-youtube-posts.yml` 이 매일 한국시간 아침 7시에 `scripts/sync_youtube_posts.py` 를 실행합니다.
- 채널 '게시물' 탭의 새 글을 `posts/` 에, 포스터 이미지를 `images/` 에 저장합니다.
- 바로 실행하려면 GitHub 저장소 → Actions → "유튜브 게시물 → 공지사항" → Run workflow.
