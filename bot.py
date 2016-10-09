#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import telepot
from agenda import Agenda
from flask import Flask, request
from collections import namedtuple
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)
bot = telepot.Bot(os.getenv('TELEGRAM_TOKEN'))
agenda = Agenda()

START_MSG = u'Hola humano. Utiliza los botones para consultar la agenda de la PyconES 2016.'
DAYS_MSG = u'Días de la PyconES 2016'
SCHEDULE_MSG = u'Agenda del {}'
SLOTS_MSG = u'Eventos del {} a las {}'
INIT_MSG = u'Mostar todos los días'

TELEGRAM_MSG_TYPES = [
    'message', 'edited_message', 'callback_query',
    'inline_query', 'chosen_inline_result'
]

Day = namedtuple('Day', ['name', 'value'])
DAYS = [
    Day(u'Viernes 7 de Octubre', u'friday'),
    Day(u'Sabado 8 de Octubre', u'saturday'),
    Day(u'Domingo 9 de Octubre', u'sunday'),
]


@app.route("/", methods=['GET', 'POST'])
def webhook():
    msg = request.json
    if msg:
        key = telepot._find_first_key(msg, TELEGRAM_MSG_TYPES)
        process_msg(msg[key])
    return 'OK'  # allways ack telegram msg


def process_msg(msg):
    flavor = telepot.flavor(msg)
    if flavor == 'callback_query':
        process_callback(msg)
    elif flavor == 'chat' and is_start_cmd(msg):
        chat_id = msg['chat']['id']
        bot.sendMessage(chat_id, START_MSG, reply_markup=get_days_keyboard())


def process_callback(msg):
    bot.answerCallbackQuery(msg['id'])  # ack callback
    chat_id = msg['from']['id']
    data = msg['data'].split()

    if data[0] == 'days':
        kb = get_days_keyboard()
        bot.sendMessage(chat_id, DAYS_MSG, reply_markup=kb)
    elif data[0] == 'schedules':
        process_schedules(chat_id, data[1])
    elif data[0] == 'slots':
        process_slots(chat_id, data[1], data[2])


def process_schedules(chat_id, day):
    text = SCHEDULE_MSG.format(get_day_name(day))
    kb = get_schedules_keyboard(day)
    bot.sendMessage(chat_id, text, reply_markup=kb)


def process_slots(chat_id, day, start):
    slots = [s for s in agenda.get_slots(day, start) if s.name]
    if len(slots):
        header_text = SLOTS_MSG.format(get_day_name(day), start)
        bot.sendMessage(chat_id, header_text)
        last_slot = slots[-1]
        for slot in slots:
            kb = get_all_days_keyboard() if slot == last_slot else None
            bot.sendMessage(chat_id, get_slot_text(slot),
                disable_web_page_preview=True, parse_mode='markdown',
                reply_markup=kb)


def is_start_cmd(msg):
    return 'text' in msg and msg['text'] == '/start'


def get_day_name(day):
    for d in DAYS:
        if d.value == day:
            return d.name


def get_slot_text(slot):
    text = u'*{}*\n'.format(slot.track) if slot.track else u''
    text += u'[{}]({})\n'.format(slot.name, slot.url)
    text += u'_{}_'.format(slot.speakers) if slot.speakers else u''
    return text.strip()


def get_all_days_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=INIT_MSG, callback_data='days')]])


def get_days_keyboard():
    kb = []
    for day in DAYS:
        kb.append([InlineKeyboardButton(text=day.name,
            callback_data='schedules {}'.format(day.value))])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_schedules_keyboard(day):
    kb = []
    for schedule in agenda.get_schedules(day):
        text = u'{} - {} {}'.format(schedule.start, schedule.end, schedule.type)
        kb.append([InlineKeyboardButton(text=text, callback_data='slots {} {}'.format(day, schedule.start))])
    kb.append([InlineKeyboardButton(text='Mostar todos los días', callback_data='days')])
    return InlineKeyboardMarkup(inline_keyboard=kb)
