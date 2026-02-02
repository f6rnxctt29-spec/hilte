from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()
# status.py -> app/routers/status.py; parents[3] points to /hilte
PROGRESS_FILE = Path(__file__).resolve().parents[3] / 'PROGRESS.md'

@router.get('/status')
def status():
    """Return progress counts from PROGRESS.md.

    Counts:
    - Done/In progress: markdown bullets '- '
    - Next: accepts bullets and numbered list items like '1)'
    """
    try:
        text = PROGRESS_FILE.read_text(encoding='utf-8')
    except Exception:
        return {"done": 0, "inprogress": 0, "next": 0}

    done_count = 0
    in_count = 0
    next_count = 0

    section = None
    for raw in text.splitlines():
        l = raw.strip()
        if l.startswith('## Done'):
            section = 'done'
            continue
        if l.startswith('## In progress'):
            section = 'inprogress'
            continue
        if l.startswith('## Next'):
            section = 'next'
            continue
        if l.startswith('##'):
            section = None
            continue

        if not section:
            continue

        is_bullet = l.startswith('- ')
        is_numbered = len(l) > 2 and l[0].isdigit() and (l[1] == ')' or (l[1].isdigit() and ')' in l[:4]))

        if section in ('done', 'inprogress') and is_bullet:
            if section == 'done':
                done_count += 1
            else:
                in_count += 1
        elif section == 'next' and (is_bullet or is_numbered):
            next_count += 1

    return {"done": done_count, "inprogress": in_count, "next": next_count}
