import frappe

def run():
    frappe.set_user("Administrator")

    # UOMs
    for uom in ["Nos", "Kg", "Km", "Liter", "Trip"]:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

    frappe.db.commit()
    print("UOM fixtures created")

    # Item for transport service
    if not frappe.db.exists("Item", "Transport Service"):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "Transport Service",
            "item_name": "Transport Service",
            "item_group": "Services",
            "is_stock_item": 0,
            "stock_uom": "Nos",
        })
        item.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Transport Service item created")
    else:
        print("Transport Service item exists")

    print("Fixtures ready!")
