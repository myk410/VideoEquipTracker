# widgets.py
import tkinter as tk

class DateInput:
    def __init__(self, parent, row, column):
        self.date_frame = tk.Frame(parent)
        self.date_frame.grid(row=row, column=column, sticky="w")
        
        self.months = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
        self.month_var = tk.StringVar(self.date_frame)
        self.month_var.set(self.months[0])
        self.day_var = tk.StringVar(self.date_frame)
        self.year_var = tk.StringVar(self.date_frame)
        
        self.month_menu = tk.OptionMenu(self.date_frame, self.month_var, *self.months)
        pixel_width = 5  # Adjust this value based on the UI requirement
        self.month_menu.config(width=pixel_width)
        self.month_menu.grid(row=0, column=0, sticky="w")
        
        self.day_entry = tk.Entry(self.date_frame, textvariable=self.day_var, width=2)
        self.day_entry.grid(row=0, column=1, sticky="w")
        
        self.year_entry = tk.Entry(self.date_frame, textvariable=self.year_var, width=4)
        self.year_entry.grid(row=0, column=2, sticky="w")

    def reset(self):
        self.month_var.set(self.months[0])  # Reset to the first month in the list
        self.day_var.set('1')  # Reset to the first day
        self.year_var.set('2024')  # Reset to a default year, change as needed

    def get_date(self):
        month = self.months.index(self.month_var.get()) + 1
        day = self.day_var.get()
        year = self.year_var.get()
        
        # Validate day and year are not empty and are digits
        if not day.isdigit() or not year.isdigit():
            return None  # or some default date, or raise an error
        
        day = int(day)
        year = int(year)
        
        # Additional validation can be added here if necessary
        # (e.g., check if the day is within the valid range for the month)
        
        return f"{year}-{month:02d}-{day:02d}"  # Format as YYYY-MM-DD
    
    def set_date(self, date_obj):
        if date_obj:
            self.month_var.set(self.months[date_obj.month - 1])
            self.day_var.set(str(date_obj.day))
            self.year_var.set(str(date_obj.year))

class ColumnDropdown:
    def __init__(self, parent, column_name, db_manager, row, column, button_label="New"):
        self.column_name = column_name
        self.db_manager = db_manager
        self.var = tk.StringVar(parent)
        self.update_options()
        
        self.dropdown_frame = tk.Frame(parent)
        self.dropdown_frame.grid(row=row, column=column, sticky='w')
        
        self.dropdown_menu = tk.OptionMenu(self.dropdown_frame, self.var, *self.options)
        self.dropdown_menu.grid(row=0, column=0, sticky='w')
        
        self.add_popup_button = tk.Button(self.dropdown_frame, text=button_label, command=self.create_add_popup)
        self.add_popup_button.grid(row=0, column=1, sticky='w')
        
        self.popup = None
        
    def reset_to_default(self):
        if self.options:
            self.var.set(self.options[0])

    def update_options(self):
        self.options = ['None'] + self.db_manager.get_unique_values(self.column_name)
        self.var.set(self.options[0])

    def create_add_popup(self):
        formatted_column_name = self.column_name.replace('_', ' ').title()
        self.popup = tk.Toplevel()
        self.popup.title(f"Add New {formatted_column_name}")
        add_frame = tk.Frame(self.popup)
        add_frame.pack(padx=30, pady=10)
        new_value_entry = tk.Entry(add_frame)
        new_value_entry.pack()
        add_button = tk.Button(add_frame, text="Add", command=lambda: self.add_new_option_to_list(new_value_entry.get()))
        add_button.pack()

    def add_new_option_to_list(self, new_value):
        if new_value and new_value != 'None' and new_value not in self.options:
            self.options.append(new_value)
            self.var.set(new_value)
            self.update_dropdown()
            self.popup.destroy()

    def update_dropdown(self):
        grid_info = self.dropdown_menu.grid_info()
        row = grid_info['row']
        column = grid_info['column']
        columnspan = grid_info['columnspan']
        self.dropdown_menu.destroy()
        self.dropdown_menu = tk.OptionMenu(self.dropdown_menu.master, self.var, *self.options)
        self.dropdown_menu.grid(row=row, column=column, columnspan=columnspan)
        
