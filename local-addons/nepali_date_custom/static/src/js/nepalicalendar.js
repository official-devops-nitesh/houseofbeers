/** @odoo-module **/
import { patch } from "@web/core/utils/patch"
import { DateTimeField } from "@web/views/fields/datetime/datetime_field"
import { loadCSS, loadJS } from "@web/core/assets"
import {
  useRef,
  useEffect,
  useState,
  onWillStart,
  onMounted,
  onPatched,
  onWillUnmount,
  onRendered,
  onWillRender,
  onWillUpdateProps,
} from "@odoo/owl"
import { formatDate, formatDateTime } from "@web/core/l10n/dates"
const { DateTime } = luxon

patch(DateTimeField.prototype, {
  // Define the patched method here
  setup() {
    super.setup()
    this.bs_date = useRef("nepali_date")
    this.ad_date = useRef("start-date")
    this.bs_end_date = useRef("nepali_end_date")
    this.ad_end_date = useRef("end-date")

    onWillStart(() => {
      loadCSS(
        "nepali_date_custom/static/lib/nepali_date_picker/css/nepali.datepicker.v4.0.4.min.css"
      )
    })

    useEffect(
      () => {
        const value = this.values[0]
        if (!value) {
          return
        }
        let nepali_timezone = Intl.DateTimeFormat("en-NP", {
          timeZone: "Asia/kathmandu",
        })

        if (this.bs_date.el)
          this.bs_date.el.value = NepaliFunctions.AD2BS(
            nepali_timezone.format(new Date(value)),
            "MM/DD/YYYY"
          )
        if (this.values.length > 1) {
          this.bs_end_date.el.value = NepaliFunctions.AD2BS(
            nepali_timezone.format(new Date(this.values[1])),
            "MM/DD/YYYY"
          )
        }
      },
      () => [this.state.value]
    )

    onMounted(() => {
      this.bs_date.el?.nepaliDatePicker({
        closeOnDateSelect: true,
        ndpYear: true,
        ndpMonth: true,
        onChange: this._onBSChange.bind(this),
      })
      this.bs_end_date.el?.nepaliDatePicker({
        closeOnDateSelect: true,
        ndpYear: true,
        ndpMonth: true,
        onChange: this._onEndBSChange.bind(this),
      })
      if (this.bs_date.el) this.bs_date.el.style["display"] = "none"
      if (this.bs_end_date.el) this.bs_end_date.el.style["display"] = "none"
    })
  },

  _onBSChange(ev) {
    let toUpdate = {}
    toUpdate[this.props.startDateField || this.props.name] =
      DateTime.fromJSDate(new Date(Date.parse(ev.ad)))
    this.props.record.update(toUpdate)
  },

  _onEndBSChange(ev) {
    let toUpdate = {}
    console.log(this.props)
    toUpdate[this.props.endDateField || this.props.name] = DateTime.fromJSDate(
      new Date(Date.parse(ev.ad))
    )
    this.props.record.update(toUpdate)
  },

  async addDate(valueIndex) {
    await super.addDate(valueIndex)
    setTimeout(this.mounted.bind(this, valueIndex), 3000)
  },

  mounted(index) {
    if (index == 0) {
      if (!this.bs_date.el) {
        return
      }
      this.bs_date.el.style["display"] = "none"
      this.bs_date.el.nepaliDatePicker({
        closeOnDateSelect: true,
        onChange: this._onBSChange.bind(this),
      })
    } else {
      if (!this.bs_end_date.el) {
        return
      }
      this.end_date.el.style["display"] = "none"
      this.end_date.el?.nepaliDatePicker({
        closeOnDateSelect: true,
        onChange: this._onEndBSChange.bind(this),
      })
    }
  },
  switch_end_calendar() {
    if (this.bs_end_date.el.style["display"] == "none") {
      this.bs_end_date.el.style["display"] = "block"
      this.ad_end_date.el.style["display"] = "none"
    } else {
      this.bs_end_date.el.style["display"] = "none"
      this.ad_end_date.el.style["display"] = "block"
    }
  },

  switch_calendar() {
    if (this.bs_date.el.style["display"] == "none") {
      this.bs_date.el.style["display"] = "block"
      this.ad_date.el.style["display"] = "none"
    } else {
      this.bs_date.el.style["display"] = "none"
      this.ad_date.el.style["display"] = "block"
    }
  },

  getFormattedValue(valueIndex) {
    const value = this.values[valueIndex]
    let nepali_timezone = Intl.DateTimeFormat("en-NP", {
      timeZone: "Asia/kathmandu",
    })
    let nepali_date = NepaliFunctions.AD2BS(
      nepali_timezone.format(new Date(value)),
      "MM/DD/YYYY"
    )
    return value
      ? this.field.type === "date"
        ? formatDate(value) + "(" + nepali_date + ")"
        : formatDateTime(value) + "(" + nepali_date + ")"
      : ""
  },
})

