import os
import re
import sys
import glob
import json
import argparse
import datetime
from operator import itemgetter

from bs4 import BeautifulSoup

DURATION_RE = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'


def convert_to_type(s):
    return s.replace('http://www.google.com/voice#', '')


def convert_to_tel(s):
    return s.replace('tel:', '')


def convert_to_duration(s):
    r = re.search(DURATION_RE, s)
    td = datetime.timedelta(hours=int(r.group(1) or 0),
                            minutes=int(r.group(2) or 0),
                            seconds=int(r.group(3) or 0))
    return td.total_seconds() * 1000


def serialize_html_to_record(raw):
    soup = BeautifulSoup(raw, 'html.parser')

    contributors = []
    for contributor in soup.find_all('div', class_='contributor'):
        contributors.append({
            'name': contributor.find('span', class_='fn').string or '',
            'tel': convert_to_tel(contributor.find('a', class_='tel')['href'])
        })

    record = {
        'tags': [convert_to_type(a['href']) for a in
                 soup.find_all('a', rel='tag')],
        'date': soup.find('abbr', class_='published')['title'],
        'contributors': contributors
    }

    if soup.find('abbr', class_='duration') is not None:
        record['duration'] = convert_to_duration(
            soup.find('abbr', class_='duration')['title'])

    return record


def serialize_files_to_json(paths):
    records = []
    for path in paths:
        with open(path) as f:
            print path
            serialized = serialize_html_to_record(f.read())
            records.append(serialized)

    records.sort(key=itemgetter('date'))
    return json.dumps({'records': records}, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',
                        help='Directory of call HTML files to convert')
    parser.add_argument('output',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Where to write JSON output (default: stdout)')
    args = parser.parse_args()

    files = glob.glob(os.path.join(args.source, '*.html'))

    # Ignore text messages from pre-Hangouts integration, they're funky and
    # they don't follow the same formatting as everything else.
    # [FIXME: Support these somehow?]
    files = filter(lambda f: 'Text' not in f, files)

    json = serialize_files_to_json(files)

    with args.output as f:
        f.write(json)

if __name__ == '__main__':
    main()
