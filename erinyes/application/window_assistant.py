#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------


class WindowAssistant(object):
    """ Window assistant class.

    The WindowAssistant encloses the logic to find and simulate user
    interaction with an application window or dialog.

    """
    def __init__(self, criteria, actions=None, timeout=None):
        """ Class Initialization.

        Parameters
        ----------
        criteria: dict
            The criteria to use to find the window (please see
            :class:`~pywinauto.application.WindowSpecification`).
        actions: dict
            The set of actions that can be performed along with the keyboard
            actions that are required to achieve that goal.
        timeout: int
            The standard timeout in seconds to use on the basic operations
            such as waiting for focus update or closing the window. The value
            can be overridden in some of the methods.

        """
        from pywinauto.application import WindowSpecification

        self.window_spec = WindowSpecification(criteria)
        self.actions = {} if actions is None else actions
        self.timeout = timeout

    @property
    def window(self):
        """ Return the pywinauto wrapper object corresponding to the window
        handle.

        """
        return self.window_spec.WrapperObject()

    @property
    def title(self):
        """ Return the title of the window.
        """
        return self.window.WindowText()

    def invoke_action(self, action):
        """ Execute the action in the specified window.

        Parameters
        ----------
        action : str
            The action to simulate out of the self.actions dictionary

        """
        self.set_focus()
        self.type_key_sequence(self.actions[action])

    def set_focus(self, timeout=None):
        """ Focus the window.

        Parameters
        ----------
        timeout : int
            override the default timeout interval.

        """
        timeout = self.timeout if timeout is None else timeout
        self.window_spec.Wait('exists', timeout=timeout)
        self.window.SetFocus()
        self.window_spec.Wait('ready', timeout=timeout)

    def type_key_sequence(self, key_sequence, with_spaces=False):
        """ Send the key sequence in the Window.

        Parameters
        ----------
        key_sequence : str
            The key sequence (see SendKeys for more information).
        with_spaces :
            Add a space between each key

        .. note: The method does not change the current window focus.

        """
        self.window.TypeKeys(key_sequence, with_spaces=with_spaces)

    def click(self, button='left', position=(None, None)):
        """ Simulate a mouse click in the window.

        Parameter
        ---------
        button : str
            The 'left', 'right' or 'middle' mouse button to click.
        position : tuple
            The coordinates relative to top left corner of the window where
            the mouse click will take place.

        """
        self.set_focus()
        self.window.ClickInput(button=button, double=False, coords=position)

    def doubleclick(self, button='left', position=(None, None),):
        """ Simulate a mouse double-click in the window area

        Parameter
        ---------
        button : str
            The 'left', 'right' or 'middle' mouse button to click.
        position : tuple
            The coordinates relative to top left corner of the window where
            the mouse click will take place.

        """
        self.set_focus()
        self.window.ClickInput(button=button, double=True, coords=position)

    def exists(self, timeout=None):
        """ Return true if the window exists.

        Parameter
        ---------
        timeout : int
            override the default timeout interval.

        """
        timeout = self.timeout if timeout is None else timeout
        return self.window_spec.Exists(timeout)

    def does_not_exist(self, timeout=None):
        """ Return true if the window does not exist.

        Parameter
        ---------
        timeout : int
            override the default timeout interval.

        """
        timeout = self.timeout if timeout is None else timeout
        try:
            self.window_spec.WaitNot('exists', timeout=timeout)
        except RuntimeError:
            return False
        return True

    def close(self, timeout=None):
        """ Closed the window.

        Parameter
        ---------
        timeout : int
            override the default timeout interval.

        """
        timeout = self.timeout if timeout is None else timeout
        self.window.Close()
        self.does_not_exist(timeout)
