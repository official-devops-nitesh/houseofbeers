/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { TablePopup } from "@pos_merge_table_order/popup_utils/table_popup";
import { useService } from "@web/core/utils/hooks";


export class TableMergeButton extends Component {
    static template = "pos_merge_table_order.TableMergeButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");

    }
    click() {
        this.popup.add(TablePopup, {
            title: "Merge Table"
        })
    }
}

ProductScreen.addControlButton({
    component: TableMergeButton,
    condition: function () {
        return true;
    },
});
