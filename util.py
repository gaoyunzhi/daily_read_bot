from bs4 import BeautifulSoup
import cached_url
from telegram_util import matchKey, clearUrl, isCN
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
	if not matchKey(link, ['/note/', 'thepaper', 'weixin', 'zhihu.', 'cnpoliti']):
		return
	link = clearUrl(link)
	# getTitle by default will cache
	if matchKey(export_to_telegraph.getTitle(link), [
		'链接已过期', '仅限男生', '男生350分']):
		return False
	return link

def getLink(text_field, method=getCnLink):
	for item in text_field:
		if isinstance(item, str):
			continue
		if item.name == 'a':
			link = method(item.get('href', ''))
			if link:
				return link

def shorter(x, y):
	if len(x) < len(y):
		return x
	else:
		return y 

def getShortLink(link):
	if matchKey(link, ['weibo.', 'twitter.', 't.me/']):
		return 
	raw_link = getRawLink(link)
	if isCN(export_to_telegraph.getTitle(raw_link)):
		return shorter(raw_link, link)
	if isCN(export_to_telegraph.getTitle(link)):
		return link