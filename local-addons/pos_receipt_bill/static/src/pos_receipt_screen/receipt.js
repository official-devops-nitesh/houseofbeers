/** @odoo-module **/

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { onWillStart, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";



patch(OrderReceipt.prototype, {
    setup() {
        this.rpc = useService("rpc");
        this.posOrder = null
        onWillStart(async () => {
            await this.fetchOrderInvoice();
        });
        onWillUnmount(() => {
            $(".pos-receipt").empty()
        })
    },
    async fetchOrderInvoice() {
        try {
            const response = await this.rpc('/api/pos/pos-order', {
                "ordernumber": this.props.data.name
            })
            if (response) {
                this.posOrder = {
                    invoceNumber: response.inv,
                    count: response.count,
                    invoice_date: response.invoice_date,
                    customer: response.customer,
                    pan: response.customerPan,
                    table: response.table
                }
            }
        } catch (error) {
            this.posOrder = {
                invoceNumber: "",
                count: "",
                invoice_date: "",
                customer: "",
                pan: "",
                table: ""
            }
        }
    },
    get invoiceDetail() {
        return this.posOrder
    },
    get amountInWords() {
        var num = this.props.data.amount_total.toString().split('.')[0]

        var ones = ["", "One ", "Two ", "Three ", "Four ", "Five ", "Six ", "Seven ", "Eight ", "Nine ", "Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ", "Fifteen ", "Sixteen ", "Seventeen ", "Eighteen ", "Nineteen "];
        var tens = ["l-defined float management tools to maintain float reliability. Today we are going to ta", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
        if ((num = num.toString()).length > 9)
            return "Overflow: Maximum 9 digits supported";
        var n = ("000000000" + num).substr(-9).match(/^(\d{2})(\d{2})(\d{2})(\d{1})(\d{2})$/);
        if (!n) return;
        var str = "";
        str += n[1] != 0 ? (ones[Number(n[1])] || tens[n[1][0]] + " " + ones[n[1][1]]) + "Crore " : "";
        str += n[2] != 0 ? (ones[Number(n[2])] || tens[n[2][0]] + " " + ones[n[2][1]]) + "Lakh " : "";
        str += n[3] != 0 ? (ones[Number(n[3])] || tens[n[3][0]] + " " + ones[n[3][1]]) + "Thousand " : "";
        str += n[4] != 0 ? (ones[Number(n[4])] || tens[n[4][0]] + " " + ones[n[4][1]]) + "Hundred " : "";
        str += n[5] != 0 ? (str != "" ? "and " : "") + (ones[Number(n[5])] || tens[n[5][0]] + " " + ones[n[5][1]]) : "";
        return str;
    },
    get orderLines() {
        const ordersLinesData = this.props.data.orderlines
        let finalOrderLines = []
        ordersLinesData.map(line => {
            let row,qty,productName,unitPrice,totalPrice
            if (line.order_line.packageStr != "0") {
                productName = line.productName + "-" + line.order_line.packageStr
                qty = line.order_line.input_quantity
                unitPrice = ((parseFloat(line.price.replace("₨", '').replace(",", ''))/parseFloat(line.order_line.input_quantity))/1.13).toFixed(2)
                totalPrice = (parseFloat(line.price.replace("₨", '').replace(",", ''))/1.13).toFixed(2)
            }
            else{
                productName = line.productName
                qty = parseInt(line.qty)
                unitPrice = (parseFloat(line.unitPrice.replace("₨", '').replace(",", ''))/1.13).toFixed(2)
                totalPrice = (parseFloat(line.qty) * parseFloat(line.unitPrice.replace("₨", '').replace(",", '')) / 1.13).toFixed(2)
            }
            row = {
                "productName": productName,
                "qty": qty,
                "rate": unitPrice,
                "amount": totalPrice,
                "customerNote": line.customerNote
            }
            finalOrderLines.push(row)
        })

        return finalOrderLines
    },
    get subTotal() {
        const refactorOrderlines = this.orderLines
        let subtotals = 0
        refactorOrderlines.map(line => {
            if (line.productName != "Discount") {
                subtotals += parseFloat(line.amount)
            }
        })
        return subtotals.toFixed(2)
    },
    get taxAbleAmount() {
        return this.props.data.total_without_tax.toFixed(2)
    },
    get taxVatAmount() {
        return this.props.data.amount_tax.toFixed(2)
    },
    get paymentsMethods() {
        let methods = []
        this.props.data.paymentlines.map(line => {
            methods.push(line.name)
        })
        return methods.map((element, index, array) => {
            return index < array.length - 1 && element !== array[index + 1] ? element + "," : element;
        }).join("");
    }
});