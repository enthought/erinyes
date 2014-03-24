#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A testcase mixin to help with automated application testing. """

import os
import subprocess
import time


class ApplicationTestAssistant(object):
    """ A mixin to help with automated GUI testing.

    """

    ### Assert methods ######################################################

    def assertApplicationActive(self, application, msg=None):
        """ Assert that the application has at least one active window.

        Parameters
        ----------
        application : subprocess.Process
            The subprocess of the application that we are testing.

        """
        try:
            application.active_()
        except RuntimeError:
            if msg is None:
                msg = 'Application crashed early'
            self.fail(msg)

    def assertProcessDoesNotExist(self, process, timeout=5.0, msg=None):
        """ Assert that the given process does not exist.

        This maybe be a bit temperemental if the operating system re-uses the
        same process Id, but is probably 'good enough'.

        """
        if msg is None:
            msg = 'Process "{}" still exists'.format(process.pid)
        returncode = process.poll()
        if returncode is None:
            time.sleep(timeout)
            returncode = process.poll()

        self.assertIsNotNone(returncode, msg=msg)

    def assertWindowExists(self, window_assistant, timeout=None, msg=None):
        """ Assert that the window exists within a timeout.

         Parameters
         ----------
         window_assistant : WindowAssistant
             The window gui assistant wrapper over the application window
         timeout : int
             The timeout to use. This overrides the default value
         msg : str
             An alternative assertion message to use.

        """
        exists = window_assistant.exists(timeout)
        if not exists:
            if msg is None:
                msg = 'No Window exists with the criteria: {}'.format(
                    window_assistant.window_spec.criteria,
                )
            self.fail(msg)

    def assertWindowDoesNotExist(self, window_assistant, timeout=None,
                                 msg=None):
        """ Assert that the window does not exist within a timeout.

         Parameters
         ----------
         window_assistant : WindowAssistant
             The window gui assistant wrapper over the application window
         timeout : int
             The timeout to use. This overrides the default value
         msg : str
             An alternative assertion message to use.

        """

        died = window_assistant.does_not_exist(timeout)
        if not died:
            if msg is None:
                msg = 'Window "{}" still exists'.format(
                    window_assistant.title,
                )
            self.fail(msg)

    ### Common tasks methods ################################################

    def start_application(self, command, stdout=None, stderr=None):
        """ Start the application!

        Starts and return the process that the application was started in.
        The stdout and stderr of the child process is redirected to the
        provided stream (default is to suppress).

         Parameters
         ----------
         command : str
             The command to execute on the shell to run the application.
         stdout :
             The stream to use for standard output. Default is os.devnull
         strerr :
             The stream to use for standard error. Default is os.devnull

        """
        devnull = open(os.devnull, 'w')
        stdout = devnull if stdout is None else stdout
        stderr = devnull if stderr is None else stderr
        return subprocess.Popen(args=command, stdout=stdout, stderr=stderr)

    def close_window(self, window_assistant):
        """ Close the window and assert that it does not exist anymore.

         Parameters
         ----------
         window_assistant : WindowAssistant
             The window gui assistant wrapper over the application window

        """
        window_assistant.close()
        self.assertWindowDoesNotExist(window_assistant)
