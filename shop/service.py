class PaymentGateway:
    def create_payment(self, amount, order_id):
        pass

    def verify_payment(self, amount, authority):
        pass

    def get_payment_url(self, authority):
        pass


class ZibalGateway(PaymentGateway):
    pass