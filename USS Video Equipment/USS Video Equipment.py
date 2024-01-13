#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from tkinter import font as tkFont
from PIL import Image, ImageTk
import os
import webbrowser
import modules.connect as ct

# Global Variables
current_edit_id = None

# Database connection
def create_db_connection():
    return mysql.connector.connect(
        host=ct.host, user=ct.user, passwd=ct.passwd, database=ct.database
    )

# Utility Functions
def open_hyperlink(url):
    webbrowser.open(url)
    
def get_column_index(cursor, column_name):
    """Get the index of the column in cursor.description."""
    for i, col_info in enumerate(cursor.description):
        if col_info[0] == column_name:
            return i
    return None

def initialize_fonts():
    global bold_font, value_font
    bold_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
    value_font = tkFont.Font(family="Helvetica", size=10)

# Image Display Function
def display_image(item_name):
    global image_label  # Declare as global to update the reference
    
    # Check and load the image if exists
    found_image = False
    for extension in ['.png', '.jpg']:
        image_path = os.path.join('Pics', f'{item_name}{extension}')
        if os.path.exists(image_path):
            found_image = True
            break
        
    if found_image:
        # Load the image
        image = Image.open(image_path)
        
        # Maintain aspect ratio
        max_size = 400
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(image)
        
        # Create a new label for each image
        if 'image_label' in globals():
            image_label.destroy()
        image_label = tk.Label(image_frame, image=photo, anchor="w")
        image_label.image = photo  # Keep a reference
        image_label.grid(row=0, column=0, sticky='w')  # Align to the left
    else:
        # Clear the image if not found
        if 'image_label' in globals():
            image_label.destroy()
        image_label = tk.Label(image_frame)
        image_label.grid(row=0, column=0, sticky='w')

# Custome Widget Classes
class DateInput:
    def __init__(self, parent, row, column):
        self.months = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
        
        # Find the longest month name
        max_length = max(len(month) for month in self.months)
        
        self.month_var = tk.StringVar(parent)
        self.month_var.set(self.months[0])
    
        self.day_var = tk.StringVar(parent)
        self.year_var = tk.StringVar(parent)
    
        self.month_menu = tk.OptionMenu(parent, self.month_var, *self.months)
    
        # Set a fixed pixel width for the month OptionMenu
        pixel_width = 5 # Adjust this value based on the UI requirement
        self.month_menu.config(width=pixel_width)
        self.month_menu.grid(row=row, column=column, sticky="e")
        
        self.day_entry = tk.Entry(parent, textvariable=self.day_var, width=2)
        self.day_entry.grid(row=row, column=column+1, sticky="w")
        
        self.year_entry = tk.Entry(parent, textvariable=self.year_var, width=4)
        self.year_entry.grid(row=row, column=column+2, sticky="w")
        
    def get_date(self):
        month = self.months.index(self.month_var.get()) + 1
        day = int(self.day_var.get())
        year = int(self.year_var.get())
        return f"{year}-{month:02d}-{day:02d}"  # Format as YYYY-MM-DD
    
    def set_date(self, date_str):
            if date_str:
                year, month, day = map(int, date_str.split('-'))
                self.month_var.set(self.months[month - 1])  # Set the month
                self.day_var.set(str(day))  # Set the day
                self.year_var.set(str(year))  # Set the year

