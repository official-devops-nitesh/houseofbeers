/** @odoo-module */
/* global StripeTerminal */

import { _t } from "@web/core/l10n/translation"
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface"
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup"
import { QRPopup } from "@pos_fonepay_qr/app/popup"
import { Component, onMounted, useState, markup } from "@odoo/owl"

export class PaymentFonepay extends PaymentInterface {
  setup() {
    super.setup(...arguments)
    // console.log(this)
    // this.state = useState(null)
    // this.createStripeTerminal();
  }

  async send_payment_cancel(order, cid) {
    await super.send_payment_cancel(order, cid)
    order.selected_paymentline.set_payment_status("retry")
    this._incrementRetry(order.uid)
    return true
  }

  async send_payment_request(cid) {
    // transaction
    await super.send_payment_request(cid)
    const paymentLine = this.pos.get_order()?.selected_paymentline
    const order = this.pos?.selectedOrder
    let retry = this._retryCountUtility(order.uid)
    let transactionId = order.name
      .replace(" ", "")
      .replaceAll("-", "")
      .toUpperCase()
    if (retry > 0) {
      transactionId = transactionId.concat("retry", retry)
    }
    const transactionAmount = paymentLine.amount

    const referencePrefix = this.pos.config?.name.replace(/\s/g, "").slice(0, 4)
    const referenceId = referencePrefix.concat(
      Math.floor(Math.random() * 1000000000)
    )
    const response = await this.makePaymentRequest(
      transactionAmount,
      transactionId,
      referenceId
    )

    if (!response) {
      paymentLine.set_payment_status("force_done")
      this._incrementRetry(order.uid)
      return false
    }

    this.createSocket(response.websocketurl, order, response.qr)
    this._incrementRetry(order.uid)
    return false
  }

  async makePaymentRequest(amount, transactionId, referenceId) {
    try {
      const data = await this.env.services.orm.silent.call(
        "pos.payment.method",
        "make_fone_pay_qr_request",
        [[this.payment_method.id], amount, transactionId, referenceId]
      )
      return data
    } catch (error) {
      console.log(error)
      this._showError(
        "Failed to get response from fonepay server!!",
        "FonePay Payment Request"
      )
      return false
    }
  }

  async createSocket(url, order, qr) {
    const socket = new WebSocket(url)
    const paymentLine = this.pos.get_order()?.selected_paymentline
    setTimeout(() => paymentLine.set_payment_status("waitingPayment"))

    // Connection opened
    socket.addEventListener("open", (event) => {
      this.env.services.popup.add(QRPopup, {
        title: "FonePay QR",
        body: qr,
      })
    })

    socket.addEventListener("error", (event) => {
      paymentLine.set_payment_status("force_done")
      this._incrementRetry(order.uid)
    })

    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data)
      const transactionStatus = JSON.parse(data.transactionStatus)
      if (transactionStatus?.paymentSuccess) {
        document.getElementById("qrconfirm")?.click()
        paymentLine.set_payment_status("done")
        this.env.services.notification.add("Payment Success", {
          title: "Congrats",
          type: "success",
        })
        socket.close()
      }
    })
  }

  _retryCountUtility(uid, remove = false) {
    if (remove) {
      localStorage.removeItem(uid)
    } else {
      return localStorage.getItem(uid) || (localStorage.setItem(uid, 0) && 0)
    }
  }

  _incrementRetry(uid) {
    let retry = localStorage.getItem(uid)
    localStorage.setItem(uid, ++retry)
  }

  _showError(error_msg, title) {
    this.env.services.popup.add(ErrorPopup, {
      title: title || _t("Fone Pay Error"),
      body: error_msg,
    })
  }
}
