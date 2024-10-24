# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.model
    def enable_lot_settings(self):
        enable_env = self.env['res.config.settings'].create({'group_stock_packaging': True, 'group_product_pricelist': True,
                                                            'product_pricelist_setting': 'advanced', 'group_sale_pricelist': True })
        enable_env.execute()

class PosProductListItem(models.Model):
    _inherit = 'product.pricelist.item'

    package_id = fields.Many2one('product.packaging', 'Product Packaging', ondelete='cascade',
                            help="Specify a Packaging if this rule only applies to products belonging to this Packaging")
    product_package_id = fields.Many2one('product.product', 'Product', ondelete="cascade",
                                help="Specify the product on which the package is being applied")
    applied_on = fields.Selection(selection_add=[('3_product_package', 'Product Package')], ondelete={'3_product_package': 'set default'})

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('applied_on', False):
                if values.get('applied_on') == '3_product_package':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
                else:
                    values.update(dict(product_package_id=None, package_id=None))
        res = super(PosProductListItem, self).create(values)
        return res

    def write(self, values):
        if values.get('applied_on', False):
            if values.get('applied_on') == '3_product_package':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            else:
                values.update(dict(product_package_id=None, package_id=None))
        res = super(PosProductListItem, self).write(values)
        return res

    @api.depends('package_id', 'product_package_id', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _compute_name_and_price(self):
        super(PosProductListItem, self)._compute_name_and_price()
        for item in self:
            if item.package_id:
                item.name = _("%s[%s]") % (item.package_id.product_id.name, item.package_id.name)

    @api.onchange('product_package_id')
    def _onchange_product_package_id(self):
        if self.product_package_id:
            self.package_id = None

class PosOrderLineItem(models.Model):
    _inherit = "pos.order.line"

    package_id = fields.Many2one('product.packaging', 'Product Packaging', help="Specify a Packaging of the Products")
    input_quantity=fields.Float('Package Quantity', digits='Product Unit of Measure')
    packageStr=fields.Char('Package Name')


    def _export_for_ui(self, orderline):
        result = super()._export_for_ui(orderline)
        _logger.info("orderlin###################################################33e: %r", orderline)
        result['package_id'] = orderline.package_id.id
        result['input_quantity']=orderline.input_quantity
        result['no_of_units']=orderline.input_quantity
        result['packageStr']=orderline.package_id.name
        return result
    

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'product.packaging' not in result:
            result.append('product.packaging')
        return result

    def _loader_params_product_packaging(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'sequence', 'product_id', 'qty', 'barcode']}}

    def _get_pos_ui_product_packaging(self, params):
        return self.env['product.packaging'].search_read(**params['search_params'])

    def _product_pricelist_item_fields(self):
        result = super()._product_pricelist_item_fields()
        result = result + ['package_id','product_package_id','applied_on']
        return result

    def _loader_params_product_pricelist_item(self):
        result = super()._loader_params_product_pricelist_item()
        result['search_params']['fields'].extend(['package_id', 'product_package_id', 'applied_on'])
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('packaging_ids')
        return result
