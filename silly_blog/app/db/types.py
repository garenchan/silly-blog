# -*- coding: utf-8 -*-
"""
Custom SQLAlchemy types.
"""
from sqlalchemy import types


class Email(types.TypeDecorator):
    """An SQLAlchemy type representing an Email-address."""

    impl = types.String

    def process_bind_param(self, value, dialect):
        """Process/Formats the value before insert it into the db."""
