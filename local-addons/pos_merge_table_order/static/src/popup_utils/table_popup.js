/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState, onMounted } from "@odoo/owl";

export class TablePopup extends AbstractAwaitablePopup {
    static template = "pos_merge_table_order.TablePopup";
    static defaultProps = {
        confirmText: _t("Merge"),
        cancelText: _t("Discard"),
        title: "",
        body: "",
    };

    setup() {
        super.setup();
        this.selectedTable = [];
        this.tablesWithOrders = useState({
            tables: []
        })
        onMounted(this.onMounted);
    }
    onMounted() {
        this.getTableWithOrders()
    }

    getTableWithOrders() {
        const floors = this.env.services.pos.floors
        const currentTable = this.env.services.pos.table;

        const posTables = [];
        floors.map(floor => {
            floor.tables.map(table => {
                if (table.id != currentTable.id) {
                    if (table.order_count > 0)
                        posTables.push({
                            'id': table.id,
                            'name': table.name,
                            "order_count": table.order_count
                        })
                }
            })
        })

        this.tablesWithOrders.tables = posTables
    }

    mergeTable() {
        /* 
            merge selected table orders to current table
        */
        this.selectedTable.map(table => {
            this.env.services.pos.orders.map(item => {
                if (item.tableId == table) {
                    item.orderlines.map(line => {
                        this.env.services.pos.get_order().orderlines.add(line);
                    });
                    this.env.services.pos.removeOrder(item)
                }
            });
        });

        // refresh orderline of current table
        this.env.services.pos.get_order().select_orderline(this.env.services.pos.get_order().get_last_orderline());

        // close popup dialog
        this.cancel()
    }

    onTableClick(event) {
        if ($(event.target).data('click') == '1') {
            $(event.target).data('click', '0')
            $(event.target).css("background-color", "#fff");
            const index = this.selectedTable.indexOf($(event.target).data('table_id'))
            this.selectedTable.splice(index, 1)
        }
        else {
            $(event.target).data('click', '1')
            this.selectedTable.push($(event.target).data('table_id'))
            $(event.target).css("background-color", "#90EE90");
        }
    }
}
