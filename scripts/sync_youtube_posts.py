"""유튜브 채널 '게시물' 탭의 새 글을 공지사항(posts/*.md)으로 옮긴다.

GitHub Actions 가 하루에 한 번 실행한다 (.github/workflows/sync-youtube-posts.yml).
- 채널 게시물 페이지를 한 번 열어, 화면에 처음 보이는 최신 글들만 확인한다.
- 이미 옮긴 글은 .md 의 `source:` 줄(유튜브 게시물 주소)로 알아보고 건너뛴다.
- 새 글은 포스터 이미지를 images/ 에 저장하고, 게시물에 적힌 글을 본문으로 쓴다.
- 날짜는 유튜브가 '1일 전'처럼 대략만 알려 주므로, 수집한 날짜(한국시간)로 적는다.

사용법:
  python scripts/sync_youtube_posts.py            # 실제로 파일을 만든다
  python scripts/sync_youtube_posts.py --dry-run  # 무엇을 만들지 보여 주기만 한다
"""
import io, json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

CHANNEL_ID = 'UCr9PGzwTyw00UPQktjLECMg'
POSTS_URL = f'https://www.youtube.com/channel/{CHANNEL_ID}/posts?hl=ko&gl=KR'
POST_LINK = 'https://www.youtube.com/post/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, 'posts')
IMAGES_DIR = os.path.join(ROOT, 'images')
KST = timezone(timedelta(hours=9))
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Cookie': 'CONSENT=YES+1; SOCS=CAI',  # 해외 서버에서 쿠키 동의 화면이 뜨는 것을 막는다
}

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def find_all(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from find_all(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from find_all(v, key)


def runs_text(t):
    if not t:
        return ''
    if 'runs' in t:
        return ''.join(r.get('text', '') for r in t['runs'])
    return t.get('simpleText', '')


def read_posts_page():
    html = fetch(POSTS_URL).decode('utf-8', 'replace')
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', html, re.S)
    if not m:
        raise SystemExit('유튜브 게시물 페이지에서 데이터를 찾지 못했습니다 (페이지 구조가 바뀌었을 수 있음).')
    data = json.loads(m.group(1))
    posts, seen = [], set()
    for p in find_all(data, 'backstagePostRenderer'):
        pid = p.get('postId')
        if not pid or pid in seen:
            continue
        seen.add(pid)
        images = []
        for img in find_all(p.get('backstageAttachment') or {}, 'backstageImageRenderer'):
            th = img.get('image', {}).get('thumbnails', [])
            if th:
                images.append(re.sub(r'=s\d+.*$', '=s2048', th[-1]['url']))
        posts.append({'id': pid, 'text': runs_text(p.get('contentText')).strip(), 'images': images})
    return posts


def known_post_ids():
    ids = set()
    for name in os.listdir(POSTS_DIR):
        if name.endswith('.md'):
            text = open(os.path.join(POSTS_DIR, name), encoding='utf-8').read()
            ids.update(re.findall(r'youtube\.com/post/([\w-]+)', text))
    return ids


def make_title(text):
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), '')
    # "#환우를 위한 기도 1 #이윤호목사 #DSU" → "환우를 위한 기도 1"
    # "세미나 안내 #DSU"                  → "세미나 안내"
    cut_from = 1 if first.startswith('#') else 0
    pos = [m.start() for m in re.finditer(r'#', first)]
    if len(pos) > cut_from:
        first = first[:pos[cut_from]]
    clean = re.sub(r'\s+', ' ', first.replace('#', '')).strip()
    if not clean:
        return 'DSU 한국가평분교 새 소식'
    return clean if len(clean) <= 60 else clean[:58].rstrip() + '…'


def save_image(url, out_name):
    raw = fetch(url)
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        if im.height > 1920:
            im = im.resize((round(im.width * 1920 / im.height), 1920), Image.LANCZOS)
        im.save(os.path.join(IMAGES_DIR, out_name), 'JPEG', quality=86, optimize=True)
    except ImportError:
        open(os.path.join(IMAGES_DIR, out_name), 'wb').write(raw)


def yaml_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    dry = '--dry-run' in sys.argv
    posts = read_posts_page()
    known = known_post_ids()
    new = [p for p in posts if p['id'] not in known]
    print(f'게시물 {len(posts)}개 확인, 이미 있는 글 {len(posts) - len(new)}개, 새 글 {len(new)}개')
    now = datetime.now(KST)
    # 화면에는 최신 글이 위에 있다. 오래된 것부터 만들어 순서(시각)를 맞춘다.
    for i, p in enumerate(reversed(new)):
        when = now - timedelta(minutes=len(new) - i)
        short = p['id'][-8:]
        title = make_title(p['text'])
        image_name = f"yt-{now:%Y-%m-%d}-{short}.jpg" if p['images'] else ''
        print(f"  + {title} (이미지 {len(p['images'])}장)")
        if dry:
            continue
        if image_name:
            save_image(p['images'][0], image_name)
        body = p['text'] or ''
        lines = ['---', f'title: {yaml_str(title)}', f'date: {when.isoformat(timespec="seconds")}']
        if image_name:
            lines.append(f'image: images/{image_name}')
        lines += [f"source: {POST_LINK}{p['id']}", '---', body, '',
                  f"[유튜브 게시물 원문 보기]({POST_LINK}{p['id']})", '']
        fname = f"{now:%Y-%m-%d}-yt-{short}.md"
        open(os.path.join(POSTS_DIR, fname), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


if __name__ == '__main__':
    main()
