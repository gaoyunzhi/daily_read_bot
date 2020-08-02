from bs4 import BeautifulSoup
import cached_url
from telegram_util import matchKey, clearUrl
import export_to_telegraph

def getRawLink(link):
	if 'telegra.ph' not in link:
		return link
	b = BeautifulSoup(cached_url.get(link, force_cache=True), 'html.parser')
	try:
		return b.find('address').find('a')['href']
	except:
		...

def getCnLink(link):
	link = getRawLink(link)
	if not link:
		return
	if not matchKey(link, ['/note/', 'thepaper', 'weixin']):
		return
	link = clearUrl(link)
	# getTitle by default will cache
	if matchKey(export_to_telegraph.getTitle(link), ['链接已过期']):
		return False
	return link

def getLink(text_field):
	for item in text_field:
		if isinstance(item, str):
			continue
		if item.name == 'a':
			link = getCnLink(item.get('href', ''))
			if link:
				return link