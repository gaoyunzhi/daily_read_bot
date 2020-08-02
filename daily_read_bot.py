#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webgram
from telegram_util import log_on_fail, compactText, removeOldFiles, tryDelete
from telegram.ext import Updater, MessageHandler, Filters
import time
import random
from util import getLink
import itertools
from datetime import date

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
    start = time.time()
    posts = getPosts()
    posts = [post for post in posts if post.link]
    posts = [(post.time + random.random(), post) for post in posts]
    posts.sort(reverse = True)
    posts = [item[1] for item in posts]
    for post in [post for post in posts if isBetterPost(post)] + [
        post for post in posts if not isBetterPost(post)]:
        link = getLink(post.text)
        if link:
            yield compactText(post.link.text), link

def getDailyRead():
    items = itertools.islice(yieldDailyRead(), Limit)
    lines = ['【%s】%s' % item for item in items]
    lines = ['%d. %s' % (index + 1, item) for index, item in enumerate(lines)]
    return ('《每日文章精选 %s》 https://t.me/daily_read \n\n' % date.today().strftime("%Y-%m-%d") + 
        '\n\n'.join(lines))

def sendDailyRead(msg):
    tmp = msg.reply_text('sending')
    removeOldFiles('tmp', day=0.1)
    if 'force' in msg.text:
        removeOldFiles('tmp', day=0)
    tele.bot.send_message(msg.chat_id, getDailyRead(), disable_web_page_preview=True)
    tryDelete(tmp)

@log_on_fail(debug_group)
def handleCommand(update, context):
    msg = update.effective_message
    if not msg.text.startswith('/dr'):
        return
    sendDailyRead(msg)
    tryDelete(msg)

@log_on_fail(debug_group)
def handlePrivate(update, context):
    msg = update.effective_message
    if not msg:
        return
    sendDailyRead(msg)

if __name__ == '__main__':
    dp = tele.dispatcher
    dp.add_handler(MessageHandler(Filters.command & (~ Filters.private), handleCommand))
    dp.add_handler(MessageHandler(Filters.private, handlePrivate))
    tele.start_polling()
    tele.idle()