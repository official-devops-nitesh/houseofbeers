/**@odoo-module */


/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { deserializeDate } from "@web/core/l10n/dates";
import { Order, Orderline, Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch"
import { roundPrecision as round_pr } from "@web/core/utils/numbers";
import { _t } from "@web/core/l10n/translation";

import { wkPackagePopup } from "@pos_manage_packages/overrides/popups";
const { DateTime } = luxon;
patch(PosStore.prototype, {
    async setup() {
        this.packages = [];
        await super.setup(...arguments)
    },
    async _processData(loadedData) {
        await super._processData(...arguments);
        var result = loadedData["product.packaging"]
        var self = this;
        self.db.package_by_id = {};
        self.packages = result;
        result.forEach(element => {
            self.db.package_by_id[element.id] = element;
        });
    },
    async addProductFromUi(product, options) {
        if (product && (product.packaging_ids).length > 0) {
            this.popup.add(wkPackagePopup, {
                'product': product,
                'pos': this
            })
        }
        else {
            super.addProductFromUi(product, options)
        }

    }
});
patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments)
        if (options.json) {
            this.package_id = options.json.package_id;
            this.packageStr = options.json.packageStr;
            this.package_qty = options.json.package_qty;
            this.unitPrice = options.json.unitPrice;
            this.no_of_units = options.json.no_of_units;
            this.input_quantity = options.json.input_quantity;
        } else {
            this.package_id = null;
            this.packageStr = '0';
            this.package_qty = '0';
            this.unitPrice = 0;
            this.no_of_units = 0;
            this.input_quantity = 0;
        }
    },
    get_package_str() {
        
        return this.packageStr;
    },
    get_per_package_price() {
        return (this.quantity * this.price)/this.input_quantity;
    },
    getDisplayData() {
        const result = super.getDisplayData()
        result["order_line"] = this
        return result
    },
    export_for_printing() {
        var dict = super.export_for_printing(this);
        dict.package_id = this.package_id;
        dict.input_quantity = this.input_quantity;
        return dict;
    },
    export_as_JSON() {
        var loaded = super.export_as_JSON(this);
        loaded.package_id = this.package_id;
        loaded.packageStr = this.packageStr;
        loaded.package_qty = this.package_qty;
        loaded.unitPrice = this.unitPrice;
        loaded.no_of_units = this.no_of_units;
        loaded.input_quantity = this.input_quantity;
        return loaded;
    },
    get_package_unit_price(product, packages, package_quantity, recurring = false) {
        var self = this;
        var pricelist = product.pos.get_order().pricelist;
        if (recurring && !pricelist) {
            alert(
                'An error occurred when loading product prices. ' +
                'Make sure all pricelists are available in the POS.'
            );
        }
        const rules = !pricelist ? [] : (pricelist.items).filter((item) => (item.applied_on == "3_product_package") && (item.product_package_id[0] == product.id));
        var price = product.get_price(pricelist, 1);

        rules.find((rule) => {
            if (rule.package_id[0] == packages.id) {
                if (rule.min_quantity && package_quantity < rule.min_quantity) {
                    return false;
                }
                if (rule.compute_price === 'fixed') {
                    if (rule.package_id && self.env.services.pos.db.package_by_id[rule.package_id[0]]) {
                        price = rule.fixed_price / self.env.services.pos.db.package_by_id[rule.package_id[0]].qty;
                    } else {
                        price = rule.fixed_price;
                    }
                    return true;
                } else if (rule.compute_price === 'percentage') {
                    if (rule.package_id && self.env.services.pos.db.package_by_id[rule.package_id[0]]) {
                        // price = (price - (price * (rule.percent_price / 100))) / self.env.services.pos.db.package_by_id[rule.package_id[0]].qty;
                        price = (price - (price * (rule.percent_price / 100))) ;
                    // } else {
                    //     price = price - (price * (rule.percent_price / 100));
                    }
                    return true;
                } else {
                    var price_limit = price;
                    price = price - (price * (rule.price_discount / 100));
                    if (rule.price_round) {
                        price = round_pr(price, rule.price_round);
                    }
                    if (rule.price_surcharge) {
                        price += rule.price_surcharge;
                    }
                    if (rule.price_min_margin) {
                        price = Math.max(price, price_limit + rule.price_min_margin);
                    }
                    if (rule.price_max_margin) {
                        price = Math.min(price, price_limit + rule.price_max_margin);
                    }
                    return true;
                }
            } else {
                return false;
            }
        });
        return price;
    }
});

