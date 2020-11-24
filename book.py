from bs4 import BeautifulSoup
import cached_url

book_prefix = 'https://book.douban.com/subject/'

def getBookRecommendation(book_name):
	search_url = 'https://www.douban.com/search?cat=1001&q=' + book_name
	soup = BeautifulSoup(cached_url.get(search_url), features='lxml')
	book = soup.find('a', {'onclick': True})
	if not book:
		return '豆瓣搜索失败'
	douban_book_name = book.get('title')
	sid = book.get('onclick').split('sid: ')[1].split(',')[0]
	book_url = book_prefix + sid
	soup = BeautifulSoup(cached_url.get(book_url), features='lxml')
	rating = soup.find('strong', class_='rating_num').text
	related = []
	count = 0
	for item in soup.find_all('a', {'href': True}):
		if 'book-rec-books' not in str(item):
			continue
		if item.text.strip() and item['href'].startswith(book_prefix):
			count += 1
			related.append('%d. <a href="%s">%s</a>' % (count, item['href'], item.text.strip()))
	return '豆瓣书名： %s\n豆瓣评分： %s\n\n相关书籍：\n%s' % (
		douban_book_name, rating, '\n'.join(related))


