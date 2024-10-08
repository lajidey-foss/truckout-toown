# Copyright (c) 2024, Jide Olayinka [lajidey-foss@github.com] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import now, today


class Vanout(Document):
	#pass
    def on_submit(self):
        #check if approved
        print(f'\n\n\n\n\n =========================> \n\n')
        print(f'\n\n *** on submit *** \n\n\n')
        if self.payment_settled == "Approved":
            self.make_rep_debit_entry()
            

    def make_rep_debit_entry(self):
        """ create journal entry"""
        #on_submit
        entry_items = [{
            "doctype":"Journal Entry Account",
			"account":frappe.db.get_single_value('Truckout Setting', 'account_loan'),            
            "debit_in_account_currency":0,
            "credit_in_account_currency": self.total_charged,
            "user_remark": self.sales_voucher
            
		},
        {
            "doctype": "Journal Entry Account",
            "account": "Debtors - TDC",
            "party_type": "Customer",
            "party": self.customer,
            "debit_in_account_currency": self.total_charged,
            "credit_in_account_currency":0,
            "user_remark": "vanout voucher #: "+ self.name
		}]
        jv_doc = frappe.get_doc(dict(
            doctype = "Journal Entry",
            posting_date = today(),
            accounts = entry_items,
            user_remark = "auto generated, from submitted Sales Invoice voucher "+ self.sales_voucher + " and for:"+ self.customer 
		))
        
        jv_doc.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        jv_doc.save(ignore_permissions = True)
        #jv_doc.save()
        jv_doc.submit()
        return jv_doc.name
        
