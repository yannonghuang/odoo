#from odoo.addons.mrp.report.mrp_report_bom_structure import ReportBomStructure
from odoo import fields, _
from odoo import api
from odoo.exceptions import ValidationError
from odoo.addons.mrp.models.product import OPERATORS

import logging

from odoo.addons.quotation.utils.bom_aggregate import BomAggregate

_logger = logging.getLogger(__name__)

#class TrinaBom(ReportBomStructure):
class TrinaBom(BomAggregate):
    _inherit = ['mrp.bom']
    _description = 'Trina BOM'
    _dico = {}
    _rec_names_search = ['product_tmpl_id', 'code', 'bom_aggregate']

    number_of_panels = fields.Integer(
        _("Number of Panels"), default=248,
        help=_("Number of Panels"),
     )

    panel_length = fields.Float(
        _("Panel Length"), default=2102,
        help=_("Panel Length"),
    )

    panel_width = fields.Float(
        _("Panel Width"), default=1040,
        help=_("Panel Width"),
    )

    panel_power = fields.Float(
        _("Panel Power"), default=400,
        help=_("Panel Power"),
    )

    total_power = fields.Float(
        _("Total Power"),
        help=_("Total Power"),
        compute='_compute_total_power'
    )

    panel_spacing = fields.Float(
        _("Panel Spacing"), default=1090,
        help=_("Panel Spacing"),
    )

    channel_length = fields.Float(
        _("Channel Length"), default=4400,
        help=_("Channel Length"),
    )

    number_of_isolators = fields.Integer(
        _("Number of Isolators"), default=5,
        help=_("Number of Isolators"),
     )

    wind_load = fields.Float(
        _("Wind Load"), default=10,
        help=_("Wind Load"),
    )

    tilt_angle = fields.Float(
        _("Tilt Angle"), default=45,
        help=_("Tilt Angle"),
    )

    installation_type = fields.Selection(
        [('roof', 'Roof Top'), ('ground', 'Ground Based')],
        default='roof',
        required="True"
    )

    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name')

    def _compute_total_power(self):
        self.total_power = self.panel_power * self.number_of_panels

    def _compute_length_uom_name(self):
        self.length_uom_name = self._get_length_uom_name_from_ir_config_parameter()

    @api.model
    def _get_length_uom_name_from_ir_config_parameter(self):
        return self._get_length_uom_id_from_ir_config_parameter().display_name

    @api.model
    def _get_length_uom_id_from_ir_config_parameter(self):
        """ Get the unit of measure to interpret the `length`, 'width', 'height' field.
        By default, we considerer that length are expressed in millimeters. Users can configure
        to express them in feet by adding an ir.config_parameter record with "product.volume_in_cubic_feet"
        as key and "1" as value.
        """
        product_length_in_feet_param = self.env['ir.config_parameter'].sudo().get_param('product.volume_in_cubic_feet')
        if product_length_in_feet_param == '1':
            return self.env.ref('uom.product_uom_foot')
        else:
            return self.env.ref('uom.product_uom_millimeter')


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


    @api.constrains('wind_load')
    def _check_wind_load(self):
        for record in self:
            aggregate = self._get_report_data(record)['lines']['aggregate']
            for t in aggregate:
                if (record.product_tmpl_id.id == t['id']):
                    continue
                template = self.env[t['model']].search([('id', '=', t['id'])])
                #_logger.info('template: %s, record: %s', template.id, record.product_tmpl_id.id)
                if template.is_product_variant:
                    products = [template]
                else:
                    products = template.product_variant_ids
                for product in products:
                    if record.wind_load > product.wind_load:
                        raise ValidationError("Component %s\'s wind load does not meet requirements." % (product.display_name))
        # all records passed the test, don't return anything

    def _get_report_data(self, record):
        #if record not in self._dico:
        self._dico[record] = super()._get_report_data(record.id)
        return self._dico[record]

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
