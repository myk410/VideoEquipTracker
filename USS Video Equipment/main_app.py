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
        self.current_editing_id = None  # Add this line
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
        #self.setup_shipping_frame()
        self.setup_image_frame()
        self.setup_details_frame()
        self.setup_bottom_frame()
        
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
        
        # Weight Entry
        tk.Label(self.left_frame, text="Weight (lbs):", font=self.bold_font).grid(row=row, column=0, sticky='e')
        self.entry_weight = tk.Entry(self.left_frame)
        self.entry_weight.grid(row=row, column=1)
        row += 1
        
        # Status Dropdown
        tk.Label(self.left_frame, text="Status:", font=self.bold_font).grid(row=row, column=0, sticky='e')
        
        # Initialize the StringVar with a string of spaces of length 15
        self.status_var = tk.StringVar(value=' ' * 15)
        self.status_dropdown = tk.OptionMenu(self.left_frame, self.status_var, "In Office", "Checked Out", "Under Maintenance", "Retired")
        # Set the width of the dropdown menu to 15
        self.status_dropdown.config(width=15)
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
            'weight': self.entry_weight.get(),
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
            self.current_editing_id = selected_id
            self.populate_fields_for_edit(selected_id)
            self.update_button.grid()
            
    def populate_fields_for_edit(self, equipment_id):
        equipment_details = self.db_manager.get_equipment_details(equipment_id)
        if not equipment_details:
            print("Error: Equipment details not found.")
            return
        
        equipment_tuple = equipment_details[0]
        if len(equipment_tuple) < 18:  # Adjust the number based on your data structure
            print("Error: Equipment tuple does not have enough elements.")
            return
        
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
        self.entry_weight.delete(0, tk.END)
        self.entry_purchaseCompany.delete(0, tk.END)
        self.entry_cost.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
    
        # Populate the fields with the equipment details
        self.entry_name.insert(0, equipment_tuple[1])  # Name
        self.entry_brand.insert(0, equipment_tuple[3])  # Brand
        self.entry_model.insert(0, equipment_tuple[4])  # Model
        model_number = equipment_tuple[16] if equipment_tuple[16] else ''
        self.entry_model_number.delete(0, tk.END)
        self.entry_model_number.insert(0, model_number)  # Model Number
        self.entry_description.insert(0, equipment_tuple[14])  # Description
        self.entry_sn.insert(0, equipment_tuple[5])  # Serial Number
        self.entry_weight.insert(0, str(equipment_tuple[28]))
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
        
        # Update the Kit Name Dropdown
        kit_name_index = 17  # Update this index based on your database structure
        kit_name = equipment_tuple[kit_name_index]
        if kit_name:
            self.kit_name_dropdown.var.set(kit_name)
        else:
            self.kit_name_dropdown.reset_to_default()
    
    
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
            'type': self.type_name_dropdown.var.get()
        }
        
        # Update equipment
        self.db_manager.add_or_update_equipment(updated_data, is_update=True, equipment_id=self.current_editing_id)
        
        # Refresh the equipment list
        self.refresh_equipment_list()
        
        # Find and select the updated equipment in the listbox
        for index, item in enumerate(self.equipment_listbox.get(0, tk.END)):
            if int(item.split(":")[0]) == self.current_editing_id:
                self.equipment_listbox.selection_set(index)
                self.equipment_listbox.see(index)
                self.equipment_listbox.activate(index)  # This line activates the selection
                break
            
        # Reset the editing ID
        self.current_editing_id = None
        
        self.update_button.grid_remove()
        
        # Show confirmation popup
        messagebox.showinfo("Success", "Equipment updated successfully")
        
    def reset_type_dropdown(self):
        default_value = "All Types"  # Replace with your actual default value
        self.type_var.set(default_value)
        
    
    def get_selected_equipment_id(self):
        try:
            selected = self.equipment_listbox.get(self.equipment_listbox.curselection())
            return int(selected.split(":")[0])  # Ensure it's an integer
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
                            "Purchase Company", "Date of Purchase", "Cost",  # Added 'Weight' here
                            "Date Insured", "Storage Location", "Status",
                            "Current Holder", "Current Condition", "Description",
                            "Website URL", "Model Number", "Kit Name", "Carrier",
                            "Tracking Number", "Shipping Address", "Shipping City",
                            "Shipping State", "Shipping ZIP", "Shipped Date",
                            "Box Number", "Destination Name", "Shipping Status", "Weight"]
            
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
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(column=0,row=2, padx=10, pady=10)
        
        row=0
        
        self.shipping_button = tk.Button(self.bottom_frame, text="Shipping", command=self.open_shipping_window)
        self.shipping_button.grid(column=0, row=row, padx=10)
        row += 1

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
    

    def open_shipping_window(self):
        self.shipping_window = tk.Toplevel(self)
        self.shipping_window.title("Shipping Information")
        
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
        self.carrier_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_carrier)
        self.carrier_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Carrier:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_carrier = tk.Entry(self.shipping_window)
        self.entry_carrier.grid(row=row, column=2)
        row += 1
        
        # Tracking Number Input with Checkbox
        self.tracking_number_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_tracking_number)
        self.tracking_number_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Tracking Number:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_tracking_number = tk.Entry(self.shipping_window)
        self.entry_tracking_number.grid(row=row, column=2)
        row += 1
        
        # Shipping Address Input with Checkbox
        self.shipping_address_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_shipping_address)
        self.shipping_address_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Shipping Address:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_address = tk.Entry(self.shipping_window)
        self.entry_shipping_address.grid(row=row, column=2)
        row += 1
        
        # City Input with Checkbox
        self.city_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_city)
        self.city_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="City:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_city = tk.Entry(self.shipping_window)
        self.entry_shipping_city.grid(row=row, column=2)
        row += 1
        
        # State Input with Checkbox
        self.state_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_state)
        self.state_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="State:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_state = tk.Entry(self.shipping_window)
        self.entry_shipping_state.grid(row=row, column=2)
        row += 1
        
        # ZIP Code Input with Checkbox
        self.zip_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_zip)
        self.zip_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="ZIP Code:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_zip = tk.Entry(self.shipping_window)
        self.entry_shipping_zip.grid(row=row, column=2)
        row += 1
        
        # Shipped Date Input with Checkbox
        self.shipped_date_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_shipping_date)
        self.shipped_date_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Shipped Date:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.shipped_date_input = DateInput(self.shipping_window, row=row, column=2)
        row += 1
        
        # Box Number Input with Checkbox
        self.box_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_box)
        self.box_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Box Number:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_box_number = tk.Entry(self.shipping_window)
        self.entry_box_number.grid(row=row, column=2)
        row += 1
        
        # Destination Name Input with Checkbox
        self.destination_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_destination)
        self.destination_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Destination Name:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_destination_name = tk.Entry(self.shipping_window)
        self.entry_destination_name.grid(row=row, column=2)
        row += 1
        
        # Shipping Status Input with Checkbox
        self.shipping_status_checkbox = tk.Checkbutton(self.shipping_window, variable=self.update_shipping_status)
        self.shipping_status_checkbox.grid(row=row, column=0, sticky='w')
        tk.Label(self.shipping_window, text="Shipping Status:", font=self.bold_font).grid(row=row, column=1, sticky='e')
        self.entry_shipping_status = tk.Entry(self.shipping_window)
        self.entry_shipping_status.grid(row=row, column=2)
        row += 1
        
        # Button to apply shipping details
        apply_button = tk.Button(self.shipping_window, text="Apply Shipping Info", command=self.apply_shipping_info)
        apply_button.grid(column=1, columnspan=2, row=row, pady=10)
        
        # View mode radio buttons for selecting individual items or kits
        self.view_mode = tk.IntVar(value=0)  # 0 for individual items, 1 for kits
        tk.Radiobutton(self.shipping_window, text="Individual Items", variable=self.view_mode, value=0, command=self.populate_shipping_listbox).grid(row=0, column=3, sticky='w')
        tk.Radiobutton(self.shipping_window, text="Kits", variable=self.view_mode, value=1, command=self.populate_shipping_listbox).grid(row=0, column=4, sticky='w')
        row += 1
    
        # Create a Listbox to display equipment or kits
        #self.shipping_listbox = tk.Listbox(self.shipping_window, width=50, height=15)
        #self.shipping_listbox.grid(column=3, row=row, columnspan=2, padx=10, pady=10)
    
        # Create scrollable frame for checkboxes
        self.checkbox_frame = self.create_scrollable_frame(self.shipping_window, 2, 3, row, 2)
        self.checkbox_vars = {}
    
        # Populate the Listbox with checkboxes
        self.populate_shipping_listbox()
        
        
    def populate_shipping_listbox(self):
        # Clear existing checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
            
        self.checkbox_vars.clear()
        
        if self.view_mode.get() == 0:
            # Populate with individual items
            equipment_list = self.db_manager.get_equipment_list()
            for equipment in equipment_list:
                var = tk.IntVar()
                checkbox = tk.Checkbutton(self.checkbox_frame, text=f"{equipment[0]}: {equipment[1]}", variable=var)
                checkbox.pack(anchor='w')
                self.checkbox_vars[equipment[0]] = var
        else:
            # Populate with kits
            kit_list = self.db_manager.fetch_kit_names()
            for kit in kit_list:
                var = tk.IntVar()
                checkbox = tk.Checkbutton(self.checkbox_frame, text=kit, variable=var)
                checkbox.pack(anchor='w')
                self.checkbox_vars[kit] = var
            
    def apply_shipping_info(self):
        selected_items = [key for key, value in self.checkbox_vars.items() if value.get() == 1]
        
        # Dictionary to hold the fields to update
        shipping_info = self.collect_shipping_info()
        
        # Check if any field was selected for update
        if not shipping_info:
            messagebox.showwarning("No Selection", "No fields selected for update.")
            return
        
        # If view mode is set to kits, update all items in the selected kits
        if self.view_mode.get() == 1:
            for kit in selected_items:
                equipment_ids = self.fetch_equipment_ids_by_kit(kit)
                for equipment_id in equipment_ids:
                    self.db_manager.update_shipping_info(equipment_id, shipping_info)
        else:
            # Update the database for each selected individual item
            for item_id in selected_items:
                self.db_manager.update_shipping_info(item_id, shipping_info)
                
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
    
