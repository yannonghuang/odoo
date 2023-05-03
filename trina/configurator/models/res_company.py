# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path
from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)


class TrinaCompany(models.Model):
    _inherit = ["res.company"]
    _name = "res.company"
    _description = 'Trina Companies'

    @api.model
    def _get_main_company(self):
        try:
            main_company = self.env['res.company'].sudo().search([('name', '=', 'Trina Solar')], limit=1, order="id")
        except ValueError:
            main_company = None
        if main_company == [] or main_company is None:
            main_company = super()._get_main_company()

        return main_company
