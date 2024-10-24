/* @odoo-modules */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { wkPackagePopup } from "@pos_manage_packages/overrides/popups";
Orderline.props.line = {
    order_line: { type: Object, optional: true },
}
patch(Orderline.prototype, {
    setup() {
        super.setup()
    },
    clikorderlinebtn(orderline) {
        this.env.services.popup.add(wkPackagePopup, {
            'product': orderline.product,
            'pos': orderline.pos,
            'orderline':orderline
        })
    }

});

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
    },
    _setValue(val) {
        const { numpadMode } = this.pos;
        const selectedLine = this.currentOrder.get_selected_orderline();
        if (selectedLine) {
            if (numpadMode === "quantity") {
                if (!selectedLine.package_id||val===""||val === "remove") {
                    super._setValue(val)
                } else {
                    this.pos.env.services.popup.add(wkPackagePopup, {
                        'product': this.currentOrder.get_selected_orderline().product,
                        'pos': this.pos,
                        'orderline': this.currentOrder.get_selected_orderline(),
                    });
                }
            } else {
                super._setValue(val)
            }
        } else {
            super._setValue(val)
        }
    },
   
  
});
