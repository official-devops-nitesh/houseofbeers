# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name"          :  "POS Manage Packages with Pricelist",
    "summary"       :  """Manage POS product Package and their prices using pricelist. The POS user can create multiple product packages each with a different price and sell them in Odoo POS. Manage Packages|Packages|Custom Packages|Product Packages""",
    "category"      :  "Point of Sale",
    "version"       :  "1.0.1",
    "sequence"      :  1,
    "author"        :  "Webkul Software Pvt. Ltd.",
    "license"       :  "Other proprietary",
    "website"       :  "https://store.webkul.com/odoo-pos-manage-packages-with-pricelist.html",
    "description"   :  """Odoo POS Manage Packages with Pricelist
                            POS Packages
                            POS Product Package
                            POS Wholesale Product
                            POS Wholesale Management
                            Packages in POS
                            Manage Packages in POS
                            POS Package Management
                            Odoo Marketplace Customized Bundle Products
                            Odoo Marketplace Product Pack
                            Odoo product packaging
                            Odoo product pack
                            product package in Odoo
                            Marketplace packs
                            make bundled products
                            bundled products marketplace
                            Odoo marketplace Product packages
                            create Product bundles Odoo
                            Marketplace Product bundles""",
    "live_test_url" :  "http://odoodemo.webkul.com/?module=pos_manage_packages&custom_url=/pos/web/#action=pos.ui",
    "depends"       :  ['point_of_sale'],
    "data"          :  ['views/pos_product_list_view.xml', ],
    "assets"        :  {
                            'point_of_sale._assets_pos': [
                                "/pos_manage_packages/static/src/css/pos_package.css",
                                'pos_manage_packages/static/src/overrides/*',
                            ],
                        },
    "demo"          :  ['demo/demo.xml'],
    "qweb"          :  ['static/src/xml/pos_package.xml'],
    "images"        :  ['static/description/Banner.gif'],
    "application"   :  True,
    "installable"   :  True,
    "auto_install"  :  False,
    "price"         :  79,
    "currency"      :  "USD",
    "pre_init_hook" :  "pre_init_check",
}
