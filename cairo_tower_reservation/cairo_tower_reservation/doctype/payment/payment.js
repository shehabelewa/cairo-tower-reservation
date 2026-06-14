frappe.ui.form.on("Payment", {
    reservation(frm) {

        if (frm.doc.reservation) {

            frappe.db.get_value(
                "Reservation",
                frm.doc.reservation,
                "total_amount"
            ).then(r => {

                frm.set_value(
                    "amount",
                    r.message.total_amount
                );

            });

        }

    }
});