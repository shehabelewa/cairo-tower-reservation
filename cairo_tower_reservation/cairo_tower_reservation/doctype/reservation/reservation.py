import frappe
import qrcode
import io

from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.file_manager import save_file


class Reservation(Document):

    def validate(self):

        # Calculate Total Amount
        ticket_price = frappe.db.get_value(
            "Ticket Type",
            self.ticket_type,
            "price"
        ) or 0

        self.total_amount = ticket_price * (self.number_of_tickets or 0)

        # Prevent booking in the past
        if self.visit_date and getdate(self.visit_date) < getdate():
            frappe.throw(
                _("You cannot book a reservation for a past date.")
            )

        # Capacity Control
        if self.visit_date and self.visit_time:

            existing_tickets = frappe.db.sql("""
                SELECT COALESCE(SUM(number_of_tickets), 0)
                FROM `tabReservation`
                WHERE visit_date=%s
                AND visit_time=%s
                AND status != 'Cancelled'
                AND name != %s
            """, (
                self.visit_date,
                self.visit_time,
                self.name
            ))[0][0]

            max_capacity = 100

            requested_tickets = self.number_of_tickets or 0

            if existing_tickets + requested_tickets > max_capacity:
                remaining = max_capacity - existing_tickets

                frappe.throw(
                    _("Only {0} spots remaining for this time slot.").format(
                        remaining
                    )
                )

    def after_insert(self):
        self.generate_qr_code()

    def generate_qr_code(self):

        # Don't generate twice
        if self.qr_code:
            return

        qr_data = f"""
Reservation: {self.name}
Visit Date: {self.visit_date}
Visit Time: {self.visit_time}
Ticket Type: {self.ticket_type}
Number Of Tickets: {self.number_of_tickets}
Total Amount: {self.total_amount}
Status: {self.status}
"""

        qr = qrcode.make(qr_data)

        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        file_doc = save_file(
            f"{self.name}_qr.png",
            buffer.getvalue(),
            self.doctype,
            self.name,
            is_private=0
        )

        self.db_set("qr_code", file_doc.file_url)