class ColumnDropdown:
    def __init__(self, parent, column_name, db_connection, row, column, button_label="Item"):
        self.column_name = column_name
        self.conn = db_connection  # Use the existing db connection object
        self.var = tk.StringVar(parent)
        self.update_options()
        
        self.dropdown_menu = tk.OptionMenu(parent, self.var, *self.options)
        self.dropdown_menu.grid(row=row, column=column, sticky='w')
        
        self.add_popup_button = tk.Button(parent, text=button_label, command=self.create_add_popup)
        self.add_popup_button.grid(row=row, column=column+1, sticky='w')
        
        self.new_entry = tk.Entry(parent)
        self.new_entry.grid(row=row+1, column=column, columnspan=3)
        
    def update_options(self):
        self.options = ['None'] + self.get_unique_column_values()
        self.var.set(self.options[0])
        
    def get_unique_column_values(self):
        cursor = self.conn.cursor()
        query = f"SELECT DISTINCT {self.column_name} FROM equipment WHERE {self.column_name} IS NOT NULL"
        cursor.execute(query)
        return [row[0] for row in cursor]
    
    def add_new_option(self):
        new_value = self.new_entry.get()
        if new_value:
            db_value = None if new_value == 'None' else new_value
            
            if db_value not in self.options:
                cursor = self.conn.cursor()
                query = f"INSERT INTO equipment ({self.column_name}) VALUES (%s)"
                cursor.execute(query, (db_value,))
                self.conn.commit()
                self.update_options()
                self.var.set(new_value)
                
    def add_new_option_to_list(self, new_value):
        if new_value and new_value != 'None' and new_value not in self.options:
            self.options.append(new_value)
            self.var.set(new_value)
            self.update_dropdown()
                
    def update_dropdown(self):
        # Get the current grid options for repositioning the updated dropdown
        grid_info = self.dropdown_menu.grid_info()
        row = grid_info['row']
        column = grid_info['column']
        columnspan = grid_info['columnspan']
        
        # Destroy the old dropdown and create a new one with updated options
        self.dropdown_menu.destroy()
        self.dropdown_menu = tk.OptionMenu(self.dropdown_menu.master, self.var, *self.options)
        self.dropdown_menu.grid(row=row, column=column, columnspan=columnspan)
    
    def create_add_popup(self):
        formatted_column_name = self.column_name.replace('_', ' ').title()
        
        popup = tk.Toplevel()
        popup.title(f"Add New {formatted_column_name}")
        
        add_frame = tk.Frame(popup)
        add_frame.pack(padx=30, pady=10)
        
        new_value_entry = tk.Entry(add_frame)
        new_value_entry.pack()
        
        def add_value():
            new_value = new_value_entry.get()
            self.add_new_option_to_list(new_value)
            popup.destroy()
            
        add_button = tk.Button(add_frame, text="Add", command=add_value)
        add_button.pack()
                
