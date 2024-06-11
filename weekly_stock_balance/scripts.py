import frappe
from frappe.utils import today

def send_weekly_stock_balance_report():
    date = today()
    query = """
            SELECT
                COALESCE(parent_item.variant_of, bin.item_code) AS parent_item_code,
                CASE 
                    WHEN parent_item.variant_of IS NOT NULL THEN parent_item2.item_name
                    ELSE parent_item.item_name
                END AS parent_item_name,
                SUM(bin.actual_qty) AS total_qty
            FROM
                `tabBin` bin
            LEFT JOIN
                `tabItem` parent_item ON bin.item_code = parent_item.name
            LEFT JOIN
                `tabItem` parent_item2 ON parent_item.variant_of = parent_item2.name
            GROUP BY
                parent_item_code
            ORDER BY
                parent_item_code
        """
    data = frappe.db.sql(query, as_dict=1)

    # generate report content
    report_content = "Item Code,Item Name,Total Qty\n"
    for row in data:
        report_content += f"{row['parent_item_code']},{row['parent_item_name']},{row['total_qty']}\n"

    # send email to stock managers
    recipients_email = frappe.get_value("User", {"role_profile_name": "Item Manager"}, "email")
    if not recipients_email:
            frappe.throw("No recipient email found for the specified user.")

    recipients = [recipients_email]
    subject = f"Weekly Stock Balance Report {date}"
    message = f"Please find attached the weekly stock balance report for {date}"
    filename = f"stock_balance_report_{date}.csv"
    attachments = [{"fname": filename, "fcontent": report_content}]

    frappe.sendmail(recipients=recipients, subject=subject, message=message, attachments=attachments)
