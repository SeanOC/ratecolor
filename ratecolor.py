#/usr/bin/env python

import json
import random
import signal
import sys
import time

from collections import deque
from urllib import urlopen

from tornado.options import define, options

from lib import blink


def signal_handler(signal, frame):
    blink.off()
    sys.exit(0)


def run(access_token, phrase):
    observed_rates = deque(maxlen=30)

    while(True):
        response = urlopen('https://api-ssl.bitly.com/v3/realtime/clickrate?access_token=%s&phrase=%s' % (
            access_token,
            phrase,
        ))
        payload = json.load(response)
        if payload.get('data', None) is None:
            print "Error from bitly"
            print payload
            sys.exit(1)
        rate = payload['data']['rate']

        print "Rate:  %r" % rate
        print "Observed Rates:  %r" % observed_rates
        
        if len(observed_rates) > 0:
            average_rate = sum(observed_rates) / len(observed_rates)
            relative_change = (rate - average_rate) / average_rate
            relative_change *= 10
            print "reltive change:  %s" % relative_change
            color_offset = max(min(int(round(255 * relative_change)), 255), -255)
            print "color offset:  %s" % color_offset
            r = 255
            g = 255
            b = 255

            if color_offset > 0:
                g -= color_offset
                b -= color_offset
            elif color_offset < 0:
                r += color_offset
                g += color_offset

            print "RGB:  %s %s %s" % (r, g, b)
            blink.set_color(r=0, g=255, b=0)
            time.sleep(.3)
            blink.set_color(r, g, b)
        else:
            blink.blink(times=10, r=0, g=255, b=0)


        observed_rates.append(rate)
        time.sleep(10)


def print_bursting_suggestions(access_token):
    response = urlopen('https://api-ssl.bitly.com/v3/realtime/bursting_phrases?access_token=%s' % (
        access_token,
    ))
    payload = json.load(response)

    for phrase in sorted(payload['data']['phrases'], key=lambda phrase: phrase['std'], reverse=True):
        print "%s (%s | %s | %s)" % (
            phrase['phrase'],
            phrase['rate'],
            phrase['mean'],
            phrase['std']
        )


def print_hot_suggestions(access_token):
    response = urlopen('https://api-ssl.bitly.com/v3/realtime/hot_phrases?access_token=%s' % (
        access_token,
    ))
    payload = json.load(response)

    for phrase in payload['data']['phrases'][:20]:
        print "%s (%s)" % (
            phrase['phrase'],
            phrase['rate'],
        )


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    define("access_token", help="Your bitly oauth2 token.")
    define("phrase", help="The phrase to show the rate limit of.")
    define("bursting", help="Print a list of suggested busting phrases", default=False)
    define("hot", help="Print a list of suggested hot phrases", default=False)
    options.parse_command_line()

    if options.phrase:
        run(options.access_token, options.phrase)

    if options.bursting:
        print_bursting_suggestions(options.access_token)

    if options.hot:
        print_hot_suggestions(options.access_token)
