#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import mysql.connector
import modules.connect as ct

# Function to find the index of the specified column
def find_column_index():
	# Get the entered column name
	column_name = column_name_entry.get()
	
	# Connect to the MySQL database
	try:
		connection = mysql.connector.connect(
			host=ct.host,
			user=ct.user,
			password=ct.passwd,
			database=ct.database  # Replace with your database name
		)
		
		cursor = connection.cursor()
		
		# Query to find the index of the specified column
		query = f"SELECT COLUMN_NAME, ORDINAL_POSITION FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'USS_Video_Equipment' AND TABLE_NAME = 'equipment' AND COLUMN_NAME = '{column_name}';"
		
		cursor.execute(query)
		
		# Fetch the result
		result = cursor.fetchone()
		
		if result:
			column_index = result[1]
			messagebox.showinfo("Column Index", f"The index of column '{column_name}' is {column_index}")
		else:
			messagebox.showerror("Error", f"Column '{column_name}' not found in the table")
			
		cursor.close()
		connection.close()
		
	except mysql.connector.Error as e:
		messagebox.showerror("MySQL Error", f"Error: {e}")
		
# Create the main window
root = tk.Tk()
root.title("Column Index Finder")

# Create and place a label
label = tk.Label(root, text="Enter Column Name:")
label.pack()

# Create an entry widget
column_name_entry = tk.Entry(root)
column_name_entry.pack()

# Create and place a button to find the column index
find_button = tk.Button(root, text="Find Column Index", command=find_column_index)
find_button.pack()

# Run the GUI application
root.mainloop()
