#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import gc
import os
from multiprocessing import Process
from multiprocessing.queues import Queue

import psutil


class MemoryLeakAssistant(object):
    """ Assistant methods used to assert against memory leaks in unittests.
    """

    def assertMemoryUsage(self, process, usage, slack=0, msg=None):
        """ Assert that the memory usage does not exceed the provided limit.

        Parameters
        ----------
        process : psutil.Process
            The process to check.
        usage : float
            The target memory usage. This is used as a soft-limit.
        msg : str
            The message to show on AssertionError.
        slack : float
            The percentage (relative to `usage`) that we allow the
            process memory usage to exceed the soft limit. The default is 0.0

        Raises
        ------
        AssertionError :
            if the current memory usage of the process is higher than
            :math:`usage * (1 + slack)`.

        """
        current_usage = self._memory_usage(process)
        hard_limit = usage * (1 + slack)
        if  hard_limit < current_usage:
            if msg is None:
                difference = (current_usage - usage) / usage
                msg = "Memory leak of {:.2%}".format(difference)
            raise AssertionError(msg)

    def assertReturnsMemory(self, function, args=None, iterations=100,
                            slack=0.0, msg=None):
        """ Assert that the function does not retain memory over a number of
        runs.

        Parameters
        ----------
        func : callable
            The function to check. The function should take no arguments.
        args : tuple
            The tuple of arguments to pass to the callable.
        iterations : int
            The number of times to run the function. Default is 100.
        msg : str
            The message to show on AssertionError.
        slack : float
            The percentage (relative to the first run) that we allow the
            process memory usage to exceed the expected. The default is 0.0

        Note
        ----
        The function is executed in-process thus any memory leaks will be
        there to cause problems to other tests that are part of the currently
        running test suite.

        """
        process = psutil.Process(os.getpid())

        def test_function():
            if args is None:
                function()
            else:
                function(*args)

        gc.collect()
        baseline = self._memory_usage(process)

        try:
            for index in xrange(iterations):
                test_function()
                gc.collect()
                self.assertMemoryUsage(process, baseline, slack=slack)
        except AssertionError:
            leak = (self._memory_usage(process) - baseline) / baseline
            if msg is None:
                msg = "Memory leak of {:.2%} after {} iterations"
                raise AssertionError(msg.format(leak, index + 1))
            else:
                raise AssertionError(msg)

    def assertDoesNotLeak(self, function, args=None, slack=0.2,
                          iterations=100):
        """ Repeat the execution of a function in a child process while
        monitoring the memory usage.

        The method checks that the memory usage of the process at the end of
        each run does not exceed on average (1 + slack) times the usage of
        the first run and returns the appropriate errors.

        .. note:: The memory leak could be so bad that the process goes out of
            memory. In such a case the method returns the exception traceback.

        """
        queue = Queue()
        process = Process(
            target=self._subprocess_runner(),
            args=(function, iterations, slack, queue, args)
        )
        self._assertChildProcessFinishes(process, queue)

    def _memory_usage(self, process):
        return float(process.get_memory_info().rss)

    def _assertChildProcessFinishes(self, process, queue):
        try:
            process.start()
            process.join()
            outcome = queue.get_nowait()
        finally:
            # Make sure that the process has terminated
            process.terminate()

        if outcome != 'FINISHED':
            self.fail(outcome)


def _check_for_memory_leak(function, iterations, slack, queue, args=None):
    assistant = MemoryLeakAssistant()
    try:
        assistant.assertNoMemoryLeak(function,
                                     iterations=iterations,
                                     args=args,
                                     slack=slack)
    except Exception as error:
        queue.put(error)
        return
    queue.put('FINISHED')
