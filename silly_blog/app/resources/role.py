#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import request
import flask_restful as restful

from silly_blog.app.resources import api
from silly_blog.app.models import Role
from silly_blog.contrib.utils import make_error_response, parse_isotime


LOG = logging.getLogger(__file__)


@api.resource("/roles/",
              methods=["GET"],
              endpoint="roles")
class RoleResource(restful.Resource):
    """Controller for user role resources"""

    @staticmethod
    def _get_by_id(role_id):
        role = Role.query.get(role_id)
        if not role:
            return make_error_response(404, "Role %r not found" % role_id)

        return {"role": role.to_dict()}

    def get(self, role_id=None):
        """List roles or show details of a specified one."""
        if role_id:
            return self._get_by_id(role_id)

        query = Role.query

        # filter by name
        name = request.args.get("name")
        if name is not None:
            exp = Role.name.like(''.join(['%', name, '%']))
            query = query.filter(exp)

        # before offset and limit, we get the entry total number
        total = query.count()

        # offset limit related
        page = request.args.get("page", None)
        pagesize = request.args.get("pagesize", None)
        if page and pagesize:
            try:
                page = int(page)
            except ValueError:
                return make_error_response(400, "Unknown page %r" % page)
            try:
                pagesize = int(pagesize)
            except ValueError:
                return make_error_response(400, "Unknown pagesize %r" % pagesize)

            offset = (page - 1) * pagesize  # page starts from 1
            if offset < 0:
                offset = 0
            query = query.offset(offset).limit(pagesize)

        roles = query.all()
        return {
            "roles": [role.to_dict() for role in roles],
            "total": total,
        }
