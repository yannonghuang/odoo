# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from itertools import groupby
import operator as py_operator
from odoo import fields, models, api, _
from odoo.tools import groupby
from odoo.tools.float_utils import float_round, float_is_zero

import logging

_logger = logging.getLogger(__name__)

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class TrinaProduct(models.Model):
    _inherit = ["product.template"]

    bom_cost = fields.Float(
        _("BoM Cost"), default=False,
        compute='_compute_bom_cost',
        search='_search_bom_cost',
        help=_("BoM Cost"),
    )

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

    @api.depends('bom_ids.bom_cost')
    def _compute_bom_cost(self):
        for record in self:
            record.bom_cost = self.bom_ids[0].bom_cost

    def _search_bom_cost(self, operator, value):
        _logger.info('ProductTemplate._search_bom_cost: %s %s', operator, value)
        if operator == '>':
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost > value)
        elif operator == '>=':
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost >= value)
        elif operator == '<':
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost < value)
        elif operator == '<=':
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost <= value)
        elif operator == '=':
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost == value)
        else:
            boms = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost != value)
        ids = []
        for bom in boms:
            ids.append(bom.product_tmpl_id.id)
            _logger.info('template: %s', bom.product_tmpl_id.display_name)
        return [('id', 'in', ids)]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        templateCopy = super(TrinaProduct, self).copy(default=default)
        for template in self:
            if template.bom_count > 0:
                template.bom_ids[0].copy({'product_tmpl_id': templateCopy.id})
        return templateCopy