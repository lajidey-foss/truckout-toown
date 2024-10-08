

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import today

def rep_loadout(doc, method):
    """ checking fig"""
    print(f'\n\n\n\n\n\n\n\n =========================> \n\n\n\n\n\n\n\n\n')
    
    #enable_truckout
    if not frappe.db.get_single_value('Truckout Setting', 'enable_truckout'):
        return

    if frappe.db.get_single_value('Truckout Setting', 'enable_truckout'):
        if frappe.db.get_single_value('Truckout Setting', 'enable_on_item'):
            print('====== itemwise path ======')
            #BILL_TYPE='Product'
            #make_itemwise(doc, BILL_TYPE)
            make_itemwise(doc)

        elif frappe.db.get_single_value('Truckout Setting', 'enable_on_customer'):
            print("====== partywise path =====")
            #BILL_TYPE='Service'
            make_partywise(doc)
        
        else:
            return


def make_rep_loadout(data, type, qty, amount):
    """ get all variable first """
    #check if customer is part of the scheme
    is_customer_part, party_wise_value = frappe.get_value('Customer',data.customer,['custom_join_scheme', 'custom_loadout_charges'])
    if not is_customer_part:
        return
    #create the truckout document
    set_items_row = []
    set_items_row.append({
        "vanout_type": type,
        "qty":qty,
        "charged_amount": amount if type != 'Service' else party_wise_value
    })
    rt_doc = frappe.new_doc("Vanout")
    rt_doc.update({
        "date_out":data.posting_date,
        "time_out": today(),
        "customer": data.customer,
        "sales_voucher": data.name,
        "payment_settled": "Approved",
        "vanout_details":set_items_row,
        "total_charged": (qty * amount) if type !='Service' else (qty * party_wise_value)
    })
    rt_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True

    rt_doc.save()
    #below line of code isnt needed as workflow show be used
    rt_doc.submit()
    

def make_itemwise(data):
    " get all value from sales invoice item "
    #detail_items_record = []
    BILL_TYPE = "Product"
    qtotal = 0.0
    setting_item = frappe.db.get_single_value('Truckout Setting', 'select_item')
    charges_per_qty = frappe.db.get_single_value('Truckout Setting', 'charges_per_qty')

    for ir in data.items:
        if (ir.item_code == setting_item and ir.amount > 0.0):
            qtotal += ir.qty

    #create the load out and save for workflow also send notification to approval manager
    make_rep_loadout(data, BILL_TYPE, qtotal, charges_per_qty)
    

def make_partywise(data):
    " get all values from customer doctype if enabled else return"
    BILL_TYPE='Service'
    #minium_charge_amount
    min_charge = frappe.db.get_single_value('Truckout Setting', 'minium_charge_amount')    
    make_rep_loadout(data,BILL_TYPE,1,min_charge)
