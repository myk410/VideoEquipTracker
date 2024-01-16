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
        details = self.fetch_data(query, (equipment_id,))
        return details

    def get_unique_values(self, column_name):
        query = f"SELECT DISTINCT {column_name} FROM equipment WHERE {column_name} IS NOT NULL"
        return self.fetch_data(query)

    def add_or_update_equipment(self, data, is_update=False, equipment_id=None):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            if is_update:
                # Update existing equipment
                query = """UPDATE equipment SET 
                                        name=%s, brand=%s, model=%s, description=%s, serial_number=%s,
                                        purchase_company=%s, date_of_purchase=%s, cost=%s, website_url=%s,
                                        date_insured=%s, status=%s, model_number=%s, kit_name=%s, type=%s
                                        WHERE id=%s"""
                params = (data['name'], data['brand'], data['model'], data['description'], data['serial_number'],
                                    data['purchase_company'], data['date_of_purchase'], data['cost'], data['website_url'],
                                    data['date_insured'], data['status'], data['model_number'], data['kit_name'], data['type'], equipment_id)
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
        
    def get_equipment_list(self):
        query = "SELECT id, name FROM equipment"
        return self.fetch_data(query)
    
    def fetch_kit_names(self):
        query = "SELECT DISTINCT kit_name FROM equipment WHERE kit_name IS NOT NULL"
        kit_names = [row[0] for row in self.fetch_data(query)]
        return kit_names
    
    def get_unique_types(self):
        query = "SELECT DISTINCT type FROM equipment WHERE type IS NOT NULL"
        results = self.fetch_data(query)
        return [result[0] for result in results]  # Assuming each result is a tuple with the type as the first element
    
