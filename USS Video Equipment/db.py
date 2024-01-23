# db.py
import mysql.connector
from mysql.connector import Error
import modules.connect as ct

remote = ct.remote
local = ct.local
server = local # local or remote
host_ct = server.host
user_ct = server.user
passwd_ct = server.passwd
database_ct = server.database

class MySQLConnection:
    def __init__(self, host, user, passwd, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        
    def __enter__(self):
        self.conn = mysql.connector.connect(
            host=self.host, 
            user=self.user, 
            passwd=self.passwd, 
            database=self.database
        )
        return self.conn
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

class DatabaseManager:
    def __init__(self):
        self.host = host_ct
        self.user = user_ct
        self.passwd = passwd_ct
        self.database = database_ct

    def create_connection(self):
        return MySQLConnection(self.host, self.user, self.passwd, self.database)

    def execute_query(self, query, params=None):
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_data(self, query, params=None):
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        
    def get_equipment_details(self, equipment_id):
        query = "SELECT * FROM equipment WHERE id = %s"
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (equipment_id,))
                results = cursor.fetchall()
                return results  # Only return the results
        except Error as e:
            print(f"Error fetching data: {e}")
            return []

    def get_unique_values(self, column_name):
        query = f"SELECT DISTINCT {column_name} FROM equipment WHERE {column_name} IS NOT NULL"
        return self.fetch_data(query)

    def add_or_update_equipment(self, data, is_update=False, equipment_id=None):
        with self.create_connection() as conn:
            cursor = conn.cursor()
        
            # Convert weight to float (or the appropriate data type)
            try:
                data['weight'] = float(data['weight']) if data['weight'] else 0.0
            except ValueError:
                print("Invalid weight value. Setting to 0.0")
                data['weight'] = 0.0
                
            try:
                # Convert kit_name to string outside the params tuple
                data['kit_name'] = str(data['kit_name'])
            
                if is_update:
                    # Update existing equipment
                    query = """UPDATE equipment SET name=%s, brand=%s, model=%s, description=%s, serial_number=%s, purchase_company=%s, date_of_purchase=%s, cost=%s, website_url=%s, date_insured=%s, status=%s, model_number=%s, kit_name=%s, type=%s, weight=%s, owner=%s, not_purchased=%s WHERE id=%s"""
                    params = (data['name'], data['brand'], data['model'], data['description'], data['serial_number'], data['purchase_company'], data['date_of_purchase'], data['cost'], data['website_url'], data['date_insured'], data['status'], data['model_number'], data['kit_name'], data['type'], data['weight'], data['owner'], data['not_purchased'], equipment_id)
                else:
                    # Add new equipment
                    query = """INSERT INTO equipment (name, brand, model, description, serial_number, purchase_company, date_of_purchase, cost, website_url, date_insured, status, model_number, kit_name, type, weight, owner, not_purchased) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    params = (data['name'], data['brand'], data['model'], data['description'], data['serial_number'], data['purchase_company'], data['date_of_purchase'], data['cost'], data['website_url'], data['date_insured'], data['status'], data['model_number'], data['kit_name'], data['type'], data['weight'], data['owner'], data['not_purchased'])
                    
                cursor.execute(query, params)
                conn.commit()
            except Error as e:
                    print(f"Error: {e}")
            finally:
                    cursor.close()
                    conn.close()
                
            

    def delete_equipment(self, equipment_id):
        query = "DELETE FROM equipment WHERE id = %s"
        self.execute_query(query, (equipment_id,))
        
    def get_equipment_list(self):
        query = "SELECT id, name FROM equipment"
        return self.fetch_data(query)
    
    def fetch_kit_names(self):
        query = "SELECT DISTINCT kit_name FROM equipment WHERE kit_name IS NOT NULL"
        kit_names = [str(row[0]) for row in self.fetch_data(query)]  # Convert to string
        return kit_names
    
    def update_shipping_info(self, equipment_id, shipping_info):
        # Start constructing the query
        query = "UPDATE equipment SET "
        
        # List to store query parameters
        params = []
        
        # Add each field to the query only if it's in the shipping_info dictionary
        query_parts = []
        for field, value in shipping_info.items():
            query_parts.append(f"{field} = %s")
            params.append(value)
            
        # Join the query parts with commas
        query += ", ".join(query_parts)
        
        # Add the WHERE clause to target the specific equipment item
        query += " WHERE id = %s"
        params.append(equipment_id)        
        
        # Execute the query
        self.execute_query(query, params)
        
    # Part of DatabaseManager class in db.py
        
    def get_boxes(self):
        query = "SELECT DISTINCT box_number FROM equipment WHERE box_number IS NOT NULL ORDER BY box_number"
        try:
            return self.fetch_data(query)
        except Error as e:
            print(f"Error fetching box numbers: {e}")
            return []
        
    def get_items_in_box(self, box_id):
        query = "SELECT name, weight, kit_name FROM equipment WHERE box_number = %s"
        try:
            return self.fetch_data(query, (box_id,))
        except Error as e:
            print(f"Error fetching items for box {box_id}: {e}")
            return []
        
    def get_unique_owners(self):
        query = "SELECT DISTINCT owner FROM equipment WHERE owner IS NOT NULL"
        return sorted([item[0] for item in self.fetch_data(query)])
    
    def get_unique_types(self):
        query = "SELECT DISTINCT type FROM equipment WHERE type IS NOT NULL"
        results = self.fetch_data(query)
        return sorted([result[0] for result in results])
    
    def get_unique_names(self):
        query = "SELECT DISTINCT name FROM equipment"
        return [item[0] for item in self.fetch_data(query)]
    
    def update_equipment_name(self, old_name, new_name):
        query = "UPDATE equipment SET name = %s WHERE name = %s"
        self.execute_query(query, (new_name, old_name))
        
    def fetch_all_equipment(self):
        query = "SELECT name, brand, model, model_number, serial_number, purchase_company, date_of_purchase, cost, owner, website_url FROM equipment"
        return self.fetch_data(query)
        
        
        
