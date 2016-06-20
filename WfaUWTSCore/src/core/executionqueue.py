
###############################################################################
#
# Copyright (c) 2016 Wi-Fi Alliance
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################

#!/usr/bin/env python

from Queue import Queue

class ExecutionQueue(object):

    def __init__(self, name='default', task_id=None):
        
        self.name = name
        self.q = Queue()

    def empty(self):
        """Removes all tasks on the queue."""
        while self.q.is_empty() != True:
            task = self.q.get()
            self.q.task_done()

    def get_name(self):
        """Returns name of class"""
        return self.name

    def is_empty(self):
        """Returns whether the current queue is empty."""
        return self.q.empty()

    def fetch_task(self, task_id):
        return

    def get_task_ids(self, offset=0, length=-1):
        """Returns a slice of task IDs in the queue."""

    def get_tasks(self, offset=0, length=-1):
        """Returns a slice of tasks in the queue."""

    @property
    def task_ids(self):
        """Returns a list of all task IDS in the queue."""
        return self.get_task_ids()

    @property
    def tasks(self):
        """Returns a list of all (valid) tasks in the queue."""
        return self.get_tasks()

    @property
    def count(self):
        """Returns a count of all tasks in the queue."""
        return self.count

    def remove(self, task_or_id):
        """Removes Task from queue, accepts either a Task instance or ID."""
        task_id = task_or_id.id if isinstance(task_or_id, self.task_class) else task_or_id

        return self.connection._lrem(self.key, 1, task_id)

    def enqueue(self, task, at_front=False):
        """Enqueues a task for  execution."""
        self.q.put(task)
        #print task.get_raw_data()
        return

    def dequeue(self):
        """Dequeues the front-most task from this queue."""
        task = self.q.get()
        #print task.get_raw_data()
        self.q.task_done()
        return task

