# -*- coding: utf-8 -*-
"""
DB related custom exceptions.
"""


class DBError(Exception):
    """Base exception for all custom database exceptions.

    :kwarg inner_exception: an original exception which was wrapped with
        DBError or its subclasses.
    """

    def __init__(self, inner_exception=None, cause=None):
        super().__init__(str(inner_exception))
        self.inner_exception = inner_exception
        self.cause = cause


class DBDuplicateEntry(DBError):
    """Duplicate entry at unique column error.

    :kwarg columns: a list of unique columns have been attempted to write a
        duplicate entry.
    :type columns: list
    :kwarg value: a value which has been attempted to write. The value will
        be None, if we can't extract it for a particular database backend.
    """

    def __init__(self, columns=None, inner_exception=None, value=None):
        super().__init__(inner_exception)
        self.columns = columns or []
        self.value = value


class DBReferenceError(DBError):
    """Foreign key violation error.

    :param table: a table name in which the reference is directed.
    :type table: str
    :param constraint: a problematic constraint name.
    :type constraint: str
    :param key: a broken reference key name.
    :type key: str
    :param key_table: a table name which contains the key.
    :type key_table: str
    """

    def __init__(self, table, constraint, key, key_table, inner_exception=None):
        super().__init__(inner_exception)
        self.table = table
        self.constraint = constraint
        self.key = key
        self.key_table = key_table


class DBNonExistentConstraint(DBError):
    """Constraint doesn't exist.

    :param table: table name
    :type table: str
    :param constraint: constraint name
    :type table: str
    """

    def __init__(self, table, constraint, inner_exception=None):
        super().__init__(inner_exception)
        self.table = table
        self.constraint = constraint


class DBNonExistentTable(DBError):
    """Table doesn't exist.

    :param table: table name
    :type table: str
    """

    def __init__(self, table, inner_exception=None):
        super().__init__(inner_exception)
        self.table = table


class DBNonExistentDatabase(DBError):
    """Database doesn't exist.

    :param database: database name
    :type database: str
    """

    def __init__(self, database, inner_exception=None):
        super().__init__(inner_exception)
        self.database = database


class DBDeadlock(DBError):
    """Database deadlock error."""

    def __init__(self, inner_exception=None):
        super().__init__(inner_exception)


class DBInvalidUnicodeParameter(Exception):
    """Database unicode error.

    Raised when unicode parameter is passed to a database
    without encoding directive。
    """

    def __init__(self):
        super().__init__('Invalid Parameter:'
                         "Encoding directive wasn't provided.")


class DBConnectionError(DBError):
    """Wrapped connection specific exception.

    Raised when database connection is failed.
    """
    pass


class DBDataError(DBError):
    """Raised for errors that are due to problems with processed data.

    E.g. division by zero, numeric value out of range, incorrect data type, etc.
    """
    pass


class DBNotSupportedError(DBError):
    """Raised when a database backend has raised sqla.exc.NotSupportedError"""
    pass
