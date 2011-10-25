#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#       battery_icon.py
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
import sys

class ACPI_Parser():
    '''
    Класс чтения информации из acpi
    '''
    def read(self):
        return self.__pars_out__(subprocess.Popen(['acpi', '-b'], stdout=subprocess.PIPE).communicate()[0])
    
    def __pars_out__(self, stdout):
        '''
        Чтение строки получиной от утилиты acpi
        '''
        return_battery_array = {}
        battery_array = stdout.split('\n')
        for i in battery_array[:-1]:
            sep_index = i.find(':')
            battery = i[:sep_index]
            return_battery_array[battery] = {}
            a = i[sep_index + 1:].split(',')
            return_battery_array[battery]['Status'] = re.search(r'\S+', a[0]).group()
            return_battery_array[battery]['Stat'] = int(re.search(r'\d+', a[1]).group())
            return_battery_array[battery]['Time'] = re.search(r'\d+:\d+:\d+', a[2]).group()
        return return_battery_array
        
            
class Battery_Icon(gtk.StatusIcon):
    '''
    Виджет батареи
    '''
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.exit_flag = True
        pixb = gtk.icon_theme_get_default().load_icon(\
        'notification-battery-100-plugged', 22, gtk.ICON_LOOKUP_USE_BUILTIN)
        self.set_from_pixbuf(pixb)
        self.connect('popup-menu', self.menu)
        self.ACPI = ACPI_Parser()
        
    def init_battery(self):
        '''
        Активирование слежения за электропитанием
        '''
        gtk.gdk.threads_init()
        t = threading.Timer(1, self.thread)
        t.start()
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
    
    def make_icon_file_name(self, battery):
        '''
        Формирование строки имени иконки
        '''
        plugged = ''
        if battery['Status'] == 'Charging': plugged = '-plugged'
        if battery['Stat'] <= 100 and battery['Stat'] >= 90:
            prc = '100'
        elif battery['Stat'] < 90 and battery['Stat'] >= 70:
            prc = '080'
        elif battery['Stat'] < 70 and battery['Stat'] >= 50:
            prc = '060'
        elif battery['Stat'] < 50 and battery['Stat'] >= 30:
            prc = '040'
        elif battery['Stat'] < 30 and battery['Stat'] >= 10:
            prc = '020'
        else:
            prc = '000'
        return 'notification-battery-%s%s' % (prc, plugged)
    
    def thread(self):
        '''
        Поток
        '''
        now = []
        while self.exit_flag:
            now_old = now    
            now = self.ACPI.read()
            now = now[now.keys()[0]] # Чтение только первого ключа
            if now != now_old:
                gtk.gdk.threads_enter()
                thm = gtk.icon_theme_get_default()
                pixb = thm.load_icon(self.make_icon_file_name(now),
                                    22, gtk.ICON_LOOKUP_USE_BUILTIN)
                self.set_from_pixbuf(pixb)
                if now['Status'] == 'Charging':
                    self.set_tooltip('Зарядка %s осталось %s' % (now['Stat'], now['Time']))
                else:
                    self.set_tooltip('Емкость %s осталось %s' % (now['Stat'], now['Time']))
                #if now[3]:
                #    subprocess.Popen(['notify-send', now[3]], stderr=None, shell=True)
                gtk.gdk.threads_leave()
            
                for i in xrange(4):
                    if self.exit_flag:
                        time.sleep(1)
                    else:
                        break
    
    def menu(self, icon, event_button, event_time):
        '''
        Контекстное меню
        '''
        menu = gtk.Menu()
        item = gtk.MenuItem('Exit')
        item.connect('activate', self.dest)
        item.show()
        menu.append(item)
        menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)
        
    def dest(self, *args):
        '''
        Функция выхода из программы
        '''
        self.set_visible(False)
        gtk.main_quit()
        self.exit_flag = False
        sys.exit(0)

def main():
    BT = Battery_Icon()
    BT.init_battery()
    return 0

if __name__ == '__main__':
    main()

