from odoo import fields, _
from odoo import api
from odoo.exceptions import ValidationError
from odoo.addons.mrp.models.product import OPERATORS

import logging

from odoo.addons.qdii_bom.models.bom import QdiiBom

_logger = logging.getLogger(__name__)

class TrinaBom(QdiiBom):
    #_inherit = ['mrp.bom']
    _description = 'Trina BOM'
    _name = 'mrp.bom'
    #_dico = {}
    #_rec_names_search = ['product_tmpl_id', 'code', 'bom_aggregate']

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

