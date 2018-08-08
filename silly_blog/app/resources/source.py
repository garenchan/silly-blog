#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import flask_restful as restful

from silly_blog.app import api
from silly_blog.app.models import Source
from silly_blog.contrib.utils import make_error_response


LOG = logging.getLogger(__name__)


@api.resource("/sources/", methods=["GET"], endpoint="sources")
@api.resource("/sources/<string:source_id>", methods=["GET"], endpoint="source")
class SourceResource(restful.Resource):
    """Controller for article source resources"""

    @staticmethod
    def _get_by_id(source_id):
        source = Source.query.get(source_id)
        if not source:
            return make_error_response(404, "Source %r not found" % source_id)

        return {"source": source.to_dict()}

    def get(self, source_id=None):
        """List sources or show details of a specified one."""
        if source_id:
            return self._get_by_id(source_id)

        sources = Source.query.all()
        return {
            "sources": [source.to_dict() for source in sources]
        }
