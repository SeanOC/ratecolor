import subprocess


def call_blink_tool(args):
    proc = subprocess.Popen(
        'blink1-tool %s' % args,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc


def off():
    call_blink_tool('--off')


def set_color(r, g, b):
    call_blink_tool('--rgb %d,%d,%d' % (r, g, b))


def blink(times=1, r=255, g=255, b=255):
    call_blink_tool('--rgb %d,%d,%d --blink %d' % (r, g, b, times))
