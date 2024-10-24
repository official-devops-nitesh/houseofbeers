/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup"
import { _t } from "@web/core/l10n/translation"

export class QRPopup extends AbstractAwaitablePopup {
  static template = "pos_fonepay_qr.PosFoneQrPopup"
  static defaultProps = {
    confirmText: _t("Ok"),
    title: _t("Error"),
    cancelKey: false,
    sound: true,
  }

  setup() {
    super.setup()
    // onMounted(this.onMounted)
    // this.sound = useService("sound")
  }
  // onMounted() {
  //   if (this.sound) {
  //     this.sound.play("error")
  //   }
  // }
}
