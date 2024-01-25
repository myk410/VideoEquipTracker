# main_app.py
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from db import DatabaseManager
from db import host_ct, user_ct, passwd_ct, database_ct
from utils import initialize_fonts, display_image
from widgets import DateInput, ColumnDropdown
import webbrowser
import os
from fpdf import FPDF
import subprocess
import modules.connect as ct
from datetime import datetime
import re
import pandas as pd
from tkinter import ttk

def backup_table_to_sql(host, user, password, database, table, output_file):
    try:
        # Run mysqldump to create the SQL file
        command = f"mysqldump -h {host} -u {user} -p{password} {database} {table} > {output_file}"
        subprocess.run(command, shell=True, check=True)
        
        # Read the created SQL file
        with open(output_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            
        # Replace the collation
        updated_sql_content = re.sub(r'utf8mb4_0900_ai_ci', 'utf8mb4_general_ci', sql_content)
        
        # Write the modified content back to the file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(updated_sql_content)
            
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing mysqldump:", e)
        
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Production Equipment Tracker")
        self.heading_font, self.bold_font, self.value_font = initialize_fonts()
        self.db_manager = DatabaseManager()
        self.current_editing_id = None  # Add this line
        self.kit_names = ["All Kits"] + self.get_kit_names()
        self.types = ["All Types"] + self.get_unique_types()
        self.equipment_IDs = []
        self.selected_name_for_rename = None
        self.purchased_filter_var = tk.StringVar(value="Show Purchased")
    
        self.setup_frames()
        
        self.refresh_equipment_list()
        
    def format_label_text(self, index):
        # Example implementation - modify as per your requirements
        column_names = ["ID", "Name", "Brand", "Model", "Description", "Serial Number", "Status", "Kit Name", "Purchase Company", "Purchase Date", "Cost", "Website URL", "Date Insured", "Type"]
        if index < len(column_names):
            return column_names[index]
        else:
            return "Unknown Column"
    
    def get_kit_names(self):
        return sorted(self.db_manager.fetch_kit_names())
        
    def setup_frames(self):
        self.setup_left_frame()  # Create and grid left_frame first
        self.setup_middle_frame()
        self.setup_right_frame()
        
    def setup_left_frame(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky='n')
        self.setup_add_update_frame()  # Inside setup_left_frame
        self.setup_window_frame()      # Inside setup_left_frame
        
    def setup_right_frame(self):
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(column=2, row=0, padx=10, pady=10, sticky='n')
        self.setup_image_frame()  # Inside setup_right_frame
        self.setup_details_frame()  # Inside setup_right_frame
        self.right_frame.grid_remove()
        
    def setup_image_frame(self):
        self.image_frame = tk.Frame(self.right_frame, bg="white")
        self.image_frame.grid(column=0, row=0, padx=10, pady=10, sticky='n')
        
    def setup_details_frame(self):
        self.details_frame = tk.Frame(self.right_frame)
        self.details_frame.grid(column=0, row=1, padx=10, pady=10, sticky='n')
        self.details_canvas = tk.Canvas(self.details_frame, height=400, width=350)
        self.scrollbar = tk.Scrollbar(self.details_frame, orient="vertical", command=self.details_canvas.yview)
        self.container_frame = tk.Frame(self.details_canvas)
        
        self.details_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.details_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.details_canvas.create_window((0, 0), window=self.container_frame, anchor="nw")
        self.container_frame.bind("<Configure>", lambda event: self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all")))

    def setup_add_update_frame(self):
        self.add_update_frame = tk.Frame(self.left_frame, borderwidth=1, relief="solid")
        self.add_update_frame.grid(column=0, row=0, padx=10, pady=10, sticky='n')
        
        # Label for Equipment List
        tk.Label(self.add_update_frame, text="Add/Update Equpiment", font=self.heading_font).grid(column=0,row=0,columnspan=4, pady=10)

        au_input_frame = tk.Frame(self.add_update_frame)
        au_input_frame.grid(row=1,column=0, padx=20)
        
        # Row index for grid placement
        row = 0
        
        # Type Dropdown (Renamed to type_name_dropdown)
        tk.Label(au_input_frame, text="Type:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.type_name_dropdown = ColumnDropdown(au_input_frame, "type", self.db_manager, row=row, column=1)
        row += 1
        
        # Name Entry
        tk.Label(au_input_frame, text="Name:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_name = tk.Entry(au_input_frame)
        self.entry_name.grid(row=row, column=1)
        row += 1
        
        # Brand Entry
        tk.Label(au_input_frame, text="Brand:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_brand = tk.Entry(au_input_frame)
        self.entry_brand.grid(row=row, column=1)
        row += 1
        
        # Model Entry
        tk.Label(au_input_frame, text="Model:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_model = tk.Entry(au_input_frame)
        self.entry_model.grid(row=row, column=1)
        row += 1
        
        # Model Number Entry
        tk.Label(au_input_frame, text="Model Number:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_model_number = tk.Entry(au_input_frame)
        self.entry_model_number.grid(row=row, column=1)
        row += 1
        
        # Description Entry
        tk.Label(au_input_frame, text="Description:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_description = tk.Entry(au_input_frame)
        self.entry_description.grid(row=row, column=1)
        row += 1
        
        # Serial Number Entry
        tk.Label(au_input_frame, text="Serial #:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_sn = tk.Entry(au_input_frame)
        self.entry_sn.grid(row=row, column=1)
        row += 1
        
        # Weight Entry
        tk.Label(au_input_frame, text="Weight (lbs):", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_weight = tk.Entry(au_input_frame)
        self.entry_weight.grid(row=row, column=1)
        row += 1
        
        # Status Dropdown
        tk.Label(au_input_frame, text="Status:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        # Initialize the StringVar with a string of spaces of length 15
        self.status_var = tk.StringVar(value=' ' * 15)
        self.status_dropdown = tk.OptionMenu(au_input_frame, self.status_var, "In Office", "Checked Out", "Under Maintenance", "Retired")
        # Set the width of the dropdown menu to 15
        self.status_dropdown.config(width=15)
        self.status_dropdown.grid(row=row, column=1, sticky='w')
        row += 1
        
        # Kit Name Dropdown
        tk.Label(au_input_frame, text="Kit Name:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.kit_name_dropdown = ColumnDropdown(au_input_frame, "kit_name", self.db_manager, row=row, column=1)
        row += 1
        
        # Purchased
        tk.Label(au_input_frame, text="Not Purchased:", font=self.bold_font).grid(row=row,column=0, sticky='e')
        self.not_purchased_var = tk.BooleanVar()
        self.checkbox_not_purchased = tk.Checkbutton(au_input_frame, variable=self.not_purchased_var)
        self.checkbox_not_purchased.grid(row=row, column=1, sticky='w')  # Adjust 'next_row' to the correct row number
        row += 1
        
        # Purchase Company Entry
        tk.Label(au_input_frame, text="Purchase Company:", font=self.bold_font).grid(row=row,column=0, sticky='e')
        self.entry_purchaseCompany = tk.Entry(au_input_frame)
        self.entry_purchaseCompany.grid(row=row, column=1)
        row += 1
        
        # Purchase Date using DateInput Widget
        tk.Label(au_input_frame, text="Purchase Date:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.purchase_date_input = DateInput(au_input_frame, row=row, column=1)
        row += 1
    
        # Cost Entry
        tk.Label(au_input_frame, text="Cost:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_cost = tk.Entry(au_input_frame)
        self.entry_cost.grid(row=row, column=1)
        row += 1
    
        # URL Entry
        tk.Label(au_input_frame, text="URL:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_url = tk.Entry(au_input_frame)
        self.entry_url.grid(row=row, column=1)
        row += 1
    
        # Insurance Checkbox
        tk.Label(au_input_frame, text="Is Insured:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.is_insured_var = tk.BooleanVar(value=False)
        self.checkbox_insured = tk.Checkbutton(au_input_frame, variable=self.is_insured_var, command=self.toggle_insured)
        self.checkbox_insured.grid(row=row, column=1, sticky='w')
        row += 1
        
        # Date Insured Input
        self.label_date_insured = tk.Label(au_input_frame, text="Date Insured:", font=self.bold_font)
        self.label_date_insured.grid(row=row, column=0, sticky='e')
        self.label_date_insured.grid_remove()
        self.date_insured_input = DateInput(au_input_frame, row=row, column=1)
        # Initially hide the date insured input
        self.date_insured_input.month_menu.grid(row=row, column=1, sticky="e")
        self.date_insured_input.day_entry.grid(row=row, column=2, sticky="w")
        self.date_insured_input.year_entry.grid(row=row, column=3, sticky="w")
        self.date_insured_input.month_menu.grid_remove()
        self.date_insured_input.day_entry.grid_remove()
        self.date_insured_input.year_entry.grid_remove()
        row += 1
        
        # Owner Dropdown
        tk.Label(au_input_frame, text="Owner:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.owner_name_dropdown = tk.StringVar(value="None")
        self.owner_dropdown = tk.OptionMenu(au_input_frame, self.owner_name_dropdown, "Enue Studios", "US Sailing")
        self.owner_dropdown.grid(row=row, column=1, sticky='w')
        row += 1
        
        au_buttons_frame = tk.Frame(self.add_update_frame)
        au_buttons_frame.grid(row=2, column=0, padx=10, pady=10)
        
        # Buttons for Add, Update, Reset
        self.add_button = tk.Button(au_buttons_frame, text="Add Equipment", command=self.add_equipment)
        self.add_button.grid(row=0, column=0)
        self.update_button = tk.Button(au_buttons_frame, text="Update Equipment", command=self.update_equipment)
        self.update_button.grid(row=0, column=1)
        self.update_button.grid_remove()
        self.reset_button = tk.Button(au_buttons_frame, text="Reset Fields", command=self.reset_fields)
        self.reset_button.grid(row=0, column=2)
        
    def setup_middle_frame(self):
        self.middle_frame = tk.Frame(self, borderwidth=1, relief="solid")
        self.middle_frame.grid(column = 1, row = 0, rowspan=2, padx=10, pady=10, sticky='n')
        
        row = 0
        
        # Label for Equipment List
        tk.Label(self.middle_frame, text="Equipment List", font=self.heading_font).grid(column=0,row=row,columnspan=2, pady=10)
        row += 1 
        
        # Label for Filters
        tk.Label(self.middle_frame, text="Filters", font=self.bold_font).grid(column=0,row=row,columnspan=2, pady=5, padx=20, sticky='w')
        row += 1 
        
        mid_filter_frame = tk.Frame(self.middle_frame)
        mid_filter_frame.grid(column=0,row=row)
        row += 1 
        
        # Kit Name Dropdown
        self.kit_var = tk.StringVar(value=self.kit_names[0])
        self.kit_dropdown = tk.OptionMenu(mid_filter_frame, self.kit_var, *self.kit_names, command=lambda _: self.refresh_equipment_list())
        self.kit_dropdown.grid(column=0,row=1)
        
        # Type Dropdown
        self.type_var = tk.StringVar(value=self.types[0])
        self.type_dropdown = tk.OptionMenu(mid_filter_frame, self.type_var, *self.types, command=lambda _: self.refresh_equipment_list())
        self.type_dropdown.grid(column=1,row=1)
        
        self.owners = ["All Owners"] + self.db_manager.get_unique_owners()
        
        # Owner Dropdown
        self.owner_var = tk.StringVar(value=self.owners[0])
        self.owner_dropdown = tk.OptionMenu(mid_filter_frame, self.owner_var, *self.owners, command=lambda _: self.refresh_equipment_list())
        self.owner_dropdown.grid(column=2, row=1)
        
        # Purchased Filter Dropdown
        self.purchased_filter_options = ["Show All", "Show Purchased", "Show Not Purchased"]
        self.purchased_filter_dropdown = ttk.Combobox(mid_filter_frame, textvariable=self.purchased_filter_var, values=self.purchased_filter_options, state="readonly")
        self.purchased_filter_dropdown.grid(column=0, row=2, padx=10, pady=10, columnspan=3)
        self.purchased_filter_dropdown.bind("<<ComboboxSelected>>", lambda _: self.refresh_equipment_list())
        
        # Equipment Listbox
        self.equipment_listbox = tk.Listbox(self.middle_frame, font=self.value_font, width=50, height=50)
        self.equipment_listbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        self.equipment_listbox.bind('<<ListboxSelect>>', self.on_select)
        row += 1 
        
        mid_buttons_frame = tk.Frame(self.middle_frame)
        mid_buttons_frame.grid(row=row, column=0, padx=10, pady=10)
        row += 1 
        
        # Edit and Delete Buttons
        self.edit_button = tk.Button(mid_buttons_frame, text="Edit Equipment", command=self.edit_equipment)
        self.edit_button.grid(row=0, column=0, padx=20)
        
        self.delete_button = tk.Button(mid_buttons_frame, text="Delete Equipment", command=self.delete_equipment)
        self.delete_button.grid(row=0, column=1)
        
        # Initial Populate Listbox
        self.refresh_equipment_list()
        
    def setup_window_frame(self):
        self.window_frame = tk.Frame(self.left_frame)
        self.window_frame.grid(column=0, row=1, padx=10, pady=10)
        
        row=0
        
        self.shipping_button = tk.Button(self.window_frame, text="Shipping", command=self.open_shipping_window)
        self.shipping_button.grid(column=0, row=row, padx=10, pady=10)
        row += 1
        
        self.boxes_button = tk.Button(self.window_frame, text="Boxes", command=self.open_boxes_window)
        self.boxes_button.grid(column=1, row=0, padx=10, pady=10)
        
        self.rename_button = tk.Button(self.window_frame, text="Rename Equipment", command=self.open_rename_window)
        self.rename_button.grid(column=2, row=0, padx=10, pady=10)  # Adjust grid parameters as needed
        
        self.sql_button = tk.Button(self.window_frame, text="Export SQL File", command=self.save_sql_file)
        self.sql_button.grid(column=0, row=1, padx=10, pady=10)  # Adjust the grid parameters as needed
        
        self.export_excel_button = tk.Button(self.window_frame, text="Export to Excel", command=self.export_to_excel)
        self.export_excel_button.grid(column=1, row=1, padx=10, pady=10)  # Adjust the grid parameters as needed
        
        
    def open_boxes_window(self):
        self.boxes_window = tk.Toplevel(self)
        self.boxes_window.title("Box Management")
        
        # Create a Listbox for boxes
        self.boxes_listbox = tk.Listbox(self.boxes_window, width=50, height=15)
        self.boxes_listbox.grid(row=0, column=0, padx=10, pady=10)
        self.boxes_listbox.bind('<<ListboxSelect>>', self.on_box_select)
        
        self.box_listbox = tk.Listbox(self.boxes_window, width=50, height=15)
        self.box_listbox.grid(row=0, column=1, padx=10, pady=10)
        
        # PDF Button
        pdf_button = tk.Button(self.boxes_window, text="Generate PDF", command=self.generate_boxes_pdf)
        pdf_button.grid(row=2, column=1, padx=10, pady=10)  # Adjust grid parameters as needed
        
        # Populate the boxes listbox
        self.populate_boxes_listbox()
        
        # Label to display the total weight
        self.total_weight_label = tk.Label(self.boxes_window, text="Total Weight: 0 lbs")
        self.total_weight_label.grid(row=1, column=1, padx=10, pady=10)  # Adjust position as needed
        
        # Frame for displaying equipment items in the selected box
        self.box_items_frame = tk.Frame(self.boxes_window)
        self.box_items_frame.grid(row=1, column=0, padx=10, pady=10)
        
    def generate_boxes_pdf(self):
        directory = filedialog.askdirectory()
        if not directory:
            messagebox.showwarning("Warning", "No directory selected")
            return
        
        filename = f"{directory}/boxes_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = FPDF()
        pdf.add_page()
        
        # Fetch box data
        boxes = self.db_manager.get_boxes()  # Modify as per your method to fetch box data
        
        for box in boxes:
            box_id = box[0]
            items_in_box = self.db_manager.get_items_in_box(box_id)  # Fetch items in the box
            
            # Distinguish between individual items and kits
            kits_in_box = set()
            individual_items = set()
            for item in items_in_box:
                kit_name = item[2]  # Assuming kit_name is at index 17
                if kit_name and kit_name != "None":
                    kits_in_box.add(kit_name)
                else:
                    individual_items.add(item[0])  # Assuming item name is at index 0
                    
            # Writing to PDF
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 7, txt=f"Box {box_id}:", ln=True, align='L')
            total_weight = sum(item[1] for item in items_in_box if item[1] is not None and len(item) > 1)
            pdf.set_font("Arial", size=10)
            
            for kit_name in kits_in_box:
                pdf.cell(0, 5, txt=f"  - {kit_name} (Kit)", ln=True, align='L')
                
            for item_name in individual_items:
                pdf.cell(0, 5, txt=f"  - {item_name}", ln=True, align='L')
                
            pdf.set_font("Arial",'I', size=10)
            pdf.cell(0, 8, txt=f"Total Weight: {total_weight:.2f} lbs", ln=True, align='L')
                
            pdf.cell(0, 5, txt="", ln=True, align='L')
                
        pdf.output(name=filename, dest='F').encode('latin1')
        messagebox.showinfo("Success", f"PDF generated at {filename}")
        
    def open_rename_window(self):
        self.rename_window = tk.Toplevel(self)
        self.rename_window.title("Rename Equipment")
        
        # Listbox to display unique equipment names
        self.rename_listbox = tk.Listbox(self.rename_window, width=50, height=15)
        self.rename_listbox.grid(row=0, column=0, padx=10, pady=10)
        self.rename_listbox.bind('<<ListboxSelect>>', self.on_rename_listbox_select)
        
        # Populate the listbox with unique names sorted alphabetically
        unique_names = self.db_manager.get_unique_names()  # Method to be implemented in DatabaseManager
        for name in sorted(unique_names):
            self.rename_listbox.insert(tk.END, name)
            
        # Entry field for new name
        self.new_name_entry = tk.Entry(self.rename_window)
        self.new_name_entry.grid(row=1, column=0, padx=10, pady=10)
        
        # Button to execute renaming
        rename_button = tk.Button(self.rename_window, text="Rename", command=self.execute_rename)
        rename_button.grid(row=2, column=0, padx=10, pady=10)
        
    def on_rename_listbox_select(self, event):
        # Get the currently selected item
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            selected_name = event.widget.get(index)
            self.selected_name_for_rename = selected_name  # Store the selected name
            # Set the selected name in the entry field
            self.new_name_entry.delete(0, tk.END)
            self.new_name_entry.insert(0, selected_name)
            
    def execute_rename(self):
        old_name = self.selected_name_for_rename
        new_name = self.new_name_entry.get()
        
        if old_name and new_name and new_name != old_name:
            # Proceed with the renaming logic
            self.db_manager.update_equipment_name(old_name, new_name)
            self.rename_image_file(old_name, new_name)
            
            # Refresh the listboxes with updated names
            self.refresh_rename_listbox()
            self.refresh_equipment_list()  # Refresh the main equipment listbox
            
            # Reset the selected name for rename
            self.selected_name_for_rename = None
            
            messagebox.showinfo("Success", f"'{old_name}' has been renamed to '{new_name}'")
        else:
            messagebox.showerror("Input Error", "Invalid input. Please ensure the new name is different.")
            
    def refresh_rename_listbox(self):
        # Clear existing items
        self.rename_listbox.delete(0, tk.END)
        
        # Fetch updated unique names and repopulate the listbox
        unique_names = self.db_manager.get_unique_names()
        for name in sorted(unique_names):
            self.rename_listbox.insert(tk.END, name)
            
        # Clear the new name entry field
        self.new_name_entry.delete(0, tk.END)
                
    def rename_image_file(self, old_name, new_name):
        for ext in ['.png', '.jpg']:
            old_path = os.path.join('Pics', f'{old_name}{ext}')
            new_path = os.path.join('Pics', f'{new_name}{ext}')
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                break
                
    def populate_boxes_listbox(self):
        self.boxes_listbox.delete(0, tk.END)
        max_length = 0  # Variable to store the length of the longest item
        upper_limit = 30  # Upper limit for the width
        boxes = self.db_manager.get_boxes()  # Implement this method in your DatabaseManager
        for box in boxes:
            item_text = f"Box {box[0]}"
            max_length = max(max_length, len(item_text))
            self.boxes_listbox.insert(tk.END, item_text)
        self.boxes_listbox.config(width=min(max_length, upper_limit))
    
    def get_selected_box_id(self):
        try:
            selected = self.boxes_listbox.get(self.boxes_listbox.curselection())
            box_id = selected.split(" ")[1]  # Assuming the format is "Box <id>"
            return box_id
        except tk.TclError:
            messagebox.showerror("Error", "No box selected")
            return None
        
    
    def on_box_select(self, event):
        # Clear the box_listbox first
        self.box_listbox.delete(0, tk.END)
        
        box_id = self.get_selected_box_id()
        if not box_id:
            return  # Exit if no box is selected
        
        items = self.db_manager.get_items_in_box(box_id)
        
        # Assuming that each item is a tuple in the format (name, weight)
        total_weight = round(sum(item[1] for item in items if item[1] is not None), 2)
        
        # Update total weight label
        self.total_weight_label.config(text=f"Total Weight: {total_weight} lbs")
        
        # Populate box_listbox with items
        for item in items:
            item_text = f"{item[0]} - {item[1]} lbs"  # item[0] is name, item[1] is weight
            self.box_listbox.insert(tk.END, item_text)
            
    def delete_equipment(self):
        selected_id = self.get_selected_equipment_id()
        if selected_id:
            response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this equipment?")
            if response:
                self.db_manager.delete_equipment(selected_id)
                messagebox.showinfo("Success", "Equipment deleted successfully")
                self.refresh_equipment_list()
            
    def toggle_insured(self):
        if self.is_insured_var.get():
            self.label_date_insured.grid()
            self.date_insured_input.month_menu.grid()
            self.date_insured_input.day_entry.grid()
            self.date_insured_input.year_entry.grid()
        else:
            self.label_date_insured.grid_remove()
            self.date_insured_input.month_menu.grid_remove()
            self.date_insured_input.day_entry.grid_remove()
            self.date_insured_input.year_entry.grid_remove()
    
    def get_unique_kit_names(self):
        query = "SELECT DISTINCT kit_name FROM equipment WHERE kit_name IS NOT NULL"
        return [item[0] for item in self.fetch_data(query)]
    
    def get_unique_types(self):
        query = "SELECT DISTINCT type FROM equipment WHERE type IS NOT NULL"
        return sorted([item[0] for item in self.db_manager.fetch_data(query)])
    
    def refresh_dropdowns(self):
        # Refresh Kit Names
        self.kit_names = ["All Kits"] + self.get_kit_names()
        self.update_option_menu(self.kit_dropdown, self.kit_var, self.kit_names)
        
        # Refresh Types
        unique_types = self.get_unique_types()
        if "All Types" not in unique_types:
            unique_types.insert(0, "All Types")
        self.types = unique_types
        self.update_option_menu(self.type_dropdown, self.type_var, self.types)
        
        # Refresh Owners
        self.owners = ["All Owners"] + self.get_unique_owners()
        self.update_option_menu(self.owner_dropdown, self.owner_var, self.owners)
        
    def update_option_menu(self, dropdown, variable, options):
        menu = dropdown["menu"]
        menu.delete(0, "end")
        for option in options:
            menu.add_command(label=option, command=lambda value=option: variable.set(value))
        variable.set(options[0])

    def add_equipment(self):
        # Collect data from UI elements
        equipment_data = {
            'name': self.entry_name.get(),
            'brand': self.entry_brand.get(),
            'model': self.entry_model.get(),
            'model_number': self.entry_model_number.get(),
            'description': self.entry_description.get(),
            'serial_number': self.entry_sn.get(),
            'weight': self.entry_weight.get(),
            'status': self.status_var.get(),
            'kit_name': self.kit_name_dropdown.var.get(),
            'purchase_company': self.entry_purchaseCompany.get(),
            'date_of_purchase': self.purchase_date_input.get_date(),
            'cost': self.entry_cost.get(),
            'website_url': self.entry_url.get(),
            'date_insured': self.date_insured_input.get_date() if self.is_insured_var.get() else None,
            'type': self.type_name_dropdown.var.get(),
            'owner': self.owner_name_dropdown.get(),
            'not_purchased': self.not_purchased_var.get()
            
        }
        
        # Validate 'type' and 'owner' to ensure they are not set to 'All Types' or 'All Owners'
        if equipment_data['type'] == 'All Types' or equipment_data['owner'] == 'All Owners':
            messagebox.showerror("Invalid Selection", "Please select a valid type and owner.")
            return
        
        # Validate and convert 'cost' field
        try:
            equipment_data['cost'] = float(equipment_data['cost']) if equipment_data['cost'] else 0.0
        except ValueError:
            messagebox.showerror("Input Error", "Invalid cost value. Please enter a valid number.")
            return  # Stop the execution if the cost value is invalid
        
        # Call DatabaseManager method to add equipment
        self.db_manager.add_or_update_equipment(equipment_data, is_update=False)
        self.refresh_equipment_list()
        
        # Show confirmation popup
        messagebox.showinfo("Success", "Equipment added successfully")

    def edit_equipment(self):
        selected_id = self.get_selected_equipment_id()
        if selected_id:
            self.current_editing_id = selected_id
            self.populate_fields_for_edit(selected_id)
            self.update_button.grid()
            
    def populate_fields_for_edit(self, equipment_id):
        equipment_details = self.db_manager.get_equipment_details(equipment_id)
        if not equipment_details:
            print("Error: Equipment details not found.")
            return
        
        equipment_tuple = equipment_details[0]
        
        # Check if equipment_tuple has enough elements
        if len(equipment_tuple) < 29:  # Adjust the number based on your data structure
            print("Error: Equipment tuple does not have enough elements.")
            return
    
        # Clear existing content in the fields
        self.entry_name.delete(0, tk.END)
        self.entry_brand.delete(0, tk.END)
        self.entry_model.delete(0, tk.END)
        self.entry_model_number.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_sn.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.entry_purchaseCompany.delete(0, tk.END)
        self.entry_cost.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
    
        # Populate the fields with the equipment details
        self.entry_name.insert(0, equipment_tuple[1])  # Name
        self.entry_brand.insert(0, equipment_tuple[3])  # Brand
        model_value = str(equipment_tuple[4]) if equipment_tuple[4] is not None else ""
        self.entry_model.insert(0, model_value)
        model_number = equipment_tuple[16] if equipment_tuple[16] else ''
        self.entry_model_number.delete(0, tk.END)
        self.entry_model_number.insert(0, model_number)  # Model Number
        self.entry_description.insert(0, equipment_tuple[14])  # Description
        serial_number_value = str(equipment_tuple[5]) if equipment_tuple[5] is not None else ""
        self.entry_sn.insert(0, serial_number_value)
        self.entry_weight.insert(0, str(equipment_tuple[28]))
        self.status_var.set(equipment_tuple[11])  # Status
        purchase_company_value = str(equipment_tuple[6]) if equipment_tuple[6] is not None else ""
        self.entry_purchaseCompany.insert(0, purchase_company_value)
        if equipment_tuple[7]:  # Checking if the date_of_purchase is not None
            self.purchase_date_input.set_date(equipment_tuple[7])
        else:
            self.purchase_date_input.reset()  # Reset or clear the date fields if no date is present
            
        self.entry_cost.insert(0, str(equipment_tuple[8]))  # Cost
        self.entry_url.insert(0, equipment_tuple[15])  # URL
        
        # Populate the not_purchased checkbox
        not_purchased_index = 30
        self.not_purchased_var.set(equipment_tuple[not_purchased_index])
    
        # Handling insured date (if applicable)
        if equipment_tuple[9]:  # Date Insured
            self.is_insured_var.set(True)
            self.date_insured_input.set_date(equipment_tuple[9])
        else:
            self.is_insured_var.set(False)
            
        # Type Dropdown (Use type_name_dropdown)
        self.type_name_dropdown.var.set(equipment_tuple[2])  # Type
    
        # Toggle insured date visibility
        self.toggle_insured()
        
        # Update the Kit Name Dropdown
        kit_name_index = 17  # Update this index based on your database structure
        kit_name = equipment_tuple[kit_name_index]
        if isinstance(kit_name, tuple) and len(kit_name) > 0:
            kit_name = kit_name[0]
        self.kit_name_dropdown.var.set(kit_name)
        
        self.owner_name_dropdown.set(equipment_tuple[29])
    
        # Show update button, hide add button
        self.update_button.grid()
    
    def update_equipment(self):
        if self.current_editing_id is None:
            messagebox.showerror("Error", "No equipment selected for editing")
            return
        # Collecting data from UI elements
        updated_data = {
            'name': self.entry_name.get(),
            'brand': self.entry_brand.get(),
            'model': self.entry_model.get(),
            'model_number': self.entry_model_number.get(),
            'description': self.entry_description.get(),
            'serial_number': self.entry_sn.get(),
            'weight': self.entry_weight.get(),
            'status': self.status_var.get(),
            'kit_name': self.kit_name_dropdown.var.get(),
            'purchase_company': self.entry_purchaseCompany.get(),
            'date_of_purchase': self.purchase_date_input.get_date(),
            'cost': self.entry_cost.get(),
            'website_url': self.entry_url.get(),
            'date_insured': self.date_insured_input.get_date() if self.is_insured_var.get() else None,
            'type': self.type_name_dropdown.var.get(),
            'owner': self.owner_name_dropdown.get(),
            'not_purchased': self.not_purchased_var.get()
        }
        
        # Update equipment
        self.db_manager.add_or_update_equipment(updated_data, is_update=True, equipment_id=self.current_editing_id)
        
        # Refresh the equipment list
        self.refresh_equipment_list()
        
        # Find and select the updated equipment in the listbox
        for index, item in enumerate(self.equipment_listbox.get(0, tk.END)):
            selected = self.equipment_IDs[index]
            if int(selected) == self.current_editing_id:
                self.equipment_listbox.selection_set(index)
                self.equipment_listbox.see(index)
                self.equipment_listbox.activate(index)  # This line activates the selection
                break
            
        # Reset the editing ID
        self.current_editing_id = None
        
        self.update_button.grid_remove()
        
        # Show confirmation popup
        messagebox.showinfo("Success", "Equipment updated successfully")
    
    def get_selected_equipment_id(self):
        try:
            selected = self.equipment_IDs[self.equipment_listbox.curselection()[0]]
            return int(selected)  # Ensure it's an integer
        except tk.TclError:
            messagebox.showerror("Error", "No equipment selected")
            return None
            
    def refresh_equipment_list(self):
        self.equipment_listbox.delete(0, tk.END)  # Clear existing items in the listbox
        
        selected_kit_name = self.kit_var.get()
        selected_type = self.type_var.get()
        selected_owner = self.owner_var.get()
        selected_purchased_filter = self.purchased_filter_var.get()  # Get the selected value from the dropdown
        
        # Adjust the query based on the selected filters
        query = "SELECT id, name FROM equipment"
        conditions = []
        params = []
        
        if selected_kit_name != "All Kits":
            conditions.append("kit_name = %s")
            params.append(selected_kit_name)
        if selected_type != "All Types":
            conditions.append("type = %s")
            params.append(selected_type)
        if selected_owner != "All Owners":
            conditions.append("owner = %s")
            params.append(selected_owner)
            
        # Adjusting the query based on the purchased filter
        if selected_purchased_filter == "Show Purchased":
            conditions.append("not_purchased = FALSE")
        elif selected_purchased_filter == "Show Not Purchased":
            conditions.append("not_purchased = TRUE")
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY name"  # Add this line to sort by name
        
        self.equipment_IDs = []
        equipment_list = self.db_manager.fetch_data(query, tuple(params))
        for equipment in equipment_list:
            display_text = f"{equipment[1]}"
            self.equipment_IDs.append(f"{equipment[0]}")
            self.equipment_listbox.insert(tk.END, display_text)
            
    def on_select(self, event):
        if not self.equipment_listbox.curselection():
            return
        
        selected_index = self.equipment_listbox.curselection()[0]

        selected_id = self.equipment_IDs[selected_index]
        
        equipment_details = self.db_manager.get_equipment_details(selected_id)
        if not equipment_details or len(equipment_details) == 0:
            print("Error: No data found for equipment")
            return
        
        # Access the first tuple from the list (since it's a list of tuples)
        equipment_tuple = equipment_details[0]
        if len(equipment_tuple) < 2:
            print("Error: Insufficient data in equipment tuple")
            return
        
        # Now use equipment_tuple for further processing
        # self.populate_fields_for_edit(equipment_tuple)
        self.right_frame.grid()
        display_image(self.image_frame, equipment_tuple[1])  # Assuming the name is at index 1
        self.display_details(selected_id)
    
    def update_image(self, item_name):
        display_image(self.image_frame, item_name)
        
    def display_details(self, equipment_id):
        for widget in self.container_frame.winfo_children():
            widget.destroy()
            
        equipment_details = self.db_manager.get_equipment_details(equipment_id)
        if equipment_details:
            equipment_tuple = equipment_details[0]
            
            column_names = [
                "ID", "Name", "Type", "Brand", "Model", "Serial Number",
                "Purchase Company", "Date of Purchase", "Cost", "Date Insured",
                "Storage Location", "Status", "Current Holder", "Current Condition",
                "Description", "Website URL", "Model Number", "Kit Name", "Carrier",
                "Tracking Number", "Shipping Address", "Shipping City",
                "Shipping State", "Shipping ZIP", "Shipped Date",
                "Box Number", "Destination Name", "Shipping Status", "Weight",
                "Owner", "Not Purchased"
            ]
            
            for index, (col_name, detail) in enumerate(zip(column_names, equipment_tuple)):
                
                
                label = tk.Label(self.container_frame, text=col_name + ":", font=self.bold_font)
                label.grid(row=index, column=0, sticky="w")
                
                if col_name == "Not Purchased":
                    detail = "Yes" if detail else "No"  # Assuming detail is a boolean
                    
                if col_name == "Website URL" and detail:
                    hyperlink = tk.Label(self.container_frame, text=detail, fg="blue", cursor="hand2")
                    hyperlink.grid(row=index, column=1, sticky="w")
                    hyperlink.bind("<Button-1>", lambda e, url=detail: webbrowser.open(url) if url else None)
                else:
                    value_label = tk.Label(self.container_frame, text=str(detail), font=self.value_font)
                    value_label.grid(row=index, column=1, sticky="w")
                    
    def create_scrollable_frame(self, parent, row, column, rowspan, columnspan):
        # Create a frame to contain the Canvas and Scrollbar
        frame_container = tk.Frame(parent)
        frame_container.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        
        canvas = tk.Canvas(frame_container)
        scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return scrollable_frame
    
    def export_to_excel(self):
        data = self.db_manager.fetch_all_equipment()
        df = pd.DataFrame(data, columns=["Name", "Brand", "Model", "Model Number", "Serial Number", "Purchase Company", "Date of Purchase", "Cost", "Owner", "Website URL"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")

    def open_shipping_window(self):
        self.shipping_window = tk.Toplevel(self)
        self.shipping_window.title("Shipping Information")
        
        input_frame = tk.Frame(self.shipping_window)
        input_frame.grid(column=0,row=0, padx=20, pady=10, sticky='ns')
        items_frame = tk.Frame(self.shipping_window)
        items_frame.grid(column=1,row=0, padx=20, pady=10, sticky='ns')
        buttons_frame = tk.Frame(self.shipping_window)
        buttons_frame.grid(column=0,row=1,columnspan=2,pady=5)
        
        # Initialize row index for grid placement
        row = 0
        
        # BooleanVars for tracking checkbox states
        self.update_carrier = tk.BooleanVar(value=False)
        self.update_tracking_number = tk.BooleanVar(value=False)
        self.update_shipping_address = tk.BooleanVar(value=False)
        self.update_city = tk.BooleanVar(value=False)
        self.update_state = tk.BooleanVar(value=False)
        self.update_zip = tk.BooleanVar(value=False)
        self.update_shipping_date = tk.BooleanVar(value=False)
        self.update_box = tk.BooleanVar(value=False)
        self.update_destination = tk.BooleanVar(value=False)
        self.update_shipping_status = tk.BooleanVar(value=False)
        
        # Carrier Input with Checkbox
        self.carrier_checkbox = tk.Checkbutton(input_frame, variable=self.update_carrier)
        self.carrier_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Carrier:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_carrier = tk.Entry(input_frame)
        self.entry_carrier.grid(row=row, column=2)
        row += 1
        
        # Tracking Number Input with Checkbox
        self.tracking_number_checkbox = tk.Checkbutton(input_frame, variable=self.update_tracking_number)
        self.tracking_number_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Tracking Number:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_tracking_number = tk.Entry(input_frame)
        self.entry_tracking_number.grid(row=row, column=2)
        row += 1
        
        # Shipping Address Input with Checkbox
        self.shipping_address_checkbox = tk.Checkbutton(input_frame, variable=self.update_shipping_address)
        self.shipping_address_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Shipping Address:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_address = tk.Entry(input_frame)
        self.entry_shipping_address.grid(row=row, column=2)
        row += 1
        
        # City Input with Checkbox
        self.city_checkbox = tk.Checkbutton(input_frame, variable=self.update_city)
        self.city_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="City:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_city = tk.Entry(input_frame)
        self.entry_shipping_city.grid(row=row, column=2)
        row += 1
        
        # State Input with Checkbox
        self.state_checkbox = tk.Checkbutton(input_frame, variable=self.update_state)
        self.state_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="State:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_state = tk.Entry(input_frame)
        self.entry_shipping_state.grid(row=row, column=2)
        row += 1
        
        # ZIP Code Input with Checkbox
        self.zip_checkbox = tk.Checkbutton(input_frame, variable=self.update_zip)
        self.zip_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="ZIP Code:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_zip = tk.Entry(input_frame)
        self.entry_shipping_zip.grid(row=row, column=2)
        row += 1
        
        # Shipped Date Input with Checkbox
        self.shipped_date_checkbox = tk.Checkbutton(input_frame, variable=self.update_shipping_date)
        self.shipped_date_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Shipped Date:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.shipped_date_input = DateInput(input_frame, row=row, column=2)
        row += 1
        
        # Box Number Input with Checkbox
        self.box_checkbox = tk.Checkbutton(input_frame, variable=self.update_box)
        self.box_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Box Number:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_box_number = tk.Entry(input_frame)
        self.entry_box_number.grid(row=row, column=2)
        row += 1
        
        # Destination Name Input with Checkbox
        self.destination_checkbox = tk.Checkbutton(input_frame, variable=self.update_destination)
        self.destination_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Destination Name:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_destination_name = tk.Entry(input_frame)
        self.entry_destination_name.grid(row=row, column=2)
        row += 1
        
        # Shipping Status Input with Checkbox
        self.shipping_status_checkbox = tk.Checkbutton(input_frame, variable=self.update_shipping_status)
        self.shipping_status_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(input_frame, text="Shipping Status:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_status = tk.Entry(input_frame)
        self.entry_shipping_status.grid(row=row, column=2)
        row += 1
        
        # Button to set all shipping information to null
        set_null_button = tk.Button(input_frame, text="Reset Shipping Info", command=self.set_shipping_info_to_null)
        set_null_button.grid(column=0, row=row, columnspan=3, padx=10, pady=10, sticky='w')
        
        
        row = 0
        
        # Button to apply shipping details
        apply_button = tk.Button(buttons_frame, text="Apply Shipping Info", command=self.apply_shipping_info)
        apply_button.grid(column=1, columnspan=2, row=row, pady=10, sticky='nsew')
        
        row = 0
        
        # View mode radio buttons for selecting individual items or kits
        self.view_mode = tk.IntVar(value=0)  # 0 for individual items, 1 for kits
        tk.Radiobutton(items_frame, text="Individual Items", variable=self.view_mode, value=0, command=self.populate_shipping_listbox).grid(row=row, column=0, padx=10, pady=10)
        tk.Radiobutton(items_frame, text="Kits", variable=self.view_mode, value=1, command=self.populate_shipping_listbox).grid(row=row, column=1, padx=10, pady=10)
        row += 1

        # Button to select all checkboxes
        select_all_button = tk.Button(items_frame, text="Select All", command=self.select_all_shipping_items)
        select_all_button.grid(column=0, row=row, padx=10, pady=10, columnspan=2)
        row += 1
    
        # Create a Listbox to display equipment or kits
        #self.shipping_listbox = tk.Listbox(self.shipping_window, width=50, height=15)
        #self.shipping_listbox.grid(column=3, row=row, columnspan=2, padx=10, pady=10)
    
        # Create scrollable frame for checkboxes
        self.checkbox_frame = self.create_scrollable_frame(items_frame, row, 0, row, 2)
        self.checkbox_vars = {}
    
        # Populate the Listbox with checkboxes
        self.populate_shipping_listbox()
        
    def set_shipping_info_to_null(self):
        # Define the fields to set to null
        fields_to_nullify = ['carrier', 'tracking_number', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipped_date', 'box_number', 'shipping_destination_name', 'shipping_status']
        
        # Construct the nullify query
        query_parts = [f"{field} = NULL" for field in fields_to_nullify]
        update_query = "UPDATE equipment SET " + ", ".join(query_parts) + " WHERE id = %s"
        
        # Apply to individual items or kits based on view mode
        if self.view_mode.get() == 0:
            selected_item_ids = [item_id for (item_name, item_id), value in self.checkbox_vars.items() if value.get() == 1]
            for equipment_id in selected_item_ids:
                self.db_manager.execute_query(update_query, (equipment_id,))
        else:
            selected_kits = [kit_name for kit_name, value in self.checkbox_vars.items() if value.get() == 1]
            for kit in selected_kits:
                equipment_ids = self.fetch_equipment_ids_by_kit(kit)
                for equipment_id in equipment_ids:
                    self.db_manager.execute_query(update_query, (equipment_id,))
                    
        messagebox.showinfo("Success", "Shipping info set to null successfully")
        
    def select_all_shipping_items(self):
        for var in self.checkbox_vars.values():
            var.set(1)  # Set each checkbox variable to checked
        
    def populate_shipping_listbox(self):
        # Clear existing checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
            
        self.checkbox_vars.clear()
        
        if self.view_mode.get() == 0:
            # Populate with individual items, sorted by name
            equipment_list = self.db_manager.get_equipment_list()
            sorted_equipment_list = sorted(equipment_list, key=lambda item: item[1])  # Sort by name (item[1])
            for id, name in sorted_equipment_list:
                var = tk.IntVar()
                checkbox = tk.Checkbutton(self.checkbox_frame, text=name, variable=var)
                checkbox.pack(anchor='w')
                self.checkbox_vars[(name, id)] = var
        else:
            # Populate with kits, sorted alphabetically
            kit_list = self.db_manager.fetch_kit_names()
            sorted_kit_list = sorted(kit_list)  # Sort kits alphabetically
            for kit_name in sorted_kit_list:
                var = tk.IntVar()
                checkbox = tk.Checkbutton(self.checkbox_frame, text=kit_name, variable=var)
                checkbox.pack(anchor='w')
                self.checkbox_vars[kit_name] = var
                
    def apply_shipping_info(self):
        shipping_info = self.collect_shipping_info()
        
        if not shipping_info:
            messagebox.showwarning("No Selection", "No fields selected for update.")
            return
        
        # For individual items
        if self.view_mode.get() == 0:
            selected_item_ids = [item_id for (item_name, item_id), value in self.checkbox_vars.items() if value.get() == 1]
            for equipment_id in selected_item_ids:
                self.db_manager.update_shipping_info(equipment_id, shipping_info)
                
        # For kits
        else:
            selected_kits = [kit_name for kit_name, value in self.checkbox_vars.items() if value.get() == 1]
            for kit in selected_kits:
                equipment_ids = self.fetch_equipment_ids_by_kit(kit)
                for equipment_id in equipment_ids:
                    self.db_manager.update_shipping_info(equipment_id, shipping_info)
                    
        messagebox.showinfo("Success", "Shipping info updated successfully")
                
    def collect_shipping_info(self):
        # Collect the shipping information based on the selected checkboxes
        shipping_info = {}
        if self.update_carrier.get():
            shipping_info['carrier'] = self.entry_carrier.get()
        if self.update_tracking_number.get():
            shipping_info['tracking_number'] = self.entry_tracking_number.get()
        if self.update_shipping_address.get():
            shipping_info['shipping_address'] = self.entry_shipping_address.get()
        if self.update_city.get():
            shipping_info['shipping_city'] = self.entry_shipping_city.get()
        if self.update_state.get():
            shipping_info['shipping_state'] = self.entry_shipping_state.get()
        if self.update_zip.get():
            shipping_info['shipping_zip'] = self.entry_shipping_zip.get()
        if self.update_shipping_date.get():
            shipping_info['shipped_date'] = self.shipped_date_input.get_date()
        if self.update_box.get():
            shipping_info['box_number'] = self.entry_box_number.get()
        if self.update_destination.get():
            shipping_info['shipping_destination_name'] = self.entry_destination_name.get()
        if self.update_shipping_status.get():
            shipping_info['shipping_status'] = self.entry_shipping_status.get()
        return shipping_info
    
    def fetch_equipment_ids_by_kit(self, kit_name):
        # Fetch all equipment IDs belonging to a specific kit
        query = "SELECT id FROM equipment WHERE kit_name = %s"
        return [row[0] for row in self.db_manager.fetch_data(query, (kit_name,))]
        
    def save_sql_file(self):
        directory = filedialog.askdirectory()
        if directory:
            output_file = f"{directory}/equipment_backup.sql"  # Specify filename
            backup_table_to_sql(host_ct, user_ct, passwd_ct, database_ct, 'equipment', output_file)
            tk.messagebox.showinfo("Success", f"SQL file saved to {output_file}")
        else:
            tk.messagebox.showwarning("No Directory", "No directory was selected.")
                        
    def reset_fields(self):
        # Clearing text entries
        self.entry_name.delete(0, tk.END)
        self.entry_brand.delete(0, tk.END)
        self.entry_model.delete(0, tk.END)
        self.entry_model_number.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_sn.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.entry_purchaseCompany.delete(0, tk.END)
        self.entry_cost.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
        
        # Resetting dropdowns to default/initial values
        self.status_var.set("In Office")  # Assuming "In Office" is a default value
        self.kit_name_dropdown.reset_to_default()
        
        # Resetting date inputs
        self.purchase_date_input.reset()  # Assuming you have a reset method in DateInput class
        self.date_insured_input.reset()
        
        # Unchecking and hiding the insured checkbox and related fields
        self.is_insured_var.set(False)
        self.toggle_insured()
        
        # Reset type_dropdown
        default_type = "All Types"  # Replace with your actual default value
        self.type_var.set(default_type)
        
        self.owner_var.set("All Owners")  # Reset the owner dropdown
        
        
        
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
    
