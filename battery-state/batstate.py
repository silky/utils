# coding=UTF-8
# Based on: http://www.masnun.me/2010/09/01/python-script-to-monitor-laptop-battery-charge-ubuntulinux-mint.html
#      and: http://stevelosh.com/blog/2010/02/my-extravagant-zsh-prompt/#my-right-prompt-battery-capacity
import commands, math, sys

def display_state ():
    remaining = float(
            # Old ubuntu
            # commands.getoutput('grep "^remaining capacity" /proc/acpi/battery/BAT0/state | awk \'{ print $3 }\'')
            commands.getoutput('upower -i ' +
                    '/org/freedesktop/UPower/devices/battery_BAT0 | ' +
                    'grep -E "percentage" | awk \'{ print $2 }\'').strip("%")
            )
    # full = float(
    #         commands.getoutput('grep "^last full capacity" /proc/acpi/battery/BAT0/info | awk \'{ print $4 }\'')
    #         )
    # Old
    # charging = commands.getoutput('grep "^charging state" /proc/acpi/battery/BAT0/state | awk \'{ print $3 }\'')
    #
    charging = commands.getoutput('upower -i ' +
            '/org/freedesktop/UPower/devices/battery_BAT0 | ' +
            '"state" | awk "{ print $2 }"')
    
    fraction = remaining/100.

    # Bugfix for systems that claim they are charged but the fraction
    # is less than 1 ...
    
    if charging == "charged":
        fraction = 1

    full  = "▲"
    empty = "△"

    green  = '\033[32m'
    yellow = '\033[33m'
    red    = '\033[31m'
    cyan   = '\033[36m'
    color_reset = '\033[00m'

    total_slots = 3

    tol = 0.05 # Claim we're at 100% if we're this close.

    filled = int(math.floor(total_slots * (fraction + tol)))
    result = '%s%s' % ((total_slots - filled) * empty, full * filled)

    color_out = red

    if fraction > .15:
        color_out = yellow

    if fraction > .3:
        color_out = cyan

    if fraction > .6:
        color_out = green

    result = result.strip(' ')
    if fraction != 1:
        # The percents are required by zsh, so that the colour chars
        # don't take up physical space.
        print '%{' + color_out + '%}', result, '%{' + color_reset + '%}'
    else:
        # Say nothing.
        pass

if __name__ == "__main__":
    display_state()
