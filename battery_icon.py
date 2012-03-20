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
    path_to_bat = '/sys/class/power_supply'
    bat_name = 'BAT0'
    
    def read(self):
        return self.__pars_out_new__()
    
    def __pars_out_new__(self):
        '''
        Получения данных из /sys
        '''
        status = {'energy_now': 0, 'energy_full': 0, 'power_now': 0, 'energy_full_design': 0, 'status': 0}
        return_battery_array = {}
        bat_dir = os.path.join(self.path_to_bat, self.bat_name)
        if os.path.isdir(bat_dir):
            for i in status.keys():
                f = open(os.path.join(bat_dir, i))
                status_value = f.read()
                f.close()
                if i == 'status':
                    if status_value.find('Charging') == 0: # зарядка
                        status[i] = 1
                    elif status_value.find('Discharging') == 0: # работа от батареи
                        status[i] = -1
                    else:
                        status[i] = 0
                else:
                    status[i] = int(status_value)
                
            return_battery_array['Stat'] = int(float(status['energy_now']) * 100 / status['energy_full'])
            return_battery_array['Status'] = status['status']
            # time
            h = str(int(float(status['energy_now']) / status['power_now']))
            m = str(int(((float(status['energy_now']) % status['power_now']) / status['power_now']) * 60))
            return_battery_array['Time'] = '%s:%s' % (h.zfill(2), m.zfill(2))
            
            return_battery_array['Diff_design'] =  int(float(status['energy_full']) * 100 / status['energy_full_design'])
            return return_battery_array
        else:
            return None
            
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
        if battery['Status'] == 1: plugged = '-plugged'
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
            if not now:
                pixb = gtk.icon_theme_get_default().load_icon(\
        'gpm-battery-missing', 22, gtk.ICON_LOOKUP_USE_BUILTIN)
                self.set_from_pixbuf(pixb)
                self.set_tooltip('Батарея отсутствует')
            else:
                if now != now_old:
                    gtk.gdk.threads_enter()
                    thm = gtk.icon_theme_get_default()
                    pixb = thm.load_icon(self.make_icon_file_name(now),
                                        22, gtk.ICON_LOOKUP_USE_BUILTIN)
                    self.set_from_pixbuf(pixb)
                    if now['Status'] == 1:
                        self.set_tooltip('Зарядка %s осталось %s ресурс %s' % (now['Stat'], now['Time'], now['Diff_design']))
                    else:
                        self.set_tooltip('Емкость %s осталось %s ресурс %s' % (now['Stat'], now['Time'], now['Diff_design']))
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

