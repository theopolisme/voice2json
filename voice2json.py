import os, re, io, sys, glob, json, argparse, datetime
from operator import itemgetter
from bs4 import BeautifulSoup
# 
DURATION_RE = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
# 
def convert_to_type(s):
	return s.replace('http://www.google.com/voice#', '')
# 
def convert_to_tel(s):
	return s.replace('tel:', '')
# 
def convert_to_duration(s):
	r = re.search(DURATION_RE, s)
	td = datetime.timedelta(hours=int(r.group(1) or 0),
							minutes=int(r.group(2) or 0),
							seconds=int(r.group(3) or 0))
	return td.total_seconds() * 1000
# 
def serialize_general_to_record(raw):
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
# 
def serialize_text_messages_to_record(raw):
	soup = BeautifulSoup(raw, 'html.parser')
	# 
	sender = []
	messages = []
	dates = []
	conversation = []
	contributors = []
	# 
	for contributor in soup.find_all('cite', class_='sender'):
		# Messages from others are in the "span" tag and messages from you
		# are in the "abbr" tag
		if contributor.find('span', class_='fn'):
			sender.append({
				'name': contributor.find('span', class_='fn').string or '',
				'tel': convert_to_tel(
					contributor.find('a', class_='tel')['href'])
			})
		if contributor.find('abbr', class_='fn'):
			sender.append({
				'name': contributor.find('abbr', class_='fn').string or '',
				'tel': convert_to_tel(
					contributor.find('a', class_='tel')['href'])
			})
	for message in soup.find_all('q'):
		messages.append(message.text)
	for date in soup.find_all('abbr', class_='dt'):
		dates.append(date['title'])
	for item in sender:
		if item not in contributors:
			contributors.append(item)
	# A message where the other side didn't respond.
	# Tel is not given and will have to map later :/
	if len(contributors) == 1 and contributors[0]['name'] == 'Me':
			title = soup.find('title').text.split('\n')[-1]
			if '+' in title:
				contributors.append({
					'name': title,
					'tel': title
				})
			else:
				contributors.append({
					'name': title,
					'tel': ''
				})
	for i in range(0, len(messages)):
		conversation.append({
			'sender': sender[i],
			'message': messages[i],
			'date': dates[i]
		})
	record = {
		'date': dates[0],
		'contributors': contributors,
		'conversation': conversation,
		'tags': [convert_to_type(a['href']) for a in
				soup.find_all('a', rel='tag')]
	}
	return record
# 
def serialize_files_to_json(paths):
	records = []
	for path in paths:
		with io.open(path, 'r', encoding='utf8') as f:
			if 'Text' in path:
				serialized = serialize_text_messages_to_record(f.read())
				records.append(serialized)
			else:
				serialized = serialize_general_to_record(f.read())
				records.append(serialized)
	records.sort(key=itemgetter('date'))
	return json.dumps({'records': records}, indent=4)
# 
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('source',
						help='Directory of call & text HTML files to convert')
	parser.add_argument('output',
						nargs='?',
						type=argparse.FileType('w'),
						default=sys.stdout,
						help='Where to write JSON output (default: stdout)')
	args = parser.parse_args()
	files = glob.glob(os.path.join(args.source, '*.html'))
	json = serialize_files_to_json(files)
	with args.output as f:
		f.write(json)
if __name__ == '__main__':
	main()
