/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted } from "@odoo/owl";

export class wkPackagePopup extends AbstractAwaitablePopup {
    static template = "wkPackagePopup";
    static defaultProps = {
        title: 'Confirm ?', value: ''
    };
    setup() {
        super.setup();
        onMounted(this.WkOnMounted);
        var self = this;
        self.options = self.props || {};
        self.quantity;
        self.total_price;
        self.unit_price;
        self.selected;
        self.selected_package;
        self.e;

        // check is this product is from orderline
        if (self.props.orderline) {
            var wkpackage = self.props.orderline.package_id;
            setTimeout(() => {
                $('#' + wkpackage).click();
            }, 200);
        } else {
            self.e = undefined;
        }
    }
    WkOnMounted() {
        var self = this
        if (self && self.options && self.options.package && self.options.package.id) {
            var element = $(`.wk_product_package[id=${self.options.package.id}]`)
            $(element).click();
        }
    }
    apply_package(e) {
        $(".wk_product_package").removeClass("text_shake");
        $('.product_package_qty').removeClass("text_shake");
        if (this.e) {
            if (this.quantity <= 0) {
                $('.product_package_qty').addClass("text_shake");
            } else {
                var current_traget = this.e.currentTarget;
                self.selected = $(current_traget).attr('id');

                //if Order is from orderline
                if (this.props.orderline) {
                    let line = this.props.orderline;
                    if (this.selected >= 0) {
                        console.log(this)
                        // line.customerNote = this.selected_package.name;
                        line.package_id = this.selected_package.id;
                        line.packageStr = this.selected_package.name;
                        line.package_qty = this.selected_package.qty;
                        line.unitPrice = this.unit_price;
                        line.no_of_units = this.selected_package.qty;
                        line.input_quantity = this.quantity;
                        line.quantity = this.quantity;
                        line.price = this.unit_price;
                        line.set_quantity(this.selected_package.qty * this.quantity);
                        line.set_unit_price(line.unitPrice);
                        this.cancel();
                    } else {
                        line.package_id = null;
                        line.packageStr = '0';
                        line.input_quantity = this.quantity;
                        line.quantity = this.quantity;
                        line.price = this.props.product.lst_price;
                        line.set_quantity(this.quantity);
                        this.cancel();
                    }
                } else {
                    //If order is from product page
                    if (this.selected >= 0) {
                        this.apply_package_to_orderline(this.props, this.quantity, this.total_price, this.unit_price, this.selected_package);
                    } else {
                        this.env.services.pos.get_order().add_product(this.props.product, { quantity: this.quantity, merge: false });
                        this.cancel();
                    }
                }
            }
        } else {
            $(".wk_product_package").addClass("text_shake");
        }
    }
    apply_package_to_orderline(options, quantity, total_price, unit_price, selected_package) {
        options['merge'] = false
        this.env.services.pos.get_order().add_product_package(options.product, quantity, total_price, unit_price, selected_package, options);
        this.cancel()
    }
    wk_product_package(event) {
        var e = event;
        var current_traget = e.currentTarget;
        var self = this;
        self.e = e;
        $('.wk_product_package').css('background-color', 'white')
        $(current_traget).css('background-color', 'lightgreen');
        self.selected = $(current_traget).attr('id');
        self.selected_package = self.env.services.pos.db.package_by_id[$(current_traget).attr('id')];
        if (this.e) {
            $(".product_package_qty").css('visibility', 'visible');
            $(".product_total_price").css('visibility', 'visible');
        }
        if (this.props.orderline) {
            $('.wk_package_order_qty').val(parseInt(this.props.orderline.input_quantity));
            setTimeout(() => {
                $('.wk_package_order_qty').change();
            }, 200);
        } else {
            self.quantity = $('.wk_package_order_qty').val();
        }

        if (self.selected >= 0) {
            $('.total_value').html(self.env.utils.formatCurrency((self.get_package_unit_price(self.props.product, self.selected_package, self.quantity)) * self.quantity * self.selected_package.qty));
            self.total_price = (self.get_package_unit_price(self.props.product, self.selected_package, self.quantity)) * self.quantity * self.selected_package.qty
            self.unit_price = self.get_package_unit_price(self.props.product, self.selected_package, self.quantity);
        } else {
            $('.total_value').html(self.env.utils.formatCurrency(self.props.product.lst_price * self.quantity));
            self.total_price = self.env.utils.formatCurrency(self.props.product.lst_price * self.quantity)
        }

        //On Changing the Quantity
        var this_attr = this;
        $('.wk_package_order_qty').on('change', function (e) {
            self.quantity = $('.wk_package_order_qty').val();
            if (self.selected >= 0) {
                $('.total_value').html(self.env.utils.formatCurrency((self.get_package_unit_price(self.props.product, self.selected_package, self.quantity)) * self.quantity * self.selected_package.qty));
                self.total_price = (self.get_package_unit_price(self.props.product, self.selected_package, self.quantity)) * self.quantity * self.selected_package.qty
                self.unit_price = self.get_package_unit_price(self.props.product, self.selected_package, self.quantity);
            } else {
                $('.total_value').html(self.env.utils.formatCurrency(self.props.product.lst_price * self.quantity));
                self.quantity = this_attr.quantity;
                self.total_price = self.props.product.lst_price * self.quantity
            }
        });
    }
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
}