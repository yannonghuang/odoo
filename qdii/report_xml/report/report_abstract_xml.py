# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import re
from io import BytesIO

from odoo import models

_logger = logging.getLogger(__name__)

class ReportXMLAbstract(models.AbstractModel):
    _name = "report.report_xml.abstract"
    _description = "Abstract XML Report"

    def _get_objs_for_report(self, docids, data):
        """
        Returns objects for xml report.  From WebUI these
        are either as docids taken from context.active_ids or
        in the case of wizard are in data.  Manual calls may rely
        on regular context, setting docids, or setting data.

        :param docids: list of integers, typically provided by
            qwebactionmanager for regular Models.
        :param data: dictionary of data, if present typically provided
            by qwebactionmanager for TransientModels.
        :param ids: list of integers, provided by overrides.
        :return: recordset of active model for ids.
        """
        if docids:
            ids = docids
        elif data and "context" in data:
            ids = data["context"].get("active_ids", [])
        else:
            ids = self.env.context.get("active_ids", [])
        return self.env[self.env.context.get("active_model")].browse(ids)


    def create_xml_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        return self.generate_xml_report(data, objs), "xml"

    def generate_xml_report(self, data, objs):
        raise NotImplementedError()
