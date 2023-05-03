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
    _description = 'Trina Product'

    length = fields.Float(
        _("Length"), default=1.0,
        help=_("Length"),
    )
    


    material = fields.Selection(
        [('AL6005-T5', 'AL6005-T5'), ('AL6005-T5 SUS304', 'AL6005-T5 SUS304')],
        default='AL6005-T5',
        required="True"
    )

    wind_load = fields.Float(
        _("Wind Load"), default=10,
        help=_("Wind Load"),
    )
    

    power_uom_name = fields.Char(string='Power unit of measure label', compute='_compute_power_uom_name')
    def _compute_power_uom_name(self):
        self.power_uom_name = self.env.ref('configurator.product_uom_kw').display_name

    angle_uom_name = fields.Char(string='Angle unit of measure label', compute='_compute_angle_uom_name')
    def _compute_angle_uom_name(self):
        self.angle_uom_name = self.env.ref('configurator.product_uom_degree').display_name

    wind_load_uom_name = fields.Char(string='Wind load unit of measure label', compute='_compute_wind_load_uom_name')
    def _compute_wind_load_uom_name(self):
        self.wind_load_uom_name = self.env.ref('configurator.product_uom_wind_load').display_name

    


         