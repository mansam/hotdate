# -*- coding: utf-8 -*-
"""
when
An intuitive date processing library.

Author: Sam Lucidi <sam@samlucidi.com>

"""

from datetime import datetime, timedelta
from six import string_types
__version__ = "0.1.0"

class when(datetime):

    _units = {
        'year': 3.15569e7,
        'month': 2.62974e6,
        'day': 86400,
        'hour': 3600,
        'minute': 60,
        'second': 1,
    }

    _property_ordering = [
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second',
        'microsecond'
    ]

    def __new__(cls, year=0, month=1, day=1, hour=0, minute=0,
                second=0, microsecond=0, tzinfo=None):
        """
        Create a new 'when' object. There are a few different
        ways to call this that do different things:

        1. no params:
            Just calling when() gets you a shiny new
            when object representing the current moment.
            (i.e. datetime.datetime.now())

        2. date formating:
            If you pass two strings to when(),
            the first argument is treated as a date string
            and the second argument is treated as a strftime
            format string.

            This lets you do things like 'when("2014", "%Y")',
            which in this example would give you a when object
            representing 1/1/2014 at 00:00:00.

        3. datetime-alike:
            You can also just pass in all the normal datetime parameters,
            starting with the year. Unlike datetime, when will let you
            leave out everything but the year, so you can do something like
            'when(2011)' and when will set the other parameters to their
            minimum values. That example would give you a when object
            representing 1/1/2011 at 00:00:00.

        """


        if isinstance(year, string_types) and isinstance(month, string_types):
            # some gnarly argument overloading here
            # so that we can do format strings as
            # positional args without breaking
            # the creation of datetimes.
            datestr = year
            fstr = month
            obj = when.strptime(datestr, fstr)
        elif year:
            obj = super(
                when,
                cls).__new__(
                cls,
                year,
                month,
                day,
                hour,
                minute,
                second,
                microsecond,
                tzinfo)
        else:
            now = datetime.now()
            obj = super(
                when,
                cls).__new__(
                cls,
                now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute,
                second=now.second,
                microsecond=now.microsecond)
        return obj

    def format(self, fstr=None, microseconds=False):
        if fstr:
            output = self.strftime(fstr)
        else:
            output = when.isoformat(self)
            if not microseconds:
                output = output.split(".")[0]
        return output

    def from_now(self):
        now = when.now()
        delta = self - now
        days = int(abs(delta.total_seconds() / 86400))
        seconds = int(abs(delta.total_seconds()))
        unit = ''
        units = 0
        # this is all very approximate
        if days / 365.0 >= 1:
            unit = "year"
            units = int(days / 365.0)
        elif days / 30.0 >= 1:
            unit = "month"
            units = int(days / 30.0)
        elif days / 7.0 >= 1:
            unit = "week"
            units = int(days / 7.0)
        elif days > 0:
            unit = "day"
            units = days
        elif seconds / 3600.0 >= 1:
            unit = "hour"
            units = int(seconds / 3600.0)
        elif seconds / 60.0 >= 1:
            unit = "minute"
            units = int(seconds / 60.0)
        else:
            unit = "second"
            units = seconds
        if delta.days < 0 or delta.seconds < 0:
            suffix = "ago"
        else:
            suffix = "from now"
        return when._ago_string(unit, units, suffix)

    def add(self, **args):
        seconds = 0
        for k, v in args.items():
            if k.endswith('s'):
                k = k[:-1]
            seconds += (self._units[k] * v)

        d = self + timedelta(seconds=seconds)
        return when.from_datetime(d)

    def subtract(self, **args):
        seconds = 0
        for k, v in args.items():
            if k.endswith('s'):
                k = k[:-1]
            seconds += (self._units[k] * v)

        d = self - timedelta(seconds=seconds)
        return when.from_datetime(d)

    def calendar(self):
        """


        """

        today = when.now()

        delta = today - self
        prefix = ''
        calday = ''
        use_calday = False
        # TODO: fix this godawful mess when
        # I am actually awake
        if -7 < delta.days < 0:
            use_calday = True
        if 7 > delta.days > 0:
            prefix = 'Last '
            use_calday = True
        if delta.days == 0:
            use_calday = True
        if use_calday:
            if today.day == (self.day - 1):
                calday = 'Tomorrow'
            elif today.day == (self.day + 1):
                calday = 'Yesterday'
                prefix = ''
            elif today.day == self.day:
                calday = 'Today'
            else:
                calday = self.strftime('%A')
            return '{}{} at {}'.format(
                prefix, calday, self.strftime('%I:%M%p'))
        else:
            return self.strftime('%x')

    def start_of(self, unit):
        props = {}
        ix = self._property_ordering.index(unit)
        for prop in self._property_ordering:
            props[prop] = getattr(self, prop)
            if self._property_ordering.index(prop) > ix:
                if prop in ['month', 'day']:
                    props[prop] = 1
                else:
                    props[prop] = 0
        return when(**props)

    def end_of(self, unit):
        props = {}
        ix = self._property_ordering.index(unit)
        for prop in self._property_ordering[:(ix + 1)]:
            props[prop] = getattr(self, prop)
            if prop == unit:
                props[prop] += 1
        return when.from_datetime(when(**props) - timedelta(seconds=1))

    @classmethod
    def from_datetime(cls, dt):
        w = when(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo)
        return w

    @classmethod
    def _ago_string(cls, unit, units, suffix):
        if units == 0:
            return "just now"
        else:
            article = 'a'
            if unit == 'hour':
                article = article + 'n'
            if units == 1:
                units = article
            else:
                unit = unit + 's'
            return "{} {} {}".format(units, unit, suffix)