# Data Manipulation Functions
###
def populate_fields_for_edit(selected_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM equipment WHERE id = %s", (selected_id,))
        row = cursor.fetchone()
        if row:
            entry_name.delete(0, tk.END)
            entry_name.insert(0, row[1] if row[1] else '')  # Handle None for name
            entry_brand.delete(0, tk.END)
            entry_brand.insert(0, row[3] if row[3] else '')  # Handle None for brand
            entry_model.delete(0, tk.END)
            entry_model.insert(0, row[4] if row[4] else '')  # Handle None for model
            entry_model_number.delete(0, tk.END)
            entry_description.delete(0, tk.END)
            entry_description.insert(0, row[14] if row[14] else '')  # Handle None for description
            entry_sn.delete(0, tk.END)
            entry_sn.insert(0, row[5] if row[5] else '')  # Serial Number
            status_var.set(row[11] if row[11] else '')  # Set status
            entry_purchaseCompany.delete(0, tk.END)
            entry_purchaseCompany.insert(0, row[6] if row[6] else '')  # Purchase Company
            purchase_date = row[7].strftime('%Y-%m-%d') if row[7] else ''
            purchase_date_input.set_date(purchase_date)  # Purchase Date
            entry_cost.delete(0, tk.END)
            entry_cost.insert(0, str(row[8] if row[8] else ''))  # Cost
            insured_date = row[9].strftime('%Y-%m-%d') if row[9] else ''
            entry_url.delete(0, tk.END)
            entry_url.insert(0, str(row[15] if row[15] else ''))
            entry_model_number.insert(0, row[16] if row[16] else '')  # Set model number
            kit_name_index = 17 # replace with the actual index of kit_name
            kit_name = row[kit_name_index] if row[kit_name_index] else 'None'
            kit_name_dropdown.var.set(kit_name)
            type_index = 2
            type_name = row[type_index] if row[type_index] else 'None'
            type_dropdown.var.set(type_name)
            # Check and set the insured date
            if insured_date:
                date_insured_input.set_date(insured_date)
                is_insured_var.set(True)
            else:
                is_insured_var.set(False)
            toggle_insured()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()

###
def update_equipment():
    global current_edit_id
    if not current_edit_id:
        messagebox.showinfo("Update Error", "No equipment selected for update")
        return
    
    # Save the current selection index before updating
    selected_index = listbox.curselection()
    
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        equipment_name = entry_name.get()
        equipment_name = entry_name.get()
        equipment_brand = entry_brand.get()
        equipment_model = entry_model.get()
        equipment_description = entry_description.get()
        equipment_sn = entry_sn.get()
        equipment_purchaseCompany = entry_purchaseCompany.get()
        equipment_purchaseDate = purchase_date_input.get_date()
        equipment_cost = entry_cost.get()
        equipment_url = entry_url.get()
        equipment_dateInsured = date_insured_input.get_date() if is_insured_var.get() else None
        equipment_status = status_var.get()
        equipment_model_number = entry_model_number.get()
        equipment_kit_name = kit_name_dropdown.var.get()
        equipment_type = type_dropdown.var.get()
        if equipment_kit_name == 'None':
            equipment_kit_name = None
        
        query = """UPDATE equipment SET 
                    name=%s, brand=%s, model=%s, description=%s, serial_number=%s,
                    purchase_company=%s, date_of_purchase=%s, cost=%s, website_url=%s, 
                    date_insured=%s, status=%s, model_number=%s, kit_name=%s, type=%s
                    WHERE id=%s"""
        cursor.execute(query, (equipment_name, equipment_brand, equipment_model, equipment_description, 
                                equipment_sn, equipment_purchaseCompany, equipment_purchaseDate, 
                                equipment_cost, equipment_url, equipment_dateInsured, equipment_status, 
                                equipment_model_number, equipment_kit_name, equipment_type, current_edit_id))
        
        
        conn.commit()
        
        # Show success message
        messagebox.showinfo("Success", "Equipment updated successfully")
        

        
        # Schedule the list refresh and reselection
        root.after(100, lambda: post_update_actions(selected_index))
        
        # Restore the selection using the saved index
        if selected_index:
            listbox.selection_set(selected_index)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()
        
    update_button.grid_remove()
    refresh_equipment_list()
    current_edit_id = None  # Reset the ID after updating
    
def post_update_actions(selected_index):
    refresh_equipment_list()
    
    # Reselect item in listbox
    if selected_index is not None:
        listbox.selection_set(selected_index)
        listbox.activate(selected_index)
        listbox.see(selected_index)  # Ensures the selected item is visible in the listbox
        
    # Focus on the root window after updating
    root.focus_set()

###
def add_equipment():
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        equipment_name = entry_name.get()
        equipment_brand = entry_brand.get()
        equipment_model = entry_model.get()
        equipment_model_number = entry_model_number.get()
        equipment_description = entry_description.get()
        equipment_sn = entry_sn.get()
        equipment_status = status_var.get()
        equipment_purchaseCompany = entry_purchaseCompany.get()
        equipment_purchaseDate = purchase_date_input.get_date()
        equipment_cost = entry_cost.get()
        equipment_url = entry_url.get()
        equipment_dateInsured = date_insured_input.get_date() if is_insured_var.get() else None
        equipment_kit_name = kit_name_dropdown.var.get()
        equipment_type = type_dropdown.var.get()
        
        query = """INSERT INTO equipment (name, brand, model, description, serial_number, 
                    purchase_company, date_of_purchase, cost, website_url, date_insured, status, model_number, kit_name, type) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (equipment_name, equipment_brand, equipment_model, equipment_description, equipment_sn, 
                                equipment_purchaseCompany, equipment_purchaseDate, equipment_cost, equipment_url, 
                                equipment_dateInsured, equipment_status, equipment_model_number, equipment_kit_name, equipment_type))
        conn.commit()
        messagebox.showinfo("Success", "Equipment added successfully")
        refresh_equipment_list()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()
    refresh_equipment_list()
    update_button.grid_remove()

###
def reset_fields():
    global current_edit_id
    type_dropdown.var.set("None")
    entry_name.delete(0, tk.END)
    entry_brand.delete(0, tk.END)
    entry_model.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    entry_sn.delete(0, tk.END)
    kit_name_dropdown.var.set("None")
    entry_purchaseCompany.delete(0, tk.END)
    entry_cost.delete(0, tk.END)
    entry_url.delete(0, tk.END)
    purchase_date_input.month_var.set(purchase_date_input.months[0])
    purchase_date_input.day_var.set('')
    purchase_date_input.year_var.set('')
    is_insured_var.set(False)
    toggle_insured()
    date_insured_input.month_var.set(date_insured_input.months[0])
    date_insured_input.day_var.set('')
    date_insured_input.year_var.set('')
    current_edit_id = None  # Exit update mode
    update_button.grid_remove()

def delete_equipment():
    response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this equipment?")
    if response:  # Proceed only if user confirms
        selected = listbox.get(listbox.curselection())
        equipment_id = selected.split(":")[0]
        conn = create_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Equipment deleted successfully")
            refresh_equipment_list()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"An error occurred: {err}")
        finally:
            cursor.close()
            conn.close()
    refresh_equipment_list()
    update_button.grid_remove()
    
def edit_equipment():
    global current_edit_id
    try:
        selected_id = listbox.get(listbox.curselection()).split(":")[0]
        current_edit_id = selected_id  # Store the ID for updating
        populate_fields_for_edit(selected_id)
        update_button.grid(row=left_frame_buttons_row, column=1, columnspan=2)
    except tk.TclError:
        messagebox.showerror("Error", "No equipment selected")
    
# UI Update Functions
def toggle_insured(): # Function to toggle the visibility of the date insured input
    if is_insured_var.get():
        label_dateInsured.grid(row=11, column=0)
        date_insured_input.month_menu.grid(row=11, column=1, columnspan=1)
        date_insured_input.day_entry.grid(row=11, column=2, columnspan=1)
        date_insured_input.year_entry.grid(row=11, column=3)
    else:
        label_dateInsured.grid_remove()
        date_insured_input.month_menu.grid_remove()
        date_insured_input.day_entry.grid_remove()
        date_insured_input.year_entry.grid_remove()
        
def refresh_equipment_list():
    listbox.delete(0, tk.END)  # Clear current list
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM equipment")
        for id, name in cursor:
            listbox.insert(tk.END, f"{id}: {name}")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()
    
def get_kit_names():
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT kit_name FROM equipment WHERE kit_name IS NOT NULL")
    kits = [row[0] for row in cursor]
    cursor.close()
    conn.close()
    return ["All Equipment"] + kits

# Detail Display Function
def display_details(selected_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    bold_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
    value_font = tkFont.Font(family="Helvetica", size=13)
    hyperlink_font = tkFont.Font(family="Helvetica", size=13, underline=True)
    
    try:
        cursor.execute("SELECT * FROM equipment WHERE id = %s", (selected_id,))
        row = cursor.fetchone()
        if row:
            for widget in details_frame.winfo_children():
                widget.destroy()
            url_index = get_column_index(cursor, 'website_url')
            for index, col in enumerate(row):
                col_name = cursor.description[index][0].replace('_', ' ').title()  # Replace underscores and capitalize words
                
                if col_name.lower() == 'website url':
                    continue  # Skip displaying the 'website_url' label and value
                
                row_frame = tk.Frame(details_frame)
                row_frame.pack(fill='x', expand=True)
                
                label = tk.Label(row_frame, text=f"{col_name}:", font=bold_font, anchor='w')
                label.pack(side='left')
                
                if col_name.lower() == 'name' and url_index is not None:
                    value = tk.Label(row_frame, text=str(col), font=hyperlink_font, cursor="hand2", anchor='w')
                    value.bind("<Button-1>", lambda e, url=row[url_index]: webbrowser.open(url))
                else:
                    value = tk.Label(row_frame, text=str(col) if col_name.lower() != 'kit name' else (col if col else 'None'), font=value_font, anchor='w')
                value.pack(side='left')
                    
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()
        
# Event Handlers
def on_select(evt):
    # Note here that Tkinter passes an event object to on_select()
    w = evt.widget
    if not w.curselection():  # Check if there's a selection
        return  # Exit the function if nothing is selected
    index = int(w.curselection()[0])
    value = w.get(index)
    selected_id = value.split(":")[0]
    selected_name = value.split(":")[1].strip()  # Get the name of the item
    display_image(selected_name)
    display_details(selected_id)
    
# Main Aplication Setup
root = tk.Tk()
root.title("USS Video Production Equipment Tracker")
initialize_fonts()

# Frame Set-Ups
left_frame_boarder = tk.Frame(root, borderwidth=.5, relief="solid", highlightbackground="white")
left_frame_boarder.grid(row=0, column=0, padx=10, pady=10, rowspan=2, sticky='n')

left_frame = tk.Frame(left_frame_boarder)
left_frame.pack(padx=10, pady=10)

right_frame_boarder = tk.Frame(root, borderwidth=.5, relief="solid")
right_frame_boarder.grid(row=0, column=1, padx=10, pady=10, rowspan=2, sticky='n')

right_frame = tk.Frame(right_frame_boarder)
right_frame.pack(padx=10, pady=10)

image_frame = tk.Frame(root, bg="white")
image_frame.grid(row=0, column=2, padx=10, pady=10, sticky='w')

details_frame = tk.Frame(root)
details_frame.grid(row=1, column=2, padx=10, pady=10, sticky='w')

# Left Frame - Input Form

### when a new input is added these functions must be modified: populate_fields_for_edit, reset_fields, add_equipment, update_equipment
label_type = tk.Label(left_frame, text="Type:")
label_type.grid(row=0, column=0, sticky='e')
type_dropdown = ColumnDropdown(left_frame, "type", create_db_connection(), row=0, column=1, button_label="New Type")

label_name = tk.Label(left_frame, text="Name:")
label_name.grid(row=1, column=0, sticky='e')
entry_name = tk.Entry(left_frame)
entry_name.grid(row=1, column=1, columnspan=3)  # Span across 3 columns

label_brand = tk.Label(left_frame, text="Brand:")
label_brand.grid(row=2, column=0, sticky='e')
entry_brand = tk.Entry(left_frame)
entry_brand.grid(row=2, column=1, columnspan=3)

label_model = tk.Label(left_frame, text="Model:")
label_model.grid(row=3, column=0, sticky='e')
entry_model = tk.Entry(left_frame)
entry_model.grid(row=3, column=1, columnspan=3)

label_model_number = tk.Label(left_frame, text="Model Number:")
label_model_number.grid(row=4, column=0, sticky='e')
entry_model_number = tk.Entry(left_frame)
entry_model_number.grid(row=4, column=1, columnspan=3)

label_description = tk.Label(left_frame, text="Description:")
label_description.grid(row=5, column=0, sticky='e')
entry_description = tk.Entry(left_frame)
entry_description.grid(row=5, column=1, columnspan=3)

label_sn = tk.Label(left_frame, text="Serial #:")
label_sn.grid(row=6, column=0, sticky='e')
entry_sn = tk.Entry(left_frame)
entry_sn.grid(row=6, column=1, columnspan=3)

label_status = tk.Label(left_frame, text="Status:")
label_status.grid(row=7, column=0, sticky='e')
status_var = tk.StringVar()
status_dropdown = tk.OptionMenu(left_frame, status_var, "In Office", "Checked Out", "Under Maintenance", "Retired")
status_dropdown.grid(row=7, column=1, columnspan=3, sticky="w")

label_kit_name = tk.Label(left_frame, text="Kit Name:")
label_kit_name.grid(row=8, column=0, sticky='e')
kit_name_dropdown = ColumnDropdown(left_frame, "kit_name", create_db_connection(), row=8, column=1, button_label="New Kit")

label_purchaseCompany = tk.Label(left_frame, text="Purchase Company:")
label_purchaseCompany.grid(row=9, column=0, sticky='e')
entry_purchaseCompany = tk.Entry(left_frame)
entry_purchaseCompany.grid(row=9, column=1, columnspan=3)

label_purchaseDate = tk.Label(left_frame, text="Purchase Date:")
label_purchaseDate.grid(row=10, column=0, sticky='e')
purchase_date_input = DateInput(left_frame, row=10, column=1)

label_cost = tk.Label(left_frame, text="Cost:")
label_cost.grid(row=11, column=0, sticky='e')
entry_cost = tk.Entry(left_frame)
entry_cost.grid(row=11, column=1, columnspan=3)

label_url = tk.Label(left_frame, text="URL:")
label_url.grid(row=12, column=0, sticky='e')
entry_url = tk.Entry(left_frame)
entry_url.grid(row=12, column=1, columnspan=3)

is_insured_var = tk.BooleanVar(value=False)
checkbox_insured = tk.Checkbutton(left_frame, text="Is Insured?", variable=is_insured_var, command=toggle_insured)
checkbox_insured.grid(row=13, column=0, columnspan=4)

label_dateInsured = tk.Label(left_frame, text="Date Insured:")
label_dateInsured.grid(row=14, column=0, sticky='e')
date_insured_input = DateInput(left_frame, row=14, column=1)
toggle_insured()  # Set initial visibility based on checkbox

left_frame_buttons_row = 15

# Left Frame - Buttons
update_button = tk.Button(left_frame, text="Update Equipment", command=update_equipment) # Update button (Initially hidden)

submit_button = tk.Button(left_frame, text="Add Equipment", command=add_equipment)
submit_button.grid(row=left_frame_buttons_row, column=0)

reset_button = tk.Button(left_frame, text="Reset Fields", command=reset_fields)
reset_button.grid(row=left_frame_buttons_row, column=3, columnspan=2)

# Right Frame - Equipment List and Delete Function
listbox = tk.Listbox(right_frame, width=50, height=40)
listbox.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
listbox.bind('<<ListboxSelect>>', on_select)
def update_listbox_by_kit(kit_name):
    listbox.delete(0, tk.END)  # Clear the current list
    conn = create_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, name FROM equipment"
    if kit_name != "All Equipment":
        query += " WHERE kit_name = %s"
        cursor.execute(query, (kit_name,))
    else:
        cursor.execute(query)
    for id, name in cursor:
        listbox.insert(tk.END, f"{id}: {name}")
    cursor.close()
    conn.close()
kit_var = tk.StringVar() # Dropdown for kit names
kit_var.set("All Equipment")  # default value
kit_dropdown = tk.OptionMenu(right_frame, kit_var, *get_kit_names(), command=update_listbox_by_kit)
kit_dropdown.grid(row=0, column=0, padx=10, pady=10, columnspan=2)  # place this above the listbox in your grid

update_listbox_by_kit("All Equipment")# Initial population of listbox


edit_button = tk.Button(right_frame, text="Edit Equipment", command=edit_equipment)
edit_button.grid(row=2, column=0)

delete_button = tk.Button(right_frame, text="Delete Equipment", command=delete_equipment)
delete_button.grid(row=2, column=1)

# Initial Refresh Function Call
refresh_equipment_list()  # Initial list population

# Main Loop Call
root.mainloop()