patch(Order.prototype, {
    set_pricelist(pricelist) {
        var self=this
        super.set_pricelist(...arguments);
        const orderlines = this.get_orderlines();

        const lines_to_recompute = orderlines.filter(
            (line) =>
                line.price_type === "original" && line.package_id
        );
        lines_to_recompute.forEach((line) => {
            line.set_unit_price(
                line.get_package_unit_price(line.product,self.env.services.pos.db.package_by_id[line.package_id],line.package_qty)
            );
            self.fix_tax_included_price(line);
        });
    },


    add_product_package(product, quantity, total_price, unit_price, selected_package, options) {
        const line = new Orderline(
            { env: this.env },
            { pos: this.pos, order: this, product: product, quantity: quantity }
        );

        line.package_id = selected_package.id;
        line.packageStr = selected_package.name;
        line.package_qty = selected_package.qty;
        line.unitPrice = unit_price;
        line.input_quantity = quantity;
        line.no_of_units = selected_package.qty;
        line.price = unit_price;
        if (this._printed) {
            // when adding product with a barcode while being in receipt screen
            this.pos.removeOrder(this);
            return this.pos.add_new_order().add_product_package(product, options);
        }
        this.assert_editable();
        options = options || {};
        // var attr = JSON.parse(JSON.stringify(product));
        product.pos = this.pos;
        product.order = this;
        quantity = options.quantity ? options.quantity : line.input_quantity;

        if (selected_package.qty !== undefined) {
            line.set_quantity(selected_package.qty * line.input_quantity);
        }

        if (unit_price !== undefined) {
            line.set_unit_price(line.unitPrice);
        }

        //To substract from the unit price the included taxes mapped by the fiscal position
        this.fix_tax_included_price(line);

        if (options.discount !== undefined) {
            line.set_discount(options.discount);
        }

        if (options.extras !== undefined) {
            for (var prop in options.extras) {
                line[prop] = options.extras[prop];
            }
        }

        var to_merge_orderline;
        for (var i = 0; i < this.orderlines.length; i++) {
            if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
                to_merge_orderline = this.orderlines.at(i);
            }
        }
        if (to_merge_orderline) {
            to_merge_orderline.merge(line);
        } else {
            this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());

        if (line.has_product_lot) {
            this.display_lot_popup();
        }
    }

});


patch(Product.prototype, {
    get_price(pricelist, quantity, price_extra = 0, recurring = false) {
        var self = this;
        const date = DateTime.now();
        if (recurring && !pricelist) {
            alert(
                _t(
                    "An error occurred when loading product prices. " +
                    "Make sure all pricelists are available in the POS."
                )
            );
        }
        var category_ids = [];
        var category = this.categ;
        while (category) {
            category_ids.push(category.id);
            category = category.parent;
        }

        const rules = !pricelist
            ? []
            : (pricelist.items).filter((item) => {
               return  (!item.product_package_id) ?
                    (!item.product_tmpl_id || item.product_tmpl_id[0] === self.product_tmpl_id) &&
                        (!item.product_id || item.product_id[0] === self.id) &&
                        (!item.categ_id || this.parent_category_ids.concat(this.categ.id).includes(item.categ_id[0])) &&
                        (!item.date_start || deserializeDate(item.date_start) <= date) &&
                        (!item.date_end || deserializeDate(item.date_end) >= date)
                :false
            });
        let price = this.lst_price
        const rule = rules.find((rule) => !rule.min_quantity || quantity >= rule.min_quantity);
        if (!rule) {
            return price;
        }
        if (rule.base === "pricelist") {
            const base_pricelist = this.pos.pricelists.find(
                (pricelist) => pricelist.id === rule.base_pricelist_id[0]
            );
            if (base_pricelist) {
                price = this.get_price(base_pricelist, quantity, 0, true);
            }
        } else if (rule.base === "standard_price") {
            price = this.standard_price;
        }

        if (rule.compute_price === "fixed") {
            price = rule.fixed_price;
        } else if (rule.compute_price === "percentage") {
            price = price - price * (rule.percent_price / 100);
        } else {
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }

        // This return value has to be rounded with round_di before
        // being used further. Note that this cannot happen here,
        // because it would cause inconsistencies with the backend for
        // pricelist that have base == 'pricelist'.
        return price;
    }
    ,
    async getAddProductOptions(base_code, event) {
        var self = this;
        var product = this
        if (base_code && product && (product.packaging_ids).length > 0) {
            const { confirmed } = this.pos.env.services.popup.add(wkPackagePopup, {
                'product': product,
                'pos': self.env.services.pos,
                'package': self.env.services.pos.db.product_packaging_by_barcode[base_code.code]
            });
            if (confirmed) {
                return super.getAddProductOptions(...arguments)
            }
        } else {
            return super.getAddProductOptions(...arguments)
        }
    }
});