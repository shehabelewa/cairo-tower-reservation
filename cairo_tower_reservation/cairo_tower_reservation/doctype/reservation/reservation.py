import frappe
from frappe.model.document import Document

class Reservation(Document):

    def validate(self):

        ticket_price = frappe.db.get_value(
            "Ticket Type",
            self.ticket_type,
            "price"
        )

        self.total_amount = (
            ticket_price * self.number_of_tickets
        )