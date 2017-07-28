# -*- coding: utf-8 -*-
{
    'name': 'Delivery Routes',
    'version': '1.1',
    'category': 'Delivery Routes',
    'description': """
        Delivery Routes
    """,
    'author': 'Bista Solutions Pvt Ltd',
    'website': 'www.bistasolutions.com',
    'depends': ['sale_contract_recurring', 'service_fleet'],
    'data': [
        'views/delivery_route_view.xml',
        'views/analytic_view.xml',
        'views/stock_view.xml',
        'wizard/assign_route_view.xml',
        'wizard/plan_route_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
