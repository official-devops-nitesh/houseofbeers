from odoo import fields, models, api, _


class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    rep_label2 = fields.Char('Report Label', compute='get_rep_label2', store=True)

    @api.depends('product_id', 'move_id.invoice_origin')
    def get_rep_label2(self):
        self.rep_label2 = False
        for rec in self:
            if rec.product_id and rec.move_id.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                # if rec.product_id.type == 'service':
                if rec.move_id.invoice_origin:
                    if 'RMA' in rec.move_id.invoice_origin:
                        rma_obj = self.env['repair.order'].search([('name', '=', rec.move_id.invoice_origin)], limit=1)
                        if rma_obj:
                            rec.rep_label2 = rec.product_id.name + " - " + rma_obj.product_id.name
                    else:
                        rec.rep_label2 = rec.product_id.name
                else:
                    rec.rep_label2 = rec.product_id.name[:]
                    # else:
                # rec.rep_label2 = rec.product_id.name[:50]
            else:
                rec.rep_label2 = " "
