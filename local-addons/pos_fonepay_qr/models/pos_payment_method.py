# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import requests
import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import hashlib
import hmac
import qrcode
from io import BytesIO
import base64


_logger = logging.getLogger(__name__)
TIMEOUT = 10

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    fone_pay_secret_key = fields.Char(string='Fone Pay Secret Key')
    fone_pay_username = fields.Char(string='Fone Pay Username')
    fone_pay_password = fields.Char(string='Fone Pay Password')
    fone_pay_merchant = fields.Char(string='Fone Pay Merchant Code')

    # secret_key = 404133f991e64d0eb82c286ee978ba31
    # username = 98510815@fonepay.com
    # password = y@Wp$ER7UsdD#ms
    # merchant = 2103042886
     
    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('fonepay', 'FonePay')]



    def make_fone_pay_qr_request(self,amount,transactionId,referenceId):
        url = "https://merchantapi.fonepay.com/api/merchant/merchantDetailsForThirdParty/thirdPartyDynamicQrDownload"

    
        hash_code = self.generate_fonepay_hash(
                      secret_key=self.fone_pay_secret_key,
                      message=f"{amount},{transactionId},{self.fone_pay_merchant},{referenceId},pos_payment"
                     )

        response = requests.post(url=url,json={
                                "amount": amount,
                                "remarks1": referenceId,
                                "remarks2": "pos_payment",
                                "prn": transactionId,
                                "merchantCode": self.fone_pay_merchant,
                                "dataValidation":hash_code,
                                "username": self.fone_pay_username,
                                "password": self.fone_pay_password})
        
        if response.status_code > 199 and response.status_code<300:   
            try: 
                qr =self.generate_fonepay_qr(response.json()['qrMessage'])
                return {
                    "message":"payment data",
                    "qr":qr,
                    'websocketurl':response.json()['merchantWebSocketUrl']
                }
            except :
                raise UserError(response.json()['message'])

        raise UserError("Failed to connect fonepay server !!")
        


    def generate_fonepay_qr(self,text):
        qr = qrcode.QRCode(
            version=3,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    
    def generate_fonepay_hash(self,secret_key, message):
        try:
            byte_key = bytes(secret_key, 'utf-8')
            hmac_sha512 = hmac.new(
                byte_key,
                bytes(message, 'utf-8'),
                hashlib.sha512
            )
            result = hmac_sha512.hexdigest()
            return result.upper()
        except Exception as exception:
            print(exception)
            return None