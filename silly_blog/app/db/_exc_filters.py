# -*- coding: utf-8 -*-
"""
Define exception redefinitions for SQLAlchemy DBAPI exceptions.
"""
import sys
import re
import collections
import logging

from sqlalchemy import exc as sqla_exc
from sqlalchemy import event

from silly_blog.app.db import exception


LOG = logging.getLogger(__name__)

_registry = collections.defaultdict(
    lambda: collections.defaultdict(list))


def filters(dbname, exception_type, regex):
    """Mark a function as receiving a filtered exception.

    :param dbname: string database name, e.g. 'mysql'
    :param exception_type: a SQLAlchemy database exception class, which
        extends from :class:`sqlalchemy.exc.DBAPIError`.
    :param regex: a string, or a collection of strings, that will be processed
        as matching regular expressions.
    """
    def wrapper(fn):
        _registry[dbname][exception_type].extend(
            (fn, re.compile(reg))
            for reg in (regex if isinstance(regex, tuple) else (regex,))
        )
        return fn
    return wrapper


@filters('mysql', sqla_exc.OperationalError, r'^.*\b1213\b.*Deadlock found.*')
@filters('mysql', sqla_exc.DatabaseError,
         r'^.*\b1205\b.*Lock wait timeout exceeded.*')
@filters('mysql', sqla_exc.InternalError, r'^.*\b1213\b.*Deadlock found.*')
@filters('mysql', sqla_exc.InternalError,
         r'^.*\b1213\b.*detected deadlock/conflict.*')
def _deadlock_error(operational_error, match, engine_name, is_disconnect):
    """Filter for MySQL deadlock error."""
    raise exception.DBDeadlock(operational_error)


@filters('mysql', sqla_exc.IntegrityError,
         r"^.*\b1062\b.*Duplicate entry '(?P<value>.*)'"
         r" for key '(?P<columns>[^']+)'.*$")
@filters('mysql', sqla_exc.IntegrityError,
         r"^.*\b1062\b.*Duplicate entry \\'(?P<value>.*)\\'"
         r" for key \\'(?P<columns>.+)\\'.*$")
def _default_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for MySQL duplicate key error."""
    try:
        columns = match.group('columns')
    except IndexError:
        columns = []
    else:
        uniqbase = 'uniq_'
        if not columns.startswith(uniqbase):
            columns = [columns]
        else:
            columns = columns[len(uniqbase):].split('0')[1:]

    value = match.groupdict().get('value')

    raise exception.DBDuplicateEntry(columns, integrity_error, value)


@filters('sqlite', sqla_exc.IntegrityError,
         (r'^.*columns?(?P<columns>[^)]+)(is|are)\s+not\s+unique$',
          r'^.*UNIQUE\s+constraint\s+failed:\s+(?P<columns>.+)$',
          r'^.*PRIMARY\s+KEY\s+must\s+be\s+unique.*$'))
def _sqlite_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for SQLite duplicate key error."""
    columns = []
    try:
        columns = match.group('columns')
        columns = [c.split('.')[-1] for c in columns.strip().split(', ')]
    except IndexError:
        pass

    raise exception.DBDuplicateEntry(columns, integrity_error)


@filters('sqlite', sqla_exc.IntegrityError,
         r'(?i).*foreign key constraint failed')
@filters('mysql', sqla_exc.IntegrityError,
         r'.*Cannot (add|delete) or update a (child|parent) row: '
         'a foreign key constraint fails \([`"].+[`"]\.[`"](?P<table>.+)[`"], '
         'CONSTRAINT [`"](?P<constraint>.+)[`"] FOREIGN KEY '
         '\([`"](?P<key>.+)[`"]\) REFERENCES [`"](?P<key_table>.+)[`"] ')
