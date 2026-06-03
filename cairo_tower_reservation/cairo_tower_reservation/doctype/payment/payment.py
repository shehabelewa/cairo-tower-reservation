import frappe
from frappe.model.document import Document

class Payment(Document):

    def on_submit(self):

        frappe.db.set_value(
            "Reservation",
            self.reservation,
            "status",
            "Confirmed"
        )