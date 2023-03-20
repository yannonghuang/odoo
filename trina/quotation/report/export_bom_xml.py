# Copyright 2018 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import re
from odoo import models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ExportBomXML(models.AbstractModel):
    _name = "report.export_bom_xml.export_bom_xml"
    _inherit = "report.report_xml.abstract"
    _description = "Export BOM to XML"
    _processed = []

    def _reset(self):
        self._processed.clear()

    def _is_processed(self, bom):
        bom_id = self._export_bom_id(bom)
        if bom_id in self._processed:
            return True
        else:
            self._processed.append(bom_id)
            return False

    def _remove_tags(self, text):
        """Remove html tags from a string"""
        cleaner = re.compile('<.*?>')
        return re.sub(cleaner, '', text)

    def _skip_field(self, f):
        if f.name in ('standard_price', 'default_code', 'name'):
            return False
        return f.type in ('binary', 'image', 'many2one', 'many2many', 'one2many', 'reference') or f.compute or not f.is_editable()

    def _print_fields(self, obj, refs = None):
        result = ''
        for fname, f in obj._fields.items():
            if self._skip_field(f):
                continue
            get_choice = 'get_' + fname + '_display'
            if hasattr(obj, get_choice):
                value = getattr(obj, get_choice)()
            else:
                try:
                    value = getattr(obj, fname)
                except AttributeError:
                    value = None
            # only display fields with values
            if value:
                result += '\t\t\t<field'
                result += ' name = \"' + fname + '\">' + self._remove_tags(str(value)) + '</field>\n'
        if refs:
            for fname, ref in refs.items():
                result += '\t\t\t<field'
                result += ' name = \"' + fname + '\" ref = \"' + ref + '\" />\n'
        return result

    def _export_routing_id(self, operation):
        return 'export_routing_' + str(operation.id)

    def _export_workcenter_id(self, workcenter):
        return 'export_workcenter_' + str(workcenter.id)
    def _export_product_tmpl_id(self, bom):
        return 'export_product_tmpl_' + str(bom.product_tmpl_id.id)

    def _export_bom_id(self, bom):
        return 'export_bom_' + str(bom.id)

    def _export_bom_line_id(self, bom_line):
        return 'export_bom_line_' + str(bom_line.id)

    def _export_product_product_id(self, bom_line):
        return 'export_product_product_' + str(bom_line.product_id.id)

    def _print_routing_workcenter(self, bom):
        result = ''
        for operation in bom.operation_ids:
            routing_id = self._export_routing_id(operation)
            workcenter = operation.workcenter_id
            if workcenter:
                workcenter_id = self._export_workcenter_id(workcenter)
            else:
                workcenter_id = None
            bom_id = self._export_bom_id(bom)

            if workcenter_id:
                result += '\t\t<record id=\"'
                result += workcenter_id
                result += '\" model=\"mrp.workcenter\">\n'
                result += self._print_fields(workcenter, {"resource_calendar_id": "resource.resource_calendar_std"})
                result += '\t\t</record>\n\n'

            result += '\t\t<record id=\"'
            result += routing_id
            result += '\" model=\"mrp.routing.workcenter\">\n'
            result += self._print_fields(operation, {"workcenter_id": workcenter_id, "bom_id": bom_id})
            result += '\t\t</record>\n'


        return result

    def _print_product_template(self, bom):
        product_tmpl_id = self._export_product_tmpl_id(bom)
        result = '\t\t<record id=\"'
        result += product_tmpl_id
        result += '\" model=\"product.product\">\n'
        result += self._print_fields(bom.product_tmpl_id)
        result += '\t\t</record>\n'

        result += '\t\t<record id=\"'
        result += self._export_bom_id(bom) #str(bom.id)
        result += '\" model=\"mrp.bom\">\n'
        result += self._print_fields(bom, {"product_tmpl_id": product_tmpl_id + '_product_template'})
        result += '\t\t</record>\n\n'
        return result

    def _print_product_product(self, bom_line):
        product_id = self._export_product_product_id(bom_line)
        result = '\t\t<record id=\"'
        result += product_id
        result += '\" model=\"product.product\">\n'
        result += self._print_fields(bom_line.product_tmpl_id)
        result += '\t\t</record>\n\n'
        return result

    def _print_bom_line(self, bom_line, bom_id, isTemplate):
        if isTemplate:
            product_id = self._export_product_tmpl_id(bom_line)
        else:
            product_id = self._export_product_product_id(bom_line)
        result = '\t\t<record id=\"'
        result += self._export_bom_line_id(bom_line)
        result += '\" model=\"mrp.bom.line\">\n'
        result += self._print_fields(bom_line, {'bom_id': bom_id, 'product_id': product_id})
        result += '\t\t</record>\n\n'
        return result

    def _print_bom(self, bom):
        if self._is_processed(bom):
            return ''
        result = ''
        result += self._print_product_template(bom)
        result += self._print_routing_workcenter(bom)
        for component_index, line in enumerate(bom.bom_line_ids):
            if line.child_bom_id:
                result += self._print_bom(line.child_bom_id)
                result += self._print_bom_line(line, self._export_bom_id(bom), True)
            else:
                result += self._print_product_product(line)
                result += self._print_bom_line(line, self._export_bom_id(bom), False)
        return result

    def generate_xml_report(self, data, objects):
        header = '<?xml version="1.0" encoding="utf-8"?>\n'
        header += '<odoo>\n'
        header += '\t<data noupdate=\"1\">\n'
        trailer = '\n\t</data>\n'
        trailer += '</odoo>'
        result = ''
        for obj in objects:
            result += self._print_bom(obj)

        self._reset()
        return header + result + trailer

