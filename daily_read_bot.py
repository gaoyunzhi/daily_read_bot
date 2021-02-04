#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webgram
from telegram_util import log_on_fail, compactText, removeOldFiles, tryDelete
from telegram.ext import Updater, MessageHandler, Filters
from telegram import MessageEntity
import time
import random
from util import getLink, getCnLink, getShortLink
import itertools
from datetime import date
from book import getBookRecommendation
import sys
import export_to_telegraph
from export_to_telegraph import getTitle
from bs4 import BeautifulSoup

with open('token') as f:
    token = f.read().strip()

tele = Updater(token, use_context=True) # @daily_read_bot
debug_group = tele.bot.get_chat(420074357)

with open('pool') as f:
    pool = [channel.strip() for channel in f.readlines()]
pool = [channel for channel in pool if channel]

Day = 24 * 60 * 60
Limit = 5

def getPosts():
    start = time.time()
    result = []
    for channel in pool:
        posts = webgram.getPosts(channel, force_cache=True)[1:]
        result += posts
        while posts and posts[0].time > time.time() - 7 * Day:
            posts = webgram.getPosts(channel, posts[0].post_id, 
                direction='before', force_cache=True)[1:]
            result += posts
    return result

def clearComment(comment):
    comment = comment.strip()
    for _ in range(3):
        comment.replace('\n\n', '\n')
    return comment

def getComment(text_field):
    result = ''
    for item in text_field:
        if isinstance(item, str):
            result += item
            continue
        if item.name == 'a':
            return clearComment(result)
        if item.name == 'br':
            result += '\n'
        else:
            result += item.text

def isBetterPost(post):
    return len(getComment(post.text)) > 10 and post.time > time.time() - 3 * Day

def yieldDailyRead():
    existing = set()
    start = time.time()
    posts = getPosts()
    posts = [post for post in posts if post.link]
    posts = [(post.time + random.random(), post) for post in posts]
    posts.sort(reverse = True)
    posts = [item[1] for item in posts]
    for post in [post for post in posts if isBetterPost(post)] + [
        post for post in posts if not isBetterPost(post)]:
        link = getLink(post.text)
        if not link:
            continue
        text = compactText(post.link.text)
        if link in existing or text in existing:
            continue
        existing.add(link)
        existing.add(text)
        yield text, link

def yieldPoliticsRead():
    posts = webgram.getPosts('freedom_watch', force_cache=True)[1:]
    for post in posts[::-1]:
        link = getLink(post.text, getShortLink)
        if not link:
            continue
        yield export_to_telegraph.getTitle(link), link

def getDailyRead(method=yieldDailyRead):
    items = itertools.islice(method(), Limit)
    lines = ['【%s】%s' % item for item in items]
    lines = ['%d. %s' % (index + 1, item) for index, item in enumerate(lines)]
    return ('《每日文章精选 %s》 https://t.me/daily_read \n\n' % date.today().strftime("%Y-%m-%d") + 
        '\n\n'.join(lines))

def sendDailyRead(msg, method=yieldDailyRead):
    tmp = msg.reply_text('sending')
    removeOldFiles('tmp', day=0.1)
    if 'force' in msg.text:
        removeOldFiles('tmp', day=0)
    tele.bot.send_message(msg.chat_id, getDailyRead(method), disable_web_page_preview=True)
    tryDelete(tmp)

@log_on_fail(debug_group)
def handleCommand(update, context):
    msg = update.effective_message
    if msg.text.startswith('/dr'):
        sendDailyRead(msg, yieldDailyRead)
    elif msg.text.startswith('/pr'):
        sendDailyRead(msg, yieldPoliticsRead)
    else:
        return
    tryDelete(msg)

@log_on_fail(debug_group)
def handlePrivate(update, context):
    msg = update.effective_message
    if not msg:
        return
    # book recommendation and download
    if not 2 <= len(msg.text) <= 100:
        msg.reply_text('请输入书名')
    msg.reply_text(getBookRecommendation(msg.text), parse_mode='HTML', disable_web_page_preview=True)

@log_on_fail(debug_group)
def handleUrl(update, context):
    msg = update.effective_message
    if not msg:
        return
    raw_links = msg.text.split()
    raw_links = [x for x in raw_links if 'http' in x]
    if not raw_links:
        return
    existing = set()
    items = []
    for raw_link in raw_links:
        link = getCnLink(raw_link)
        if not link:
            continue
        title = compactText(export_to_telegraph.getTitle(link))
        if link in existing or title in existing:
            continue
        existing.add(link)
        existing.add(title)
        items.append((title, link))
    lines = ['【%s】%s' % item for item in items]
    lines = ['%d. %s' % (index + 1, item) for index, item in enumerate(lines)]
    reply = ('《每日文章精选 %s》 https://t.me/daily_read \n\n' % date.today().strftime("%Y-%m-%d") + 
        '\n\n'.join(lines))
    msg.reply_text(reply, disable_web_page_preview=True)

def decorate(text):
    return '\n【%s】 %s' % (getTitle(text), text)

@log_on_fail(debug_group)
def toWC(update, context):
    msg = update.message
    if not msg:
        return
    soup = BeautifulSoup(msg.text_html_urled or msg.cap_html_urled, 'html.parser')
    elm = soup.find_all("a")[-1]
    elm.replace(decotate(elm['href']))
    text = elm.text.replace('\n', '\n\n')
    for _ in range(5):
        text = text.replace('\n\n\n', '\n\n')
    msg.chat.send_message(text.strip(), disable_web_page_preview=True)

if __name__ == '__main__':
    if 'once' in sys.argv:
        msg = debug_group.send_message('test')
        sendDailyRead(msg, yieldPoliticsRead)
    else:
        dp = tele.dispatcher
        dp.add_handler(MessageHandler((~Filters.private) & Filters.command, handleCommand))
        # dp.add_handler(MessageHandler(Filters.private & Filters.entity(MessageEntity.URL), handleUrl))
        # dp.add_handler(MessageHandler(Filters.private & (~Filters.entity(MessageEntity.URL)), handlePrivate))
        dp.add_handler(MessageHandler(Filters.private, toWC))
        tele.start_polling()
        tele.idle()