# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Trina Quotation',
    'version': '1.0',
    'website': 'https://www.odoo.com/app/manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'sequence': 55,
    'summary': 'Trina Quotation Management',
    'depends': ['product', 'stock', 'resource', 'mrp', 'sale', 'report_xml'],
    'data': [
        'views/menu.xml',
        'views/bom.xml',
        'views/product.xml',

        'data/export_bom_xml.xml',
    ],
    'demo': [
        'data/mrp_demo.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'assets': {

    },
    'license': 'LGPL-3',
}
