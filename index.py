import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import re
import sys
import bcrypt
import os
import shutil
from main import Ui_mainWindow
from db import Database
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from test_run.design import AuctionWindow, CarBox
from reciept import PDFPreviewApp


class Window(QMainWindow, Ui_mainWindow):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.car_price = 0
      self.tax = 0
      self.total_fee = 0
      self.ui = Ui_mainWindow()
      self.setupUi(self)
      self.image_paths = []
      self.db = Database("localhost", "root", "", "car_rental_db")
      self.auction_window = None

      # Fetch car data from the database
      car_data_list = self.fetch_car_data()
      
      if car_data_list:
         self.car_box = CarBox(car_data_list[0])
      else:
         self.car_box = None

      # triggering buttons
      self.get_started_button.clicked.connect(self.show_login_page)
      self.log_back_button.clicked.connect(self.show_login_page)
      self.create_acc_button.clicked.connect(self.show_signup_page)
      self.host_button.clicked.connect(self.show_list_page)
      self.pushButton.clicked.connect(self.show_main_page)
      self.pushButton_2.clicked.connect(self.show_signup_page)
      self.pushButton_4.clicked.connect(self.show_garage_page)
      self.pushButton_6.clicked.connect(self.show_garage_page)
      self.pushButton_8.clicked.connect(self.show_garage_page)     

      self.signup_button.clicked.connect(self.signup_user)
      self.login_button.clicked.connect(self.login_user)
      self.logout_button.clicked.connect(self.logout_user)
      self.submit_button.clicked.connect(self.car_list)
      self.upload_button.clicked.connect(self.select_images)
      self.reserve_button.clicked.connect(self.rental_user_info)
      self.checkout_button.clicked.connect(self.protection_page_info)


   def show_main_page(self):
      self.stackedWidget.setCurrentIndex(0)

   def show_login_page(self):
      self.stackedWidget.setCurrentIndex(1)

   def show_signup_page(self):
      self.stackedWidget.setCurrentIndex(2)

   def show_garage_page(self):
      self.stackedWidget.setCurrentIndex(3)

      if self.auction_window:
         self.auction_window.close()

      car_data_list = self.fetch_car_data()

   # Pass self.protection_page as the callback
      self.auction_window = AuctionWindow(
         car_data_list, 
         cars_per_page=2, 
         parent_frame=self.car_list_frame,
         protection_callback=self.protection_page
      )
      self.auction_window.show()

      for car_box, car_data in zip(self.auction_window.car_boxes, car_data_list):
         car_box.select_button.clicked.connect(lambda _, data=car_data: self.auction_window.on_car_selected_and_protection(data))

   def show_list_page(self):
      self.stackedWidget.setCurrentIndex(4)

   def protection_page(self, car_price):
      self.stackedWidget.setCurrentIndex(5)

      self.car_price = float(car_price)
      self.total_label.setText(f"GH₵{car_price:,.2f}")

       # Connect checkboxes to the method that will update the total price
      self.pack1_check.toggled.connect(self.update_total_price)
      self.pack2_check.toggled.connect(self.update_total_price)
      self.pack3_check.toggled.connect(self.update_total_price)

   def update_total_price(self):
      # Get the checkbox prices
      tax1 = float(self.extract_num(self.pack1_check.text())) if self.pack1_check.isChecked() else 0
      tax2 = float(self.extract_num(self.pack2_check.text())) if self.pack2_check.isChecked() else 0
      tax3 = float(self.extract_num(self.pack3_check.text())) if self.pack3_check.isChecked() else 0
      
      # Calculate the total fee
      total_fee = self.car_price + tax1 + tax2 + tax3
      
      # Update the total_label to display the new total price
      self.total_label.setText(f"GH₵{total_fee:,.2f}")
      self.total_fee = total_fee

      # Store the selected tax value in self.tax
      if self.pack1_check.isChecked():
         self.tax = tax1
      elif self.pack2_check.isChecked():
         self.tax = tax2
      elif self.pack3_check.isChecked():
         self.tax = tax3
      else:
         self.tax = 0 

   # Function to extract the numerical value from the checkbox text
   def extract_num(self, text):
      numbers = re.findall(r'\d+', text)
      return ''.join(numbers)

   def checkout_page(self):
      self.stackedWidget.setCurrentIndex(6)

   def login_user(self, user_id):
      email = self.login_email.text()
      password = self.login_pword.text()

      self.current_user_id = user_id

      if not all([email, password]):
         QMessageBox.warning(self, "Input Error", "All fields must be filled out")
         return

      if not self.validate_email(email):
         QMessageBox.warning(self, "Input Error", "Invalid email format.")
         return

      # Fetch the user data based on email
      clause = {'email': email}
      results = self.db.read("users", clause=clause, columns=None)

      if results:
         s_hashed_password = results[0][5]

         if bcrypt.checkpw(password.encode('utf-8'), s_hashed_password.encode('utf-8')):
            QMessageBox.information(self, "Success", f"Welcome Back.")
            self.current_user_id = results[0][0]

            self.show_garage_page()
         else:
            QMessageBox.warning(self, "Login Error", "Invalid email or password.")
      else:
         QMessageBox.warning(self, "Login Error", "Invalid email or password.")
         
      self.reset()

   def signup_user(self, user_id):
      fname = self.fname_entry.text()
      lname = self.lname_entry.text()
      number = self.number_entry.text()
      email = self.email_entry.text()
      password = self.pword_entry.text()
      confirm_password = self.cpword_entry.text()
      region = self.comboBox.currentText()

      self.current_user_id = user_id

      if password != confirm_password:
         QMessageBox.warning(self, "Input Error", "Passwords do not match")
         return
            
      if not all([fname, lname, number, email, password, confirm_password, region]):
         QMessageBox.warning(self, "Input Error", "All fields must be filled out")
         return
      
      if not self.validate_email(email):
         QMessageBox.warning(self, "Input Error", "Invalid email address") 
         return
      
      if len(password) <= 5:
         QMessageBox.warning(self, "Password Error", "Password must be more than 5")
         return
      
      if not number.isdigit():
         QMessageBox.warning(self, "Input Error", "Phone number must be integers")
         return
      
      # Hash the password
      hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  
      
      columns = ['fname', 'lname', 'number', 'email', 'password', 'region']
      values = [fname, lname, number, email, hashed_password, region]
      
      self.db.insert("users", columns, values)
      QMessageBox.information(self, "Success", "Signup successful")

      # Automatically log in the user
      clause = {'email': email}
      results = self.db.read("users", clause=clause, columns=None)
      if results:
         self.current_user_id = results[0][0]
      self.show_garage_page()
      self.reset()

   def logout_user(self):
      self.current_user_id = None
      QMessageBox.information(self, "Success", "You have been logged out.")
      self.show_main_page()

   def validate_email(self, email):
      email_pattern = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
      if re.match(email_pattern, email):
         return True
      else:
         False

   def car_list(self):
      license_num = self.license_num_entry.text()
      car_availability = self.dateEdit.date().toString('yyyy-MM-dd')
      car_model = self.car_model_entry.text()
      car_num = self.car_number_entry.text()
      seats = self.seats_entry.text()
      location = self.pickup_entry.text()
      contact_info = self.contact_info_entry.text()
      price = self.price_entry.text()
      odometer = self.odometer_entry.text()
      transmision_type = self.transmission_combo.currentText()
      image_path = self.image_path_entry.text()

      if not all([license_num, car_availability, car_model, car_num, seats, location, contact_info, price, odometer,transmision_type,
                  image_path]):
         QMessageBox.warning(self, "Input Error", "All fields must be filled out")
         self.reset()
         return
      
      if not seats.isdigit():
        QMessageBox.warning(self, "Input Error", "Number of seats must be an integer")
        return
      
      if not price.isdigit():
        QMessageBox.warning(self, "Input Error", "Price must be an integer")
        return
      
      
      # Save the images to the filesystem
      saved_paths = self.save_images_to_filesystem(image_path)
      
      user_id = self.current_user_id

      columns = ['user_id', 'license num', 'car availability', 'car model', 'car number', 'no of seats', 'pickup location', 'contact', 'price', 'odometer', 'transmission type',
                 'image_path']
      values = [user_id, license_num, car_availability, car_model, car_num, seats, location, contact_info, price, odometer, transmision_type,
                saved_paths]

      self.db.insert("car_list", columns, values)
      QMessageBox.information(self, "Success", "Car submitted successfully")

      self.checkBox_4.setCheckable(False)
      self.show_garage_page()
      self.reset()

   def select_images(self):
      files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)")
      if files:
         
         file_paths = ';'.join(files)
         self.image_path_entry.setText(file_paths)

   def save_images_to_filesystem(self, image_paths):
      script_dir = os.path.dirname(os.path.abspath(__file__))
      current_user_id = self.current_user_id

      upload_dir = os.path.join(script_dir, "uploads", f"user{current_user_id}")  # Directory to save the images
      if not os.path.exists(upload_dir):
         os.makedirs(upload_dir)
      
      saved_paths = []

      for file_path in image_paths.split(';'):
         filename = os.path.basename(file_path)
         destination_path = os.path.join(upload_dir, filename)
         shutil.copy(file_path, destination_path)
         
         # Save the relative path instead of the full destination path
         relative_path = os.path.join("uploads", f"user{current_user_id}", filename)
         relative_path = relative_path.replace("\\", "/")
         saved_paths.append(relative_path)
      
      return ';'.join(saved_paths)


   def reset(self):
      self.login_email.clear()
      self.login_pword.clear()
      self.fname_entry.clear()
      self.lname_entry.clear()
      self.number_entry.clear()
      self.email_entry.clear()
      self.pword_entry.clear()
      self.cpword_entry.clear()
      self.license_num_entry.clear()
      self.dateEdit.clear()
      self.car_model_entry.clear()
      self.car_number_entry.clear()
      self.seats_entry.clear()
      self.pickup_entry.clear()
      self.contact_info_entry.clear()
      self.price_entry.clear()
      self.odometer_entry.clear()
      self.checkBox.setCheckable(False)
      self.checkBox.setCheckable(True)
      self.checkBox_4.setCheckable(False)
      self.checkBox_4.setCheckable(True)
      self.image_path_entry.clear()
      self.lineEdit.clear()
      self.lineEdit_2.clear()
      self.lineEdit_3.clear()
      self.lineEdit_4.clear()
      self.lineEdit_5.clear()
      self.lineEdit_6.clear()
      self.pack1_check.setCheckable(False)
      self.pack1_check.setCheckable(True)
      self.pack2_check.setCheckable(False)
      self.pack2_check.setCheckable(True)
      self.pack3_check.setCheckable(False)
      self.pack3_check.setCheckable(True)
      self.checkBox_2.setCheckable(False)
      self.checkBox_2.setCheckable(True)
      self.terms_check.setCheckable(False)
      self.terms_check.setCheckable(True)

   def fetch_car_data(self):
      results = self.db.read("car_list", clause=None, columns=None)
      
      car_data_list = []
      for row in results:
         car_data = {
            'car_id': row[0],
            'image_path': row[12].split(';'),
            'model': row[4],
            'location': row[7],
            'price': row[9],
            'odometer': row[10],
            'transmission': row[11],
            'car_number': row[5],
            'car_availability': row[3]
         }
         car_data_list.append(car_data)

      return car_data_list
   
   def rental_user_info(self):
      ui_fname = self.lineEdit.text()
      ui_lname = self.lineEdit_2.text()
      ui_email = self.lineEdit_3.text()
      ui_num = self.lineEdit_4.text()
      card_num = self.lineEdit_5.text()
      exp_date = self.dateEdit_2.date().toString('yyyy-MM-dd')
      cvv = self.lineEdit_6.text()

      if not all([ui_fname, ui_lname, ui_email, ui_num, card_num, exp_date, cvv]):
         QMessageBox.warning(self, "Input Error", "All fields must be filled out")
         return

      if len(cvv) != 3 or not cvv.isdigit():
         QMessageBox.warning(self, "Input Error", "CVV/CVC should be exactly 3 numbers")
         return
      
      if len(card_num) != 16 or not card_num.isdigit():
         QMessageBox.warning(self, "Input Error", "Card number should be exactly 16 numbers")
         return
      
      if len(ui_num) != 10 or not ui_num.isdigit():
         QMessageBox.warning(self, "Input Error", "Mobile number should be exactly 10 integers")
         return       
      
      if not self.validate_email(ui_email):
         QMessageBox.warning(self, "Input Error", "Invalid email address") 
         return
      
      if not self.terms_check.isChecked():
         QMessageBox.warning(self, "Input Error", "Accept the terms and condition to reserve")
         return

      QMessageBox.information(self, "Success", "Information submitted successfully")
      self.previewpdf = PDFPreviewApp(ui_fname, ui_lname, ui_email, ui_num, self.car_price, self.tax, self.total_fee)
      self.show_garage_page()
      self.reset()

   def protection_page_info(self):
      # Count the number of checked checkboxes
      checked_count = sum([
         self.pack1_check.isChecked(),
         self.pack2_check.isChecked(),
         self.pack3_check.isChecked()
      ])
      
      # Check if no checkboxes are checked
      if checked_count == 0:
         QMessageBox.warning(self, "Checkable Error", "Check one of the check boxes to proceed")
      
      # Check if more than one checkbox is checked
      elif checked_count > 1:
         QMessageBox.warning(self, "Checkable Error", "You can only check one checkbox at a time") 

      else:
         self.checkout_page()
         self.reset()

      

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
