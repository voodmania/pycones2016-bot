#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from collections import namedtuple

Schedule = namedtuple('Schedule', ['start', 'end', 'type'])
Slot = namedtuple('Slot', ['track', 'room', 'name', 'speakers', 'url', 'language', 'tags'])

SCHEDULE_SQL = '''
    select distinct start, end, type
    from agenda where day="{}" order by start;
'''
SLOT_SQL = '''
    select track, room, name, speakers, url, language, tags
    from agenda where day="{}" and start="{}";
'''


class Agenda(object):
    def __init__(self):
        self._conn = sqlite3.connect('agenda.db')
        self._cur = self._conn.cursor()

    def get_schedules(self, day):
        self._cur.execute(SCHEDULE_SQL.format(day))
        return [Schedule(*row) for row in self._cur.fetchall()]

    def get_slots(self, day, start):
        self._cur.execute(SLOT_SQL.format(day, start))
        return [Slot(*row) for row in self._cur.fetchall()]


__all__ = ['Agenda']
