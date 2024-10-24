/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store"
import { PaymentFonepay } from "@pos_fonepay_qr/app/payment_stripe"

register_payment_method("fonepay", PaymentFonepay)
