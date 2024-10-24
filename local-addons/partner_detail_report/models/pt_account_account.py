from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ResCompanyInherited(models.Model):
    _inherit = "res.company"

    rep_account_ids = fields.Many2many('account.account', string='Report Accounts')


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rep_account_ids = fields.Many2many('account.account', string='Report Accounts',related='company_id.rep_account_ids', readonly=False)

