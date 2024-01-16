# main_app.py
import tkinter as tk
from tkinter import messagebox
from db import DatabaseManager
from utils import initialize_fonts, display_image
from widgets import DateInput, ColumnDropdown

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USS Video Production Equipment Tracker")
        self.bold_font, self.value_font = initialize_fonts()
        self.db_manager = DatabaseManager()
    
        self.kit_names = ["All Kits"] + self.get_kit_names()
        self.types = ["All Types"] + self.db_manager.get_unique_types()
    
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
        return self.db_manager.fetch_kit_names()
        
    def setup_frames(self):
        self.setup_left_frame()
        self.setup_right_frame()
        self.setup_shipping_frame()
        self.setup_image_frame()
        self.setup_details_frame()
        
    def setup_shipping_frame(self):
        self.shipping_frame = tk.Frame(self, borderwidth=1, relief="solid")
        self.shipping_frame.grid(column=0, row=1, padx=10, pady=10)
        
        # Initialize row index for grid placement
        row = 0
        
        # Carrier Input
        tk.Label(self.shipping_frame, text="Carrier:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_carrier = tk.Entry(self.shipping_frame)
        self.entry_carrier.grid(row=row, column=1)
        row += 1
        
        # Tracking Number Input
        tk.Label(self.shipping_frame, text="Tracking Number:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_tracking_number = tk.Entry(self.shipping_frame)
        self.entry_tracking_number.grid(row=row, column=1)
        row += 1
        
        # Shipping Address Input
        tk.Label(self.shipping_frame, text="Shipping Address:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_shipping_address = tk.Entry(self.shipping_frame)
        self.entry_shipping_address.grid(row=row, column=1)
        row += 1
        
        # City Input
        tk.Label(self.shipping_frame, text="City:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_shipping_city = tk.Entry(self.shipping_frame)
        self.entry_shipping_city.grid(row=row, column=1)
        row += 1
        
        # State Input
        tk.Label(self.shipping_frame, text="State:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_shipping_state = tk.Entry(self.shipping_frame)
        self.entry_shipping_state.grid(row=row, column=1)
        row += 1
        
        # ZIP Code Input
        tk.Label(self.shipping_frame, text="ZIP Code:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_shipping_zip = tk.Entry(self.shipping_frame)
        self.entry_shipping_zip.grid(row=row, column=1)
        row += 1
        
        # Shipped Date Input using DateInput Widget
        tk.Label(self.shipping_frame, text="Shipped Date:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.shipped_date_input = DateInput(self.shipping_frame, row=row, column=1)
        row += 1
        
        # Box Number Input
        tk.Label(self.shipping_frame, text="Box Number:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_box_number = tk.Entry(self.shipping_frame)
        self.entry_box_number.grid(row=row, column=1)
        row += 1
        
        # Destination Name Input
        tk.Label(self.shipping_frame, text="Destination Name:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_destination_name = tk.Entry(self.shipping_frame)
        self.entry_destination_name.grid(row=row, column=1)
        row += 1
        
        # Shipping Status Input
        tk.Label(self.shipping_frame, text="Shipping Status:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_shipping_status = tk.Entry(self.shipping_frame)
        self.entry_shipping_status.grid(row=row, column=1)
        row += 1
        
    def setup_image_frame(self):
        self.image_frame = tk.Frame(self, bg="white")
        self.image_frame.grid(column = 2, row=0, padx=10, pady=10)
        # Initially, the image frame will be empty
        
    def setup_details_frame(self):
        self.details_frame = tk.Frame(self)
        self.details_frame.grid(column=2, row=1, padx=10, pady=10)
        self.details_canvas = tk.Canvas(self.details_frame)
        self.scrollbar = tk.Scrollbar(self.details_frame, orient="vertical", command=self.details_canvas.yview)
        self.container_frame = tk.Frame(self.details_canvas)
        
        self.details_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.details_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.details_canvas.create_window((0, 0), window=self.container_frame, anchor="nw")
        self.container_frame.bind("<Configure>", lambda event: self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all")))

    def setup_left_frame(self):
        self.left_frame = tk.Frame(self, borderwidth=1, relief="solid")
        self.left_frame.grid(column=0, row=0, padx=10, pady=10)
        
        # Row index for grid placement
        row = 0
        
        # Type Dropdown (Renamed to type_name_dropdown)
        tk.Label(self.left_frame, text="Type:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.type_name_dropdown = ColumnDropdown(self.left_frame, "type", self.db_manager, row=row, column=1)
        row += 1
        
        # Name Entry
        tk.Label(self.left_frame, text="Name:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_name = tk.Entry(self.left_frame)
        self.entry_name.grid(row=row, column=1)
        row += 1
        
        # Brand Entry
        tk.Label(self.left_frame, text="Brand:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_brand = tk.Entry(self.left_frame)
        self.entry_brand.grid(row=row, column=1)
        row += 1
        
        # Model Entry
        tk.Label(self.left_frame, text="Model:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_model = tk.Entry(self.left_frame)
        self.entry_model.grid(row=row, column=1)
        row += 1
        
        # Model Number Entry
        tk.Label(self.left_frame, text="Model Number:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_model_number = tk.Entry(self.left_frame)
        self.entry_model_number.grid(row=row, column=1)
        row += 1
        
        # Description Entry
        tk.Label(self.left_frame, text="Description:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_description = tk.Entry(self.left_frame)
        self.entry_description.grid(row=row, column=1)
        row += 1
        
        # Serial Number Entry
        tk.Label(self.left_frame, text="Serial #:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_sn = tk.Entry(self.left_frame)
        self.entry_sn.grid(row=row, column=1)
        row += 1
        
        # Status Dropdown
        tk.Label(self.left_frame, text="Status:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.status_var = tk.StringVar()
        self.status_dropdown = tk.OptionMenu(self.left_frame, self.status_var, "In Office", "Checked Out", "Under Maintenance", "Retired")
        self.status_dropdown.grid(row=row, column=1, sticky='w')
        row += 1
        
        # Kit Name Dropdown
        tk.Label(self.left_frame, text="Kit Name:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.kit_name_dropdown = ColumnDropdown(self.left_frame, "kit_name", self.db_manager, row=row, column=1)
        row += 1
        
        # Purchase Company Entry
        tk.Label(self.left_frame, text="Purchase Company:", font=self.bold_font).grid(row=row,column=0, sticky='e')
        self.entry_purchaseCompany = tk.Entry(self.left_frame)
        self.entry_purchaseCompany.grid(row=row, column=1)
        row += 1
        
        # Purchase Date using DateInput Widget
        tk.Label(self.left_frame, text="Purchase Date:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.purchase_date_input = DateInput(self.left_frame, row=row, column=1)
        row += 1
    
        # Cost Entry
        tk.Label(self.left_frame, text="Cost:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_cost = tk.Entry(self.left_frame)
        self.entry_cost.grid(row=row, column=1)
        row += 1
    
        # URL Entry
        tk.Label(self.left_frame, text="URL:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_url = tk.Entry(self.left_frame)
        self.entry_url.grid(row=row, column=1)
        row += 1
    
        # Insurance Checkbox
        tk.Label(self.left_frame, text="Is Insured?", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.is_insured_var = tk.BooleanVar(value=False)
        self.checkbox_insured = tk.Checkbutton(self.left_frame, variable=self.is_insured_var, command=self.toggle_insured)
        self.checkbox_insured.grid(row=row, column=1, sticky='w')
        row += 1
        
        # Date Insured Input
        self.label_date_insured = tk.Label(self.left_frame, text="Date Insured:", font=self.bold_font)
        self.label_date_insured.grid(row=row, column=0, sticky='e')
        self.label_date_insured.grid_remove()
        self.date_insured_input = DateInput(self.left_frame, row=row, column=1)
        # Initially hide the date insured input
        self.date_insured_input.month_menu.grid(row=row, column=1, sticky="e")
        self.date_insured_input.day_entry.grid(row=row, column=2, sticky="w")
        self.date_insured_input.year_entry.grid(row=row, column=3, sticky="w")
        self.date_insured_input.month_menu.grid_remove()
        self.date_insured_input.day_entry.grid_remove()
        self.date_insured_input.year_entry.grid_remove()
        row += 1
    
        # Buttons for Add, Update, Reset
        self.add_button = tk.Button(self.left_frame, text="Add Equipment", command=self.add_equipment)
        self.add_button.grid(row=row, column=0)
        self.update_button = tk.Button(self.left_frame, text="Update Equipment", command=self.update_equipment)
        self.update_button.grid(row=row, column=1)
        self.update_button.grid_remove()
        self.reset_button = tk.Button(self.left_frame, text="Reset Fields", command=self.reset_fields)
        self.reset_button.grid(row=row, column=2)
        row += 1
        
    def setup_right_frame(self):
        self.right_frame = tk.Frame(self, borderwidth=1, relief="solid")
        self.right_frame.grid(column = 1, row = 0, rowspan=2, padx=10, pady=10)
        
        # Label for Equipment List
        tk.Label(self.right_frame, text="Equipment List", font=self.bold_font).grid(column=0,row=0)
        
        # Kit Name Dropdown
        self.kit_var = tk.StringVar(value=self.kit_names[0])
        self.kit_dropdown = tk.OptionMenu(self.right_frame, self.kit_var, *self.kit_names, command=lambda _: self.refresh_equipment_list())
        self.kit_dropdown.grid(column=0,row=1)
        
        # Type Dropdown
        self.type_var = tk.StringVar(value=self.types[0])
        self.type_dropdown = tk.OptionMenu(self.right_frame, self.type_var, *self.types, command=lambda _: self.refresh_equipment_list())
        self.type_dropdown.grid(column=1,row=1)
        
        # Equipment Listbox
        self.equipment_listbox = tk.Listbox(self.right_frame, font=self.value_font, width=50, height=40)
        self.equipment_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.equipment_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Edit and Delete Buttons
        self.edit_button = tk.Button(self.right_frame, text="Edit Equipment", command=self.edit_equipment)
        self.edit_button.grid(row=3, column=0)
        
        self.delete_button = tk.Button(self.right_frame, text="Delete Equipment", command=self.delete_equipment)
        self.delete_button.grid(row=3, column=1)
        
        # Initial Populate Listbox
        self.refresh_equipment_list()
        
    def delete_equipment(self):
        selected_id = self.get_selected_equipment_id()
        if selected_id:
            # Prompt for confirmation
            response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this equipment?")
            if response:
                # Delete the equipment
                self.db_manager.delete_equipment(selected_id)
                messagebox.showinfo("Success", "Equipment deleted successfully")
                # Refresh the equipment list
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
        return [item[0] for item in self.fetch_data(query)]

    def add_equipment(self):
        # Collect data from UI elements
        equipment_data = {
            'name': self.entry_name.get(),
            'brand': self.entry_brand.get(),
            'model': self.entry_model.get(),
            'model_number': self.entry_model_number.get(),
            'description': self.entry_description.get(),
            'serial_number': self.entry_sn.get(),
            'status': self.status_var.get(),
            'kit_name': self.kit_name_dropdown.var.get(),
            'purchase_company': self.entry_purchaseCompany.get(),
            'date_of_purchase': self.purchase_date_input.get_date(),
            'cost': self.entry_cost.get(),
            'website_url': self.entry_url.get(),
            'date_insured': self.date_insured_input.get_date() if self.is_insured_var.get() else None,
            'type': self.type_var.get()
        }
        
        # Validate and convert 'cost' field
        try:
            equipment_data['cost'] = float(equipment_data['cost']) if equipment_data['cost'] else 0.0
        except ValueError:
            messagebox.showerror("Input Error", "Invalid cost value. Please enter a valid number.")
            return  # Stop the execution if the cost value is invalid
        
        # Call DatabaseManager method to add equipment
        self.db_manager.add_or_update_equipment(equipment_data, is_update=False)
        self.refresh_equipment_list()
        self.reset_fields()
        

    def edit_equipment(self):
        selected_id = self.get_selected_equipment_id()
        if selected_id:
            self.populate_fields_for_edit(selected_id)
            self.update_button.grid()
            
    def populate_fields_for_edit(self, equipment_id):
        # Fetch equipment details using the ID
        equipment_details = self.db_manager.get_equipment_details(equipment_id)
        if not equipment_details:
            print("Error: Equipment details not found.")
            return
        
        # Assuming the first item in equipment_details contains the data tuple
        equipment_tuple = equipment_details[0]
        
        # Check if equipment_tuple has enough elements
        if len(equipment_tuple) < 18:  # Adjust the number based on your data structure
            print("Error: Equipment tuple does not have enough elements.")
            return
    
        # Clear existing content in the fields
        self.entry_name.delete(0, tk.END)
        self.entry_brand.delete(0, tk.END)
        self.entry_model.delete(0, tk.END)
        self.entry_model_number.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_sn.delete(0, tk.END)
        self.entry_purchaseCompany.delete(0, tk.END)
        self.entry_cost.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
    
        # Populate the fields with the equipment details
        self.entry_name.insert(0, equipment_tuple[1])  # Name
        self.entry_brand.insert(0, equipment_tuple[3])  # Brand
        self.entry_model.insert(0, equipment_tuple[4])  # Model
        model_number = equipment_tuple[17] if equipment_tuple[17] else ''
        self.entry_model_number.delete(0, tk.END)
        self.entry_model_number.insert(0, model_number)  # Model Number
        self.entry_description.insert(0, equipment_tuple[14])  # Description
        self.entry_sn.insert(0, equipment_tuple[5])  # Serial Number
        self.status_var.set(equipment_tuple[11])  # Status
        self.kit_name_dropdown.var.set(equipment_tuple[18])  # Kit Name
        self.entry_purchaseCompany.insert(0, equipment_tuple[6])  # Purchase Company
        if equipment_tuple[7]:  # Checking if the date_of_purchase is not None
            self.purchase_date_input.set_date(equipment_tuple[7])
        else:
            self.purchase_date_input.reset()  # Reset or clear the date fields if no date is present
            
        self.entry_cost.insert(0, str(equipment_tuple[8]))  # Cost
        self.entry_url.insert(0, equipment_tuple[15])  # URL
    
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
    
    
        # Adjustments for other UI elements, if necessary
        # ...
    
        # Show update button, hide add button
        self.update_button.grid()
    
    def update_equipment(self):
        selected_id = self.get_selected_equipment_id()
        if selected_id:
            # Collecting data from UI elements
            updated_data = {
                'name': self.entry_name.get(),
                'brand': self.entry_brand.get(),
                'model': self.entry_model.get(),
                'model_number': self.entry_model_number.get(),
                'description': self.entry_description.get(),
                'serial_number': self.entry_sn.get(),
                'status': self.status_var.get(),
                'kit_name': self.kit_name_dropdown.var.get(),
                'purchase_company': self.entry_purchaseCompany.get(),
                'date_of_purchase': self.purchase_date_input.get_date(),
                'cost': self.entry_cost.get(),
                'website_url': self.entry_url.get(),
                'date_insured': self.date_insured_input.get_date() if self.is_insured_var.get() else None,
                'type': self.type_name_dropdown.var.get()
            }
            
            # Calling DatabaseManager method to update equipment
            self.db_manager.add_or_update_equipment(updated_data, is_update=True, equipment_id=selected_id)
            
            # Refreshing the equipment list and resetting fields
            self.refresh_equipment_list()
            self.reset_fields()
            
            self.update_button.grid_remove()
    
    def reset_type_dropdown(self):
        default_value = "All Types"  # Replace with your actual default value
        self.type_var.set(default_value)
        
    
    def get_selected_equipment_id(self):
        try:
            selected = self.equipment_listbox.get(self.equipment_listbox.curselection())
            return selected.split(":")[0]
        except tk.TclError:
            messagebox.showerror("Error", "No equipment selected")
            return None
            
    def refresh_equipment_list(self):
        self.equipment_listbox.delete(0, tk.END)  # Clear existing items in the listbox
        
        selected_kit_name = self.kit_var.get()
        selected_type = self.type_var.get()
        
        # Adjust the query based on the selected filters
        query = "SELECT id, name FROM equipment"
        params = []
        if selected_kit_name != "All Kits" or selected_type != "All Types":
            conditions = []
            if selected_kit_name != "All Kits":
                conditions.append("kit_name = %s")
                params.append(selected_kit_name)
            if selected_type != "All Types":
                conditions.append("type = %s")
                params.append(selected_type)
            query += " WHERE " + " AND ".join(conditions)
            
        equipment_list = self.db_manager.fetch_data(query, tuple(params))
        for equipment in equipment_list:
            display_text = f"{equipment[0]}: {equipment[1]}"  # Equipment ID and Name
            self.equipment_listbox.insert(tk.END, display_text)
            
    def on_select(self, event):
        if not self.equipment_listbox.curselection():
            return
        
        selected_index = self.equipment_listbox.curselection()[0]
        selected_id = self.equipment_listbox.get(selected_index).split(":")[0]
        
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
        display_image(self.image_frame, equipment_tuple[1])  # Assuming the name is at index 1
        self.display_details(selected_id)
        
    
    def update_image(self, item_name):
        display_image(self.image_frame, item_name)
        
    def display_details(self, equipment_id):
        for widget in self.container_frame.winfo_children():
            widget.destroy()
            
        equipment_details = self.db_manager.get_equipment_details(equipment_id)
        if equipment_details:
            # Assuming equipment_details[0] is a tuple with all the column values
            equipment_tuple = equipment_details[0]
            column_names = ["ID", "Name", "Type", "Brand", "Model", "Serial Number", 
                            "Purchase Company", "Date of Purchase", "Cost", 
                            "Date Insured", "Storage Location", "Status", 
                            "Current Holder", "Current Condition", "Description", 
                            "Website URL", "Model Number", "Kit Name", "Carrier", 
                            "Tracking Number", "Shipping Address", "Shipping City", 
                            "Shipping State", "Shipping ZIP", "Shipped Date", 
                            "Box Number", "Destination Name", "Shipping Status"]
            
            for index, (col_name, detail) in enumerate(zip(column_names, equipment_tuple)):
                if col_name == "Website URL" and detail: 
                    # For Website URL, create a clickable hyperlink
                    hyperlink = tk.Label(self.container_frame, text=detail, fg="blue", cursor="hand2")
                    hyperlink.grid(row=index, column=1, sticky="w")
                    hyperlink.bind("<Button-1>", lambda e: webbrowser.open(detail))
                else:
                    # For all other columns, display the detail as text
                    value_label = tk.Label(self.container_frame, text=str(detail), font=self.value_font)
                    value_label.grid(row=index, column=1, sticky="w")
                    
                # Create and place the label for the column name
                label = tk.Label(self.container_frame, text=col_name + ":", font=self.bold_font)
                label.grid(row=index, column=0, sticky="w")        
            
    def setup_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.root, borderwidth=1, relief="solid")
        self.bottom_frame.pack(side='bottom', fill='x', expand=False, padx=10, pady=10)
        
        # Status Label for displaying information like "Ready", "Operation Completed", etc.
        self.status_label = tk.Label(self.bottom_frame, text="Ready", font=self.value_font)
        self.status_label.pack(side='left', padx=10)
        
        # Refresh Button
        self.refresh_button = tk.Button(self.bottom_frame, text="Refresh", command=self.refresh_equipment_list)
        self.refresh_button.pack(side='left', padx=10)
        
        # Exit Button
        self.exit_button = tk.Button(self.bottom_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack(side='right', padx=10)
        
    def reset_fields(self):
        # Clearing text entries
        self.entry_name.delete(0, tk.END)
        self.entry_brand.delete(0, tk.END)
        self.entry_model.delete(0, tk.END)
        self.entry_model_number.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_sn.delete(0, tk.END)
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
        self.toggle_insured()\
        
        # Reset type_dropdown
        default_type = "All Types"  # Replace with your actual default value
        self.type_var.set(default_type)
        
        
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
    
