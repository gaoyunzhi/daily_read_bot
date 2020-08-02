#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webgram
from telegram_util import log_on_fail
from telegram.ext import Updater, MessageHandler, Filters
import time

with open('token') as f:
    token = f.read().strip()

tele = Updater(token, use_context=True)
debug_group = tele.bot.get_chat(420074357)

with open('pool') as f:
    pool = [channel.strip() for channel in f.readlines()]
pool = [channel for channel in pool if channel]

SevenDay = 7 * 24 * 60 * 60

def getPosts():
    result = []
    for channel in pool:
        posts = webgram.getPosts(channel)[1:]
        result += posts
        while posts and posts[0].time > time.time() - SevenDay:
            posts = webgram.getPosts(channel, posts[0].post_id, direction='before')
            result += posts
    print(len(result))
    return result

def getDailyRead():
    posts = getPosts()
    posts = [post for post in posts in post.link]
    [print(post.link) for post in posts]



def sendDailyRead(msg):
    removeOldFiles('tmp', day=0.1)
    if 'force' in msg.text:
        removeOldFiles('tmp', day=0)
    tele.bot.send_message(msg.chat_id, getDailyRead(), disable_web_page_preview=True)

@log_on_fail(debug_group)
def handleCommand(update, context):
    msg = update.effective_message
    if not msg.startswith('/dr'):
        return
    sendDailyRead(msg)
    msg.delete()

@log_on_fail(debug_group)
def handlePrivate(update, context):
    msg = update.effective_message
    if not msg:
        return
    sendDailyRead(msg)

if __name__ == '__main__':
    getDailyRead() # test
    dp = tele.dispatcher
    dp.add_handler(MessageHandler(Filters.command & (~ Filters.private), handleCommand))
    dp.add_handler(MessageHandler(Filters.private, handlePrivate))