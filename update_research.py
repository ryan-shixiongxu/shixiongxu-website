"""Update verified OpenAlex paper records and optional AI summaries.

Environment: OPENALEX_API_KEY; optional OPENAI_API_KEY and OPENAI_MODEL.
Summaries describe supplied abstracts only. No keys reach site visitors.
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'papers.json'
THEMES = ('legitimacy', 'reputation', 'credibility', 'trust')
QUERIES = [
    'international organizations legitimacy',
    'international organizations reputation',
    'international institutions credibility',
    'international organizations trust',
    'global governance institutional legitimacy',
    'human rights organization legitimation',
    'organizational legitimacy audience',
]
CONTEXT = ('international organization', 'united nations', 'global governance', 'human rights',
           'international institution', 'intergovernmental', 'institutional', 'organization', 'audience')


def abstract_from_index(inv):
    if not inv:
        return ''
    slots = [(int(pos), word) for word, poses in inv.items() for pos in poses]
    return ' '.join(word for _, word in sorted(slots))[:4500]


def request_openalex(query, start_date):
    params = {'search': query, 'filter': 'from_publication_date:' + start_date,
              'sort': '-publication_date', 'per_page': 40}
    if os.getenv('OPENALEX_API_KEY'):
        params['api_key'] = os.environ['OPENALEX_API_KEY']
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'ShixiongXuAcademicResearchTracker/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)['results']


def score_work(w):
    abstract = abstract_from_index(w.get('abstract_inverted_index'))
    title = w.get('title') or ''
    content = (title + ' ' + abstract).lower()
    topics = [t for t in THEMES if re.search(r'\b' + t + r'\b', content)]
    if 'legitimation' in content and 'legitimacy' not in topics:
        topics.append('legitimacy')
    context = sum(term in content for term in CONTEXT)
    score = 4 * len(topics) + 2 * context + 3 * sum(t in title.lower() for t in THEMES)
    if not topics or not context:
        return None
    return score, topics, abstract


def load_old_data():
    try:
        return json.loads(OUTPUT.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {'papers': [], 'monthly_summaries': {}}


def ai_client():
    if not os.getenv('OPENAI_API_KEY'):
        return None
    from openai import OpenAI
    return OpenAI()


def generate_text(client, instructions, content, max_tokens):
    response = client.responses.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
        instructions=instructions,
        input=content,
        max_output_tokens=max_tokens,
    )
    return (response.output_text or '').strip() or None


def ai_paper_summary(client, paper):
    return generate_text(client,
        'Write a precise, accessible 2-sentence summary of ONLY the supplied scholarly abstract. '
        'Mention the research question or argument and its main contribution if supported. '
        'Do not invent findings, data, or causal claims. Do not claim to have read the full paper.',
        f"Title: {paper['title']}\nAbstract: {paper['abstract']}", 170)


def ai_monthly_summary(client, month, selected):
    """Synthesize papers from one publication month, grounded in abstracts."""
    payload = [{'title': p['title'], 'abstract': p['abstract'][:2500]} for p in selected]
    return generate_text(client,
        'You are compiling a scholarly literature digest. In 100-150 words, synthesize '
        'common questions, differing arguments, and emerging research directions across '
        'the supplied abstracts. The input is a selected set of indexed papers, not all '
        'publications from the month. Do not invent findings, trends, or consensus. '
        'Avoid ungrounded superlatives. No headings or bullet points.',
        json.dumps({'publication_month': month, 'papers': payload}, ensure_ascii=False), 250)


def main():
    today = dt.date.today()
    since = (today - dt.timedelta(days=180)).isoformat()
    old = load_old_data()
    prior = {p.get('url'): p for p in old.get('papers', [])}
    prior_months = old.get('monthly_summaries', {})
    records = {}
    for query in QUERIES:
        try:
            works = request_openalex(query, since)
        except Exception as exc:
            print(f'OpenAlex query failed ({query}): {exc}')
            continue
        for work in works:
            assessed = score_work(work)
            if not assessed:
                continue
            score, topics, abstract = assessed
            identifier = work.get('doi') or work.get('id')
            if not identifier:
                continue
            venue = ((work.get('primary_location') or {}).get('source') or {}).get('display_name')
            row = {
                'title': work.get('title') or 'Untitled',
                'authors': [a.get('author', {}).get('display_name', '') for a in work.get('authorships', [])],
                'date': work.get('publication_date'),
                'venue': venue or 'Unspecified venue',
                'abstract': abstract,
                'topics': topics,
                'score': score,
                'url': identifier,
            }
            if identifier in prior and prior[identifier].get('abstract') == abstract:
                if prior[identifier].get('ai_summary'):
                    row['ai_summary'] = prior[identifier]['ai_summary']
            if identifier not in records or score > records[identifier]['score']:
                records[identifier] = row

    papers = sorted(records.values(), key=lambda p: (p['score'], p['date'] or ''), reverse=True)[:35]
    if not papers:
        print('No verified results retrieved; retaining prior feed.')
        return

    client = None
    try:
        client = ai_client()
    except ImportError:
        print('To enable AI summaries, install the openai Python package.')

    # Summarize newest 20 records with abstracts, retaining previously generated results.
    by_date = sorted(papers, key=lambda p: p['date'] or '', reverse=True)
    if client:
        for paper in [p for p in by_date if p['abstract'] and not p.get('ai_summary')][:20]:
            try:
                summary = ai_paper_summary(client, paper)
                if summary:
                    paper['ai_summary'] = summary
            except Exception as exc:
                print('Paper AI summary skipped:', exc)

    # Keep latest three publication-month overviews. Only publish grounded AI summaries.
    grouped = defaultdict(list)
    for paper in by_date:
        if paper['abstract'] and re.fullmatch(r'\d{4}-\d{2}-\d{2}', paper['date'] or ''):
            grouped[paper['date'][:7]].append(paper)
    monthly = {}
    for month in sorted(grouped, reverse=True)[:3]:
        selected = grouped[month][:12]
        fingerprint = sorted(p['url'] + '|' + p['abstract'] for p in selected)
        import hashlib
        digest = hashlib.sha256(json.dumps(fingerprint).encode('utf-8')).hexdigest()
        previous = prior_months.get(month, {})
        if previous.get('fingerprint') == digest and previous.get('summary'):
            monthly[month] = previous
            continue
        if client:
            try:
                summary = ai_monthly_summary(client, month, selected)
                if summary:
                    monthly[month] = {'summary': summary, 'paper_count': len(selected), 'fingerprint': digest}
            except Exception as exc:
                print('Monthly AI summary skipped:', exc)

    OUTPUT.write_text(json.dumps({'updated': today.isoformat(), 'papers': papers,
                                  'monthly_summaries': monthly}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Updated feed: {len(papers)} verified scholarly records; {len(monthly)} monthly AI summaries.')


if __name__ == '__main__':
    main()
