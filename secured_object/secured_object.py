#!/usr/bin/env python3
"""
I am attempting to overwrite the builting object.__dict__ and prevent
users from interacting with properties in ways outside of what I want

Goals:
    - Users should be able to get and set existing properties
    - Users should not be able to add or remove additional properties
    - Users should not be able to alter object's methods
    - Users should not be able to mutate read-only properties
"""


from typing import Any


class _Internal_None:
    """
    Used to define a class/type that a user is not expected to have.
    Used as default for non-existant values in internal dictionary
    """
    def __new__(cls):
        """
        Only the class should ever exist
        """
        return _Internal_None


class _Internal(dict):

    def __init__(self, *args):
        super().__init__(args)
        self.locked = False  # locking ocures outside of desire modification
        self.frozen = False  # freezing occures after Secure's init()
        self.read_only_vars = []

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get(self, key: any) -> any:
        return super().get(key, _Internal_None)

    def _add_read_only(_, caller: any, super: any) -> None:

        read_only = object.__getattribute__(caller, 'read_only_set')
        for i in super.__dir__():
            read_only.add(i)
        read_only.add('read_only')


class Secure:
    """
    Class the fulfills the requirements of the module.

    Attributes:
        x (int): a default value a user is able to mutate
        y (int): a default value a user is able to mutate
        read_only (int): a default value a user can only get not set

    Methods:
        look_at_x() -> None: prints the current value of 'x'
        look_at_y() -> None: prints the current calue of 'y'
        add() -> int: returns the result of var x + var y
    """

    def __init__(self):
        object.__setattr__(self, 'internal', _Internal())
        object.__setattr__(self, 'read_only_set', set())
        internal = object.__getattribute__(self, 'internal')
        self.x = 100
        self.y = 50
        self.read_only = 5
        internal._add_read_only(self, super())
        internal.freeze()
        internal.lock()  # prevents access to internal directly


    def __getattribute__(self, __name: str) -> Any:
        internal = object.__getattribute__(self, 'internal')
        if __name == 'internal' and not internal.locked:
            return object.__getattribute__(self, __name)

        internal.unlock()
        r = self.internal.get(__name)
        internal.lock()

        if r is _Internal_None:
            try:
                rtr = object.__getattribute__(self, __name)
                if callable(rtr):
                    return rtr
            except AttributeError:
                # handled on next line - prevents splash
                pass  # following line used to control error message
            raise AttributeError(f"type 'Secure' has no attribute '{__name}'")
        return r

    def __setattr__(self, __name: str, __value: Any) -> None:
        internal = object.__getattribute__(self, 'internal')
        if internal.frozen:  # init is complete
            # cannot change read_only
            if __name in object.__getattribute__(self, 'read_only_set') or \
               callable(getattr(self, __name)):
                raise AttributeError(f"{__name} is marked as read_only")
            # cannot create new properties
            if not hasattr(self, __name):
                raise AttributeError(
                    "type 'Secure' cannot contain new attributes"
                    )

        internal.unlock()
        self.internal[__name] = __value
        internal.lock()

    def __dir__(self) -> list:
        internal = object.__getattribute__(self, 'internal')
        rtr = set([i for i in internal.keys() if i[0] != '_'])
        for i in object.__getattribute__(Secure, '__dict__'):
            if i not in ["__module__", "__dict__", "__doc__"]:
                rtr.add(i)
        return list(rtr)

    def __delattr__(self, __name: str) -> None:
        internal = object.__getattribute__(self, 'internal')
        if internal.frozen:
            raise AttributeError("type 'Secure' cannot remove attributes")
        object.__delattr__(self, __name)

    def look_at_x(self) -> None:
        """Displays the very shiny 'x' var"""
        print(self.x)

    def look_at_y(self) -> None:
        """Displays a very plain 'y' var"""
        print(self.y)

    def add(self) -> int:
        """Returns the addition of x and y"""
        return self.x + self.y
