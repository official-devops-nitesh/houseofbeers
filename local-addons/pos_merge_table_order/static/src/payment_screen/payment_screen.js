/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";




patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.toggleIsToInvoice()
    },

    toggleIsToInvoice() {
        this.currentOrder.set_to_invoice(true);
        this.render(false)
    },
    shouldDownloadInvoice() {
        return false
    }
});