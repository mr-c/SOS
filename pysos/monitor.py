#!/usr/bin/env python3
#
# This file is part of Script of Scripts (SoS), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/bpeng2000/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
#
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import psutil
import threading
import time
from datetime import datetime
from .utils import env

class ProcessMonitor(threading.Thread):
    def __init__(self, pid, msg='', interval=1):
        threading.Thread.__init__(self)
        self.pid = pid
        self.interval = interval
        self.proc_file = os.path.join(env.exec_dir, '.sos/{}.proc'.format(self.pid))
        with open(self.proc_file, 'w') as pd:
            if msg:
                pd.write('# {}\n'.format(msg.replace('\n', '\n# ')))
            pd.write('#started at {}\n#\n'.format(datetime.now().strftime("%A, %d. %B %Y %I:%M%p")))
            pd.write('#time\tproc_cpu\tproc_mem\tchildren\tchildren_cpu\tchildren_mem\n')
                 
    def _check(self):
        current_process = psutil.Process(self.pid)
        par_cpu = current_process.cpu_percent()
        par_mem = current_process.memory_info()[0]
        ch_cpu = 0
        ch_mem = 0
        children = current_process.children(recursive=True)
        n_children = len(children)
        for child in children:
            ch_cpu += child.cpu_percent()
            ch_mem += child.memory_info()[0]
        return par_cpu, par_mem, n_children, ch_cpu, ch_mem

    def run(self):
        while True:
            try:
                cpu, mem, nch, ch_cpu, ch_mem = self._check()
                time.sleep(self.interval)
                with open(self.proc_file, 'a') as pd:
                    pd.write('{}\t{:.2f}\t{}\t{}\t{}\t{}\n'.format(time.time(), cpu, mem, nch, ch_cpu, ch_mem))
            except Exception:
                # if the process died, exit the thread
                # the warning message is usually:
                # WARNING: psutil.NoSuchProcess no process found with pid XXXXX
                #env.logger.warning(e)
                break

def summarizeExecution(pid):
    proc_file = os.path.join(env.exec_dir, '.sos/{}.proc'.format(pid))
    if not os.path.isfile(proc_file):
        return ''
    peak_cpu = 0
    accu_cpu = 0
    peak_mem = 0
    accu_mem = 0
    peak_nch = 0
    start_time = None
    end_time = None
    count = 0
    with open(proc_file) as proc:
        for line in proc:
            if line.startswith('#'):
                continue
            try:
                t, c, m, nch, cc, cm = line.split()
            except Exception as e:
                env.logger.warning('Unrecognized resource line "{}": {}'.format(line.strip(), e))
            if start_time is None:
                start_time = float(t)
            else:
                end_time = float(t)
            accu_cpu += float(c) + float(cc)
            accu_mem += float(m) + float(cm)
            count += 1
            if float(c) + float(cc) > peak_cpu:
                peak_cpu = float(c) + float(cc)
            if float(m) + float(cm) > peak_mem:
                peak_mem = float(m) + float(cm)
            if int(nch) > peak_nch:
                peak_nch = int(nch)
    if start_time is None or end_time is None:
        return ''
    else:
        return ('Completed in {:.1f} seconds with {} child{} and {:.1f}% peak ({:.1f}% avg) CPU and {:.1f}Mb peak ({:.1f}Mb avg) memory usage'
            .format(end_time - start_time, peak_nch, 'ren' if peak_nch > 1 else '', peak_cpu, accu_cpu/count, peak_mem/1024/1024, accu_mem/1024/1024/count))
        
