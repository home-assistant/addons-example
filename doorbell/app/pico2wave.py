#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2017 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

import logging
import subprocess
import tempfile

VOICES = [ 'de-DE', 'en-GB', 'en-US', 'es-ES', 'fr-FR', 'it-IT' ]

class PicoTTS(object):

    def __init__(self,
                 voice       = 'en-US'):
        self._voice       = voice

    def _picotts_exe(self, args, sync=False):
        cmd = ['pico2wave',
               '-l', self._voice,
               ]

        cmd.extend(args)

        logging.debug('picotts: executing %s' % repr(cmd))

        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        res = iter(p.stdout.readline, b'')
        if not sync:
            return res

        res2 = []
        for line in res:
            res2.append(line)
        return res2

    # def say(self, txt, sync=False):
    #     txte = txt.encode('utf8')
    #     args = []
    #     args.append(txte)
    #     self._picotts_exe(args, sync=sync)

    def synth_wav(self, txt):

        wav = None

        with tempfile.NamedTemporaryFile(suffix='.wav') as f:

            txte = txt.encode('utf8')

            args = ['-w', f.name, txte]

            self._picotts_exe(args, sync=True)

            f.seek(0)
            wav = f.read()

            logging.debug('read %s, got %d bytes.' % (f.name, len(wav)))

        return wav

    @property
    def voices(self):
        return VOICES

    @property
    def voice(self):
        return self._voice
    @voice.setter
    def voice(self, v):
        if v in VOICES:
            self._voice = v
        else:
            #print("Unknown voice, supported voices:{voices}".format(voices=VOICES))
            raise ValueError("Unknown voice, supported voices:{voices}".format(voices=VOICES))