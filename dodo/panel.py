#     Dodo - A graphical, hackable email client based on notmuch
#     Copyright (C) 2021 - Aleks Kissinger
#
# This file is part of Dodo
#
# Dodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dodo. If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QTextBrowser, QSizePolicy, QVBoxLayout

from . import keymap
from . import util

class Panel(QWidget):
    def __init__(self, app, keep_open=False, parent=None):
        super().__init__(parent)
        self.app = app
        self.keep_open = keep_open
        self.keymap = None
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.dirty = True

        # set up timer and prefix cache for handling keychords
        self._prefix = ""
        self._prefixes = set()
        self._prefix_timer = QTimer()
        self._prefix_timer.setSingleShot(True)
        self._prefix_timer.setInterval(500)
        self._prefix_timer.timeout.connect(self.prefix_timeout)

    def title(self):
        return 'view'

    def set_keymap(self, mp):
        self.keymap = mp

        # update prefix cache for current keymap
        self._prefixes = set()
        for m in [keymap.global_keymap, self.keymap]:
            for k in m:
                for i in range(1,len(k)):
                    self._prefixes.add(k[0:-i])

    def prefix_timeout(self):
        # print("prefix fired: " + self._prefix)
        if self.keymap and self._prefix in self.keymap:
            self.keymap[self._prefix](self)
        elif self._prefix in keymap.global_keymap:
            keymap.global_keymap[self._prefix](self.app)
        self._prefix = ""

    def refresh(self):
        self.dirty = False

    def keyPressEvent(self, e):
        k = util.key_string(e)
        if not k: return None
        # print("key: " + util.key_string(e))
        cmd = self._prefix + " " + k if self._prefix != "" else k
        self._prefix_timer.stop()

        if cmd in self._prefixes:
            self._prefix = cmd
            self._prefix_timer.start()
        elif self.keymap and cmd in self.keymap:
            self._prefix = ""
            if isinstance(self.keymap[cmd], tuple):
                self.keymap[cmd][1](self)
            else: 
                self.keymap[cmd](self)
        elif cmd in keymap.global_keymap:
            self._prefix = ""
            if isinstance(keymap.global_keymap[cmd], tuple):
                keymap.global_keymap[cmd][1](self.app)
            else:
                keymap.global_keymap[cmd](self.app)
