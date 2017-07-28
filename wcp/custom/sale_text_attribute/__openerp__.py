# -*- coding: utf-8 -*-
{
    'name': 'Text Attribute',
    'version': '1.1',
    'category': 'Text Attribute',
    'description': """
        Text Attribute
    """,
    'author': 'Bista Solutions Pvt Ltd',
    'website': 'www.bistasolutions.com',
    'depends': ['sale','base','product','mrp','sale_product_variants','service'],
    'data': [
        'views/sale_view.xml',
        'views/mrp_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
