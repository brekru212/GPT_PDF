import sqlite3
import pandas as pd
# global vals (note this isn't the most scalable solution since python is single threaded)
con = sqlite3.connect("test.db", check_same_thread=False)


def create_db():
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS invoices(file_name, total, date, seller) ")
    con.commit()


def clean_total(total_str):
    # Making assumption that answer is always in this format: "The grand total on this invoice is $XXXXXX.
    return (total_str.split('$')[-1])


def clean_date(date_str):
    # making assumption that answer is always in this format: "The invoice was created on MM/DD/YYYY."
    return date_str.split('on ')[-1].replace('.', '')


def clean_seller(seller_str):
    # making assumption that answer is always in this format: "The seller on the invoice is <seller name>.
    return seller_str.split('is ')[-1]


def insert_invoice(file_name, total, date, seller):
    cur = con.cursor()
    # Need to do some data cleaning
    cur.execute(
        "INSERT INTO invoices VALUES(?, ?, ?, ?)",
        (file_name, clean_total(total), clean_date(date), clean_seller(seller))
    )
    con.commit()


def get_all_invoices():
    # If we want to use sqllite instead of pandas
    # cur = con.cursor()
    # res = cur.execute("SELECT * FROM invoices")
    # invoices = res.fetchall()
    invoices = pd.read_sql_query("SELECT * FROM invoices", con)
    return invoices


def check_was_invoice_already_processed(file_name):
    cur = con.cursor()
    res = cur.execute("SELECT count(*) FROM invoices where file_name = ?", (file_name,))
    data = res.fetchone()[0]
    return data == 1




