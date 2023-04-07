# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'QDII BOM Manipulation',
    'version': '1.0',
    'website': 'https://www.odoo.com/app/manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'sequence': 55,
    'summary': 'QDII BOM Manipulation',
    'depends': ['product', 'stock', 'resource', 'mrp', 'sale', 'base_automation', 'report_xml'],
    'data': [
        'views/menu.xml',
        'views/bom.xml',
        'views/product.xml',

        'data/export_bom_xml.xml',
        'data/automated_actions.xml',
    ],
    'demo': [],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'assets': {

    },
    'license': 'LGPL-3',
}
