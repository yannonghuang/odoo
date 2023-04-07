# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from itertools import groupby
import operator as py_operator
from odoo import fields, models, api, _
from odoo.tools import groupby
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.addons.mrp.models.product import OPERATORS
from odoo.addons.qdii_bom.models.product import QdiiProduct

import logging

_logger = logging.getLogger(__name__)

'''
OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}
'''
class TrinaProduct(QdiiProduct):
    _inherit = ["product.template"]

    length = fields.Float(
        _("Length"), default=1.0,
        help=_("Length"),
    )
    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name')

    material = fields.Selection(
        [('AL6005-T5', 'AL6005-T5'), ('AL6005-T5 SUS304', 'AL6005-T5 SUS304')],
        default='AL6005-T5',
        required="True"
    )

    wind_load = fields.Float(
        _("Wind Load"), default=10,
        help=_("Wind Load"),
    )
    def _compute_length_uom_name(self):
        self.length_uom_name = self._get_length_uom_name_from_ir_config_parameter()