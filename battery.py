#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
#       battery.py
#       
#       Copyright 2011 CryptSpirit <cryptspirit@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import os
import re
import gtk
import time
import threading
import subprocess

path = '/proc/acpi/battery'
def battery_life():
    rate = {}
    if os.path.isdir(path):
        for i in os.listdir(path):
            if os.path.isdir(path + '/' + i):
                try: f = open(path + '/' + i + '/info', 'r')
                except: return None
                else:
                    fr = f.read()
                    f.close()
                    r = re.search(r'last full capacity:.*', fr).group()
                    last_full_capacity = int(re.search(r'\d+', r).group())
                    r = re.search(r'design capacity warning:.*', fr).group()
                    warning = int(re.search(r'\d+', r).group())
                    r = re.search(r'design capacity low:.*', fr).group()
                    low = int(re.search(r'\d+', r).group())
                try: f = open(path + '/' + i + '/state', 'r')
                except: return None
                else:
                    fr = f.read()
                    r = re.search(r'charging state:.*', fr).group()[16:]
                    charging_state = re.search(r'\S+', r).group()
                    #print charging_state
                    r = re.search(r'present rate:.*', fr).group()
                    present_rate = int(re.search(r'\d+', r).group())
                    #print present_rate
                    r = re.search(r'remaining capacity:.*', fr).group()
                    remaining_capacity = int(re.search(r'\d+', r).group())
                    #print remaining_capacity
                    f.close()
                rate[i] = []
                if charging_state == 'charging':
                    rate[i].append('зарядка')
                elif charging_state == 'charged':
                    rate[i].append('заряжено')
                else:
                    rate[i].append('')
                
                rate[i].append(int((float(remaining_capacity) / float(last_full_capacity)) * 100))
                if present_rate == 0:
                    rate[i].append('')
                else:
                    hours = int(float(remaining_capacity) * 1.0 / float(present_rate) * 1.0)
                    minutes = int(((float(remaining_capacity) % float(present_rate)) / float(present_rate)) * 60)
                    rate[i].append(str(hours).zfill(2) + ':' + str(minutes).zfill(2))
                if remaining_capacity > warning - 10 and remaining_capacity < warning + 10:
                    rate[i].append('Низкий заряд батареи')
                elif remaining_capacity > low - 10 and remaining_capacity < low + 10:    
                    rate[i].append('Батарея разряжена')
                else:
                    rate[i].append('')
                return rate

def bat():
    gtk.gdk.threads_enter()
    pixb = gtk.icon_theme_get_default().load_icon('notification-battery-100-plugged', 22, gtk.ICON_LOOKUP_USE_BUILTIN)
    icon = gtk.status_icon_new_from_pixbuf(pixb)
    gtk.gdk.threads_leave()
    now = []
    while 1:
        now_old = now    
        now = battery_life()
        now = now[now.keys()[0]]
        if now != now_old:
            if now[0] == 'зарядка' or now[0] == 'заряжено':
                plugged = '-plugged'
            else:
                plugged = ''
                
            if now[1] <= 100 and now[1] >= 90:
                prc = '100'
            elif now[1] < 90 and now[1] >= 70:
                prc = '080'
            elif now[1] < 70 and now[1] >= 50:
                prc = '060'
            elif now[1] < 50 and now[1] >= 30:
                prc = '040'
            elif now[1] < 30 and now[1] >= 10:
                prc = '020'
            else:
                prc = '000'
            gtk.gdk.threads_enter()
            pixb = gtk.icon_theme_get_default().load_icon('notification-battery-' + prc + plugged, 22, gtk.ICON_LOOKUP_USE_BUILTIN)
            icon.set_from_pixbuf(pixb)
            if now[0] == 'зарядка':
                icon.set_tooltip(now[0] + ' ' + str(now[1]) + ' % ')
            else:
                icon.set_tooltip(now[0] + ' ' + str(now[1]) + ' % ' + now[2])
            if now[3]:
                subprocess.Popen(['notify-send', now[3]], stderr=None, shell=True)
            gtk.gdk.threads_leave()
        time.sleep(4)

def main():
    gtk.gdk.threads_init()
    t = threading.Timer(1, bat)
    t.start()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    return 0

if __name__ == '__main__':
    main()

