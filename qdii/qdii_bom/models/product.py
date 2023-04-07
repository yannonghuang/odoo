# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from itertools import groupby
import operator as py_operator
from odoo import fields, models, api, _
from odoo.tools import groupby
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.addons.mrp.models.product import OPERATORS

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
class QdiiProduct(models.Model):
    _inherit = ["product.template"]

    bom_cost = fields.Float(
        _("BoM Cost"), default=False,
        compute='_compute_bom_cost',
        search='_search_bom_cost',
        help=_("BoM Cost"),
    )

    bom_aggregate = fields.Char(
        _("BoM Aggregate"),
        compute='_compute_bom_aggregate',
        search='_search_bom_aggregate',
        help=_("BoM Aggregate")
    )

    @api.depends('bom_ids.bom_cost', 'standard_price')
    def _compute_bom_cost(self):
        for record in self:
            try:
                record.bom_cost = record.bom_ids[0].bom_cost
            except:
                record.bom_cost = record.standard_price


    def _search_bom_cost(self, operator, value):
        ids = self.env['product.template'].search([]).filtered(
            lambda x: OPERATORS[operator](x.bom_cost, value)).ids
        return [('id', 'in', ids)]
    def __search_bom_cost(self, operator, value):
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

    def _compute_bom_aggregate(self):
        for record in self:
            try:
                record.bom_aggregate = record.bom_ids[0].bom_aggregate
            except:
                record.bom_aggregate = record.display_name

    def _search_bom_aggregate(self, operator, value):
        ids = self.env['product.template'].search([]).filtered(
            lambda x: value.lower() in x.bom_aggregate.lower()).ids
        return [('id', 'in', ids)]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        templateCopy = super(TrinaProduct, self).copy(default=default)
        for template in self:
            if template.bom_count > 0:
                template.bom_ids[0].copy({'product_tmpl_id': templateCopy.id})
        return templateCopy