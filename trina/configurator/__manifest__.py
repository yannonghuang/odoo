# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Trina Configurator',
    'version': '1.0',
    'website': 'https://www.odoo.com/app/manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'sequence': 55,
    'summary': 'Trina Product Configurator',
    'depends': ['qdii_bom'],
    'data': [
        'data/uom_data.xml',
        'views/menu.xml',
        'views/bom.xml',
        'views/product.xml',
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