def _foreign_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for foreign key error."""
    try:
        table = match.group('table')
    except IndexError:
        table = None
    try:
        constraint = match.group('constraint')
    except IndexError:
        constraint = None
    try:
        key = match.group('key')
    except IndexError:
        key = None
    try:
        key_table = match.group('key_table')
    except IndexError:
        key_table = None

    raise exception.DBReferenceError(
        table, constraint, key, key_table, integrity_error)


@filters('mysql', sqla_exc.InternalError,
         r".*1091,.*Can't DROP (?:FOREIGN KEY )?['`](?P<constraint>.+)['`]; "
         'check that .* exists')
@filters('mysql', sqla_exc.OperationalError,
         r".*1091,.*Can't DROP (?:FOREIGN KEY )?['`](?P<constraint>.+)['`]; "
         'check that .* exists')
@filters('mysql', sqla_exc.InternalError,
         r".*1025,.*Error on rename of '.+/(?P<relation>.+)' to ")
def _check_constraint_non_existing(
    programming_error, match, engine_name, is_disconnect):
    """Filter for constraint non existing errors."""
    try:
        relation = match.group('relation')
    except IndexError:
        relation = None
    try:
        constraint = match.group('constraint')
    except IndexError:
        constraint = None

    raise exception.DBNonExistentConstraint(
        relation, constraint, programming_error)


@filters('sqlite', sqla_exc.OperationalError,
         r'.* no such table: (?P<table>.+)')
@filters('mysql', sqla_exc.InternalError,
         r".*1051,.*Unknown table '(.+\.)?(?P<table>.+)'\"")
@filters('mysql', sqla_exc.OperationalError,
         r".*1051,.*Unknown table '(.+\.)?(?P<table>.+)'\"")
def _check_table_non_existing(
        programming_error, match, engine_name, is_disconnect):
    """Filter for table non existing errors."""
    try:
        table = match.group('table')
    except IndexError:
        table = None

    raise exception.DBNonExistentTable(table, programming_error)


@filters('sqlite', sqla_exc.OperationalError,
         '.*unable to open database file.*')
@filters('mysql', sqla_exc.InternalError,
         r".*1049,.*Unknown database '(?P<database>.+)'\"")
@filters('mysql', sqla_exc.OperationalError,
         r".*1049,.*Unknown database '(?P<database>.+)'\"")
def _check_database_non_existing(error, match, engine_name, is_disconnect):
    """Filter for database non existing errors."""
    try:
        database = match.group('database')
    except IndexError:
        database = None

    raise exception.DBNonExistentDatabase(database, error)


@filters('mysql', sqla_exc.DBAPIError, r'.*\b1146\b')
def _raise_mysql_table_doesnt_exist_asis(
        error, match, engine_name, is_disconnect):
    """Raise MySQL error 1146 as is.

    Raise MySQL error 1146 as is, so that it does not conflict with
    the MySQL dialect's checking a table not existing.
    """
    raise error


@filters('sqlite', sqla_exc.ProgrammingError,
         r'(?i).*You must not use 8-bit bytestrings*')
@filters('mysql', sqla_exc.OperationalError,
         r'.*(1292|1366).*Incorrect \w+ value.*')
@filters('mysql', sqla_exc.DataError, r'.*1265.*Data truncated for column.*')
@filters('mysql', sqla_exc.DataError,
         r'.*1264.*Out of range value for column.*')
@filters('mysql', sqla_exc.InternalError, r'^.*1366.*Incorrect string value:*')
@filters('mysql', sqla_exc.DataError, r'.*1406.*Data too long for column.*')
def _raise_data_error(error, match, engine_name, is_disconnect):
    """Raise DBDataError exception for different data errors."""
    raise exception.DBDataError(error)


@filters('mysql', sqla_exc.OperationalError,
         r".*\(1305,\s+\'SAVEPOINT\s+(.+)\s+does not exist\'\)")
def _raise_savepoints_as_dberrors(error, match, engine_name, is_disconnect):
    raise exception.DBError(error)


@filters('*', sqla_exc.OperationalError, r'.*')
def _raise_operational_errors_directly_filter(
        operational_error, match, engine_name, is_disconnect):
    """Filter for all remaining OperationalError classes and apply."""
    if is_disconnect:
        raise exception.DBConnectionError(operational_error)
    else:
        raise operational_error


@filters('mysql', sqla_exc.OperationalError,
         r'.*\(.*(?:2002|2003|2006|2013|1047)')
@filters('mysql', sqla_exc.InternalError, r'.*\(.*(?:1927)')
@filters('mysql', sqla_exc.InternalError, r'.*Packet sequence number wrong')
def _is_db_connection_error(
        operational_error, match, engine_name, is_disconnect):
    """Detect the exception as indicating a recoverable error on connect."""
    raise exception.DBConnectionError(operational_error)


@filters('*', sqla_exc.NotSupportedError, r'.*')
def _raise_for_not_supported_error(error, match, engine_name, is_disconnect):
    raise exception.DBNotSupportedError(error)


@filters('*', sqla_exc.DBAPIError, r'.*')
def _raise_for_remaining_db_api_errors(
        error, match, engine_name, is_disconnect):
    """Filter for remaining DBAPIErrors."""
    if is_disconnect:
        raise exception.DBConnectionError(error)
    else:
        LOG.exception('DBError exception wrapped from %s' % error)
        raise exception.DBError(error)


@filters('*', UnicodeEncodeError, r'.*')
def _raise_for_unicode_encode_error(error, match, engine_name, is_disconnect):
    raise exception.DBInvalidUnicodeParameter()


@filters('*', Exception, r'.*')
def _raise_for_all_other_errors(error, match, engine_name, is_disconnect):
    LOG.exception('DBError exception wrapped from %s' % error)
    raise exception.DBError(error)


_ROLLBACK_CAUSE_KEY = 'silly_blog.db.sp_rollback_cause'


def handler(context):
    """Iterate through available filters and invoke those which match.

    The first one which raises wins. The order in which the filters
    are attempted is sorted by specificity - dialect name or "*",
    exception class per method resolution order (``__mro__``).
    Method resolution order is used so that filter rules indicating a
    more specific exception class are attempted first.
    """
    def _dialect_registries(engine):
        dialect_name = engine.dialect.name
        if dialect_name in _registry:
            yield _registry[dialect_name]
        if '*' in _registry:
            yield _registry['*']

    for per_dialect in _dialect_registries(context.engine):
        for exc in (context.sqlalchemy_exception, context.original_exception):
            for cls in exc.__class__.__mro__:
                if cls not in per_dialect:
                    continue

                regexp_reg = per_dialect[cls]
                for fn, regexp in regexp_reg:
                    match = regexp.match(exc.args[0])
                    if match:
                        try:
                            fn(exc, match, context.engine.dialect.name,
                               context.is_disconnect)
                        except exception.DBError as dbe:
                            if (context.connection and
                                    not context.connection.closed and
                                    not context.connection.invalidated and
                                    _ROLLBACK_CAUSE_KEY in context.connection.info):
                                dbe.cause = context.connection.info.pop(
                                    _ROLLBACK_CAUSE_KEY)
                            if isinstance(dbe, exception.DBConnectionError):
                                context.is_disconnect = True
                            return dbe


def register_engine(engine):
    event.listen(engine, 'handle_error', handler, retval=True)

    @event.listens_for(engine, 'rollback_savepoint')
    def rollback_savepoint(conn, name, context):
        exc_info = sys.exc_info()
        if exc_info[1]:
            if not conn.invalidated:
                conn.info[_ROLLBACK_CAUSE_KEY] = exc_info[1]
        del exc_info

    @event.listens_for(engine, 'rollback')
    @event.listens_for(engine, 'commit')
    def pop_exc_tx(conn):
        if not conn.invalidated:
            conn.info.pop(_ROLLBACK_CAUSE_KEY, None)

    @event.listens_for(engine, 'checkin')
    def pop_exc_checkin(dbapi_conn, connection_record):
        connection_record.info.pop(_ROLLBACK_CAUSE_KEY, None)
