#from odoo.addons.mrp.report.mrp_report_bom_structure import ReportBomStructure
from odoo import fields, models, _
from odoo import api
from odoo.exceptions import ValidationError
from odoo.addons.mrp.models.product import OPERATORS
from odoo.addons.mrp.models.mrp_bom import MrpBom

import logging

from odoo.addons.qdii_bom.utils.bom_aggregate import BomAggregate

_logger = logging.getLogger(__name__)

class QdiiBom(models.Model):
    _inherit = ['mrp.bom', 'utils.bom_aggregate', 'mail.activity.mixin']
    _description = 'QDII BOM'
    _name = 'mrp.bom'
    #_dico = {}
    _rec_names_search = ['product_tmpl_id', 'code', 'bom_aggregate']

    number_of_components = fields.Integer(
        _("Number of Components"), default=False,
        compute='_compute_number_of_components',
        help=_("Number of Components")
    )

    bom_cost = fields.Float(
        _("BoM Cost"), default=False,
        compute='_compute_bom_cost',
        #search='_search_bom_cost',
        help=_("BoM Cost"),
        #store=True
    )

    bom_cost_store = fields.Float(
        _("BoM Cost"), default=False,
        compute='_compute_bom_cost_store',
        #search='_search_bom_cost',
        help=_("BoM Cost"),
        store=True
    )

    bom_aggregate = fields.Char(
        _("BoM Aggregate"),
        compute='_compute_bom_aggregate',
        search='_search_bom_aggregate',
        help=_("BoM Aggregate")
    )

    bom_lead_time = fields.Integer(
        _("BoM Lead Time"),
        compute='_compute_bom_lead_time',
        search='_search_bom_lead_time',
        help=_("BoM Lead Time"),
    )


    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    cost_currency_id = fields.Many2one(
        'res.currency', 'Cost Currency', compute='_compute_cost_currency_id')
    
    def _get_report_data(self, record):
        return super()._get_report_data(record.id)
        #if record not in self._dico:
        #self._dico[record] = super()._get_report_data(record.id)
        #return self._dico[record]

    def _print_template(self, t):
        template = self.env[t['model']].search([('id', '=', t['id'])])
        #_logger.info('template: %s', template.display_name)
        if template.is_product_variant:
            products = [template]
        else:
            products = template.product_variant_ids
        result = ''
        for product in products:
            result += "; " + product.display_name
            #_logger.info('Product: %s', product.display_name)
            ptav = product.product_template_attribute_value_ids
            tags = product.all_product_tag_ids
            if ptav:
                names = ptav.name_get()
                if names:
                    result += ', '.join(name[1] for name in names)
            if tags:
                result += ', ' + tags.name
        return result

    def _print_aggregate(self, aggregate):
        result = ''
        for template in aggregate:
            result += '; ' + self._print_template(template)
        return result

    def _compute_bom_aggregate(self):
        for record in self:
            report_data = self._get_report_data(record)
            #record.bom_aggregate = report_data['lines']['aggregate']
            record.bom_aggregate = self._print_aggregate(report_data['lines']['aggregate'])

    def _search_bom_aggregate(self, operator, value):
        ids = self.env['mrp.bom'].search([]).filtered(
            lambda x: value.lower() in x.bom_aggregate.lower()).ids
        return [('id', 'in', ids)]

    #@api.depends('sequence')
    def _compute_bom_cost(self):
        for record in self:
            report_data = self._get_report_data(record)
            record.bom_cost = report_data['lines']['bom_cost']
            record.bom_cost_store = record.bom_cost

    @api.depends('bom_cost')
    def _compute_bom_cost_store(self):
        for record in self:
            record.bom_cost_store = record.bom_cost

    def _compute_number_of_components(self):
        for record in self:
            report_data = self._get_report_data(record)
            record.number_of_components = len(report_data['lines']['aggregate'])


    def _search_bom_cost(self, operator, value):
        ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: OPERATORS[operator](x.bom_cost, value)).ids
        return [('id', 'in', ids)]

    def __search_bom_cost(self, operator, value):
        if operator == '>':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost > value).ids
        elif operator == '>=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost >= value).ids
        elif operator == '<':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost < value).ids
        elif operator == '<=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost <= value).ids
        elif operator == '=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost == value).ids
        else:
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_cost != value).ids
        return [('id', 'in', ids)]

    def _compute_bom_lead_time(self):
        for record in self:
            report_data = self._get_report_data(record)
            record.bom_lead_time = report_data['lines']['lead_time']

    def _search_bom_lead_time(self, operator, value):
        ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: OPERATORS[operator](x.bom_lead_time, value)).ids
        return [('id', 'in', ids)]

    def __search_bom_lead_time(self, operator, value):
        if operator == '>':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time > value).ids
        elif operator == '>=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time >= value).ids
        elif operator == '<':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time < value).ids
        elif operator == '<=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time <= value).ids
        elif operator == '=':
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time == value).ids
        else:
            ids = self.env['mrp.bom'].search([]).filtered(
                lambda x: x.bom_lead_time != value).ids
        return [('id', 'in', ids)]

    @api.depends('company_id')
    def _compute_currency_id(self):
        self.currency_id = self.product_tmpl_id.currency_id

    @api.depends_context('company')
    def _compute_cost_currency_id(self):
        self.cost_currency_id = self.product_tmpl_id.cost_currency_id


    volume_uom_name = fields.Char(string='Volume unit of measure label', compute='_compute_volume_uom_name')
    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.product_tmpl_id.volume_uom_name

    weight_uom_name = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name')
    def _compute_weight_uom_name(self):
        self.weight_uom_name = self.product_tmpl_id.weight_uom_name

    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name')
    def _compute_length_uom_name(self):
        self.length_uom_name = self.product_tmpl_id.length_uom_name

    uom_name = fields.Char(string='Unit of Measure Name', compute='_compute_uom_name')        
    def _compute_uom_name(self):
        self.uom_name = self.product_tmpl_id.uom_name           