import pymysql

class Database:
    def __init__(self, host, user, password, database):
        self.host, self.user, self.password, self.database = host, user, password, database
        
        # create connection
        try:
            self.my_db = pymysql.connect(
                host=self.host, 
                user=self.user, 
                password=self.password, 
                database=self.database
            )
        
            self.cursor = self.my_db.cursor()
            self.sql = ""

        except Exception as err:
            print(err)

    def insert(self, table, columns, values):
        self.sql = f"INSERT INTO {table} ("
        if isinstance(columns, list):
            for col in columns:
                self.sql += f"`{col}`, "
            self.sql = self.sql.rstrip(", ")
            self.sql += ") VALUES ("
        else:
            raise TypeError(f"Expected a list but found {type(columns)}")
        
        if isinstance(values, list):
            for val in values:
                self.sql += f"'{val}', "
            self.sql = self.sql.rstrip(", ")
            self.sql += ")"
        else:
            raise TypeError(f"Expected a list but found {type(values)}")
        
        
        self.cursor.execute(self.sql)
        self.my_db.commit()


    def read(self, table, clause=None, columns=None):
        if not columns:
            self.sql = f"SELECT * FROM {table}"
            if clause and isinstance(clause, dict):
                self.sql += " WHERE "
                for key, val in clause.items():
                    self.sql += f"{key}='{val}' AND "
                self.sql = self.sql.rstrip("AND ")
            elif clause and not isinstance(clause, dict):
                raise TypeError(f"Expected a dictionary but found {type(clause)}")
        else:
            if isinstance(columns, list):
                self.sql = f"SELECT "
                for col in columns:
                    self.sql += f"{col}, "
                self.sql = self.sql.rstrip(", ")
                self.sql += f" FROM {table}"
                if clause and isinstance(clause, dict):
                    self.sql += " WHERE "
                    for key, val in clause.items():
                        self.sql += f"{key}='{val}' AND "
                    self.sql = self.sql.rstrip("AND ")
                elif clause and not isinstance(clause, dict):
                    raise TypeError(f"Expected a dictionary but found {type(clause)}")
            else:
                raise TypeError(f"Expected a list but found {type(columns)}")
        self.cursor.execute(self.sql)
        results = self.cursor.fetchall()
        return results


    def delete(self, table_name, text):
        self.sql = f"DELETE FROM {table_name} WHERE task = '{text}'"
        self.cursor.execute(self.sql)
        self.my_db.commit()

    def update(self, table, update, clause):
        self.sql =  f"UPDATE {table} SET "
        for key, val in update.items():
            self.sql += f"{key}='{val}' and "
        self.sql = self.sql.rstrip('and ')


        self.sql += " WHERE "
        for key, val in clause.items():
            self.sql += f"{key}='{val}' and "
        self.sql = self.sql.rstrip('and ')

        self.cursor.execute(self.sql)
        self.my_db.commit()
        
    def close(self):
        self.my_db.close()

                
if __name__ == "__main__":
    db = Database("localhost", "root", "", "car_rental_db")

