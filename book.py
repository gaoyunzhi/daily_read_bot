from bs4 import BeautifulSoup
import cached_url

def getDouban(book_name):
	search_url = 'https://www.douban.com/search?cat=1001&q=' + book_name
	soup = BeautifulSoup(cached_url.get(search_url), features='lxml')
	book = soup.find('a', {'onclick': True})
	if not book:
		return '豆瓣搜索失败'
	douban_book_name = book.get('title')
	sid = book.get('onclick').split('sid: ')[1].split(',')[0]
	book_url = 'https://book.douban.com/subject/' + sid
	soup = BeautifulSoup(cached_url.get(book_url), features='lxml')
	return '豆瓣书名： %s' + douban_book_name

def getBookRecommendation(book_name):
	return getDouban(book_name)


