#!/usr/bin/env python

#
# ** The MIT License **
#
# Copyright (c) 2013 Andrei Gherzan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Helper for logging module to be able to use colors
#
# Home: https://github.com/agherzan/nodf
#
# Author: Andrei Gherzan <andrei@gherzan.ro>
#

import logging

# Color codes
WHITE = 37
RED = 31
GREEN = 32
YELLOW = 33

# Sequences
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[0;%dm"
BOLD_SEQ  = "\033[1m"
NOBOLD_SEQ  = "\033[0m"

# Map logging level to color
COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': WHITE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
    '''
    Formatting class for using colors
    '''
    FORMAT = '%(levelname)s : %(message)s'
    def __init__(self, use_color = True):
        logging.Formatter.__init__(self, self.FORMAT)
        self.use_color = use_color

    def format(self, record):
        record.msg = record.msg.replace('[bold]', BOLD_SEQ)
        record.msg = record.msg.replace('[/bold]', NOBOLD_SEQ )
        if self.use_color and record.levelname in COLORS:
            levelname_color = COLOR_SEQ % (COLORS[record.levelname]) + record.levelname
            msg_color = record.msg + RESET_SEQ
            record.levelname = levelname_color
            record.msg = msg_color
        return logging.Formatter.format(self, record)
