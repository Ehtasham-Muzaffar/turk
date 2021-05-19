# Copyright (c) 2013, Dexciss Technology and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			"fieldname": "date",
			"fieldtype": "Date",
			"label": "Date",
			"width": 150
		},
		{
			"label": "Voucher Type",
			"fieldtype": "Data",
			"fieldname": "voucher_type",
			"width": 150
		},
		{
			"label": "Voucher No.",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"fieldname": "voucher_no",
			"width": 150
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": "Item Code",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"fieldtype": "data",
			"label": "Item Name",
			"width": 170
		},
		{
			"fieldname": "qty",
			"fieldtype": "Float",
			"label": "Quantity",
			"width": 150
		},
		{
			"fieldname": "rate",
			"fieldtype": "Currency",
			"label": "Rate",
			"width": 150
		},
		{
			"fieldname": "debit",
			"fieldtype": "Currency",
			"label": "Debit",
			"width": 150
		},
		{
			"fieldname": "credit",
			"fieldtype": "Currency",
			"label": "Credit",
			"width": 150
		},
		{
			"fieldname": "balance",
			"fieldtype": "Currency",
			"label": "Balance",
			"width": 150
		}
	]
	return columns

def get_data(filters):
	if filters.get('company'):
		query = """select 
			so.transaction_date as date,
			"Sales Order" as voucher_type,
			so.name as voucher_no,
			soi.item_code,
			soi.item_name,
			soi.qty,
			soi.rate,
			soi.amount as debit,
			0 as credit
			from `tabSales Order` as so
			left join `tabSales Order Item` as soi on so.name = soi.parent
			where so.docstatus = 1 and so.company = '{0}' and so.customer = '{1}' and so.transaction_date >= '{2}' and so.transaction_date <= '{3}' 
		union
		select 
			pe.posting_date as date,
			"Payment Entry" as voucher_type,
			pe.name as voucher_no,
			'',
			'',
			'',
			'',
			0 as debit,
			pe.paid_amount as credit
			from `tabPayment Entry` as pe
			where pe.docstatus = 1 and pe.party_type = 'Customer' and pe.company = '{0}' and pe.party = '{1}' and pe.posting_date >= '{2}' and pe.posting_date <= '{3}'
		""".format(filters.get('company'),filters.get('customer'),filters.get('from_date'),filters.get('to_date'))

		# if filters.get('customer'):
		# 	query += " and so.customer = '{0}'".format(filters.get('customer'))

		# if filters.get('receiving_form'):
		# 	query += " and r.name = '{0}'".format(filters.get('receiving_form'))

		# if filters.get('from_date'):
		# 	query += " and r.date >= '{0}'".format(filters.get('from_date'))

		# if filters.get('to_date'):
		# 	query += " and r.date <= '{0}'".format(filters.get('to_date'))

		result = frappe.db.sql(query,as_dict=True)
		data = []
		balance1 = 0
		for row in result:
			row.balance = row.debit - row.credit
			balance1 += row.balance
			row = {
				"date": row.date,
				"voucher_type": row.voucher_type,
				"voucher_no": row.voucher_no,
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": row.qty,
				"rate": row.rate,
				"debit": row.debit,
				"credit": row.credit,
				"balance": balance1
			}
			data.append(row)
		return data
	else:
		return []