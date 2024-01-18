# db.py
import mysql.connector
from mysql.connector import Error
import modules.connect as ct

class DatabaseManager:
    def __init__(self):
        self.host = ct.host
        self.user = ct.user
        self.passwd = ct.passwd
        self.database = ct.database

    def create_connection(self):
        try:
            conn = mysql.connector.connect(
                host=self.host, user=self.user, passwd=self.passwd, database=self.database
            )
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

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
        conn = self.create_connection()
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
                query = """UPDATE equipment SET name=%s, brand=%s, model=%s, description=%s, serial_number=%s, purchase_company=%s, date_of_purchase=%s, cost=%s, website_url=%s, date_insured=%s, status=%s, model_number=%s, kit_name=%s, type=%s, weight=%s WHERE id=%s"""
                params = (data['name'], data['brand'], data['model'], data['description'], data['serial_number'], data['purchase_company'], data['date_of_purchase'], data['cost'], data['website_url'], data['date_insured'], data['status'], data['model_number'], data['kit_name'], data['type'], data['weight'], equipment_id)
            else:
                # Add new equipment
                query = """INSERT INTO equipment (name, brand, model, description, serial_number, purchase_company, date_of_purchase, cost, website_url, date_insured, status, model_number, kit_name, type)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                params = (data['name'], data['brand'], data['model'], data['description'], data['serial_number'],
                                    data['purchase_company'], data['date_of_purchase'], data['cost'], data['website_url'],
                                    data['date_insured'], data['status'], data['model_number'], data['kit_name'], data['type'])
                
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
    
    def get_unique_types(self):
        query = "SELECT DISTINCT type FROM equipment WHERE type IS NOT NULL"
        results = self.fetch_data(query)
        return [result[0] for result in results]  # Assuming each result is a tuple with the type as the first element
    
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
        query = "SELECT name, weight FROM equipment WHERE box_number = %s"
        try:
            return self.fetch_data(query, (box_id,))
        except Error as e:
            print(f"Error fetching items for box {box_id}: {e}")
            return []
        
        
