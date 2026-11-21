# dsu-gapyeong.github.io
DSU 한국가평분교(두나미스 소피아 대학원) 공식 홈페이지

- 주소: https://dsu-gapyeong.github.io/
- 소식 글: `posts/` 폴더의 .md 파일
- 갤러리: `gallery/` 폴더의 .md 파일 + `images/` 사진

## 유튜브 게시물 자동 수집
- `.github/workflows/sync-youtube-posts.yml` 이 매일 한국시간 아침 7시에 `scripts/sync_youtube_posts.py` 를 실행합니다.
- 채널 '게시물' 탭의 새 글을 `posts/` 에, 포스터 이미지를 `images/` 에 저장합니다.
- 바로 실행하려면 GitHub 저장소 → Actions → "유튜브 게시물 → 공지사항" → Run workflow.
