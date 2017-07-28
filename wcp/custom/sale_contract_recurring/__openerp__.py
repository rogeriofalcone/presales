# -*- coding: utf-8 -*-
{
    'name': 'Sale Contract Recurring ',
    'version': '1.1',
    'category': 'Sale/Contract Management',
    'description': """
        Sale Contract Recurring
    """,
    'author': 'Bista Solutions Pvt Ltd',
    'website': 'www.bistasolutions.com',
    'depends': ['sale_start_end_dates','account_analytic_analysis',
                'sale_product_container_rental'],
    'data': [
        'views/analytic_view.xml',
        'views/partner_view.xml',
        'views/location_data.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
