#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from colorama import Fore, Back, Style

def colormap(line):
    # Map ruter line numbers to terminal safe colors
    if line in ['1', '22', '25', '32', '48', '72', '72A', '72B', '72C', '85',
                '104',
                'L2', 'N250']:
        return Fore.BLACK + Back.CYAN
    elif line in ['2', '18', '19', '33', '51', '60', '63', '74', '86',
                  '111',
                  'L13', 'L14',
                  'N2', 'N3', 'N4', 'N5', 'N18', 'N70', 'N130', 'N140', 'N150', 'N160']:
        return Fore.BLACK + Back.YELLOW
    elif line in ['3', '12', '24', '34', '45', '68', '69', '81', '81A', '81B',
                  '103', '112',
                  'L21', 'R20', 'N30', 'N32']:
        return Fore.BLACK + Back.MAGENTA
    elif line in ['4', '21', '31', '31E', '41', '54', '56', '56B',
                  '63', '65', '67', '70', '71B', '76',
                  'L22']:
        return Fore.BLACK + Back.BLUE
    elif line in ['5', '11', '13', '30', '36E', '46', '58',
                  '62', '64', '64A', '66',
                  '71A', '75', '75A', '75B', '77', '77B', '77X', '78', '78A', '78B',
                  '80', '80E',
                  '107', '119',
                  'L3', 'R30',
                  'N20', 'N81', 'N83']:
        return Fore.BLACK + Back.GREEN
    elif line in ['17', '20', '23', '28', '37', '79', '82E', '83', '84E',
                  '102', '105', '118',
                  'L1', 'L12', 'R10', 'R11',
                  'N12', 'N54', 'N63', 'N590']:
        return Fore.BLACK + Back.RED
    if line in ['L2X']:
        return Fore.CYAN + Back.WHITE
    if line in ['L14X']:
        return Fore.YELLOW + Back.WHITE
    if line in ['L22X']:
        return Fore.BLUE + Back.WHITE
    if line in ['R11E', 'R11X']:
        return Fore.RED + Back.WHITE
    if line in ['108', '109', 'FT']:
        return Fore.BLACK + Back.WHITE
    else:
        return Fore.WHITE

def line_color(line):
    return colored(colormap(line), " " + line + " ")

def colored(color, text):
    return color + text + Style.RESET_ALL
