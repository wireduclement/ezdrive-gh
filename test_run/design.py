import sys, os
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QDialog, QFrame, QSpacerItem, QSizePolicy, QGridLayout
from PyQt6.QtGui import QPixmap, QMouseEvent, QCursor
from PyQt6.QtCore import Qt, QEvent

class ImagePopup(QDialog):
    def __init__(self, image_list):
        super().__init__()
        self.image_list = image_list
        self.current_image = 0
        self.initUI()

    def initUI(self):
        # Main Layout as a Grid
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        # Frame that covers the entire grid with faded black background
        full_frame = QFrame(self)
        full_frame.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        full_frame.setLayout(grid_layout)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(full_frame)

        # Close Button
        close_button = QPushButton("X", self)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border-radius: 15px;")
        close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_button.clicked.connect(self.close)
        grid_layout.addWidget(close_button, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Main Image Display
        image_frame = QFrame(self)
        image_frame.setStyleSheet("background-color: transparent; border-radius: 10px; padding: 20px;")
        grid_layout.addWidget(image_frame, 1, 1, 3, 1)

        image_layout = QVBoxLayout(image_frame)
        self.image_label = QLabel(image_frame)
        self.image_label.setFixedSize(600, 400)
        self.image_label.setStyleSheet("border: 2px solid transparent;")
        self.update_image()
        image_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Forward and Backward Navigation Arrows
        prev_button = QPushButton("<", self)
        prev_button.setFixedSize(50, 50)
        prev_button.clicked.connect(self.show_previous_image)
        prev_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border-radius: 25px;")
        prev_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        grid_layout.addWidget(prev_button, 2, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        next_button = QPushButton(">", self)
        next_button.setFixedSize(50, 50)
        next_button.clicked.connect(self.show_next_image)
        next_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border-radius: 25px;")
        next_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        grid_layout.addWidget(next_button, 2, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Thumbnail Display
        self.thumbnail_layout = QHBoxLayout()
        self.thumbnails = []
        self.thumbnail_highlight_box = QLabel(self)
        self.thumbnail_highlight_box.setFixedSize(60, 60)
        self.thumbnail_highlight_box.setStyleSheet("border: 2px solid red;")

        self.thumbnail_frame = QFrame(self)
        self.thumbnail_frame.setLayout(self.thumbnail_layout)
        self.thumbnail_frame.setFixedHeight(100)
        self.thumbnail_frame.setStyleSheet("background-color: rgba(0, 0, 0, 150); padding: 5px;")

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.thumbnail_layout.addSpacerItem(spacer)

        for i, image_path in enumerate(self.image_list):
            thumb_label = QLabel(self)
            thumb_label.setFixedSize(60, 60)
            thumb_label.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
            thumb_label.mousePressEvent = self.create_thumbnail_click_handler(i)
            self.thumbnail_layout.addWidget(thumb_label)
            self.thumbnails.append(thumb_label)

        self.thumbnail_layout.addSpacerItem(spacer)
        grid_layout.addWidget(self.thumbnail_frame, 4, 0, 1, 3)

        # Configure the popup window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(800, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.update_thumbnail_highlight()
        self.installEventFilter(self)

    def create_thumbnail_click_handler(self, index):
        def handler(event):
            self.current_image = index
            self.update_image()
            self.update_thumbnail_highlight()
        return handler

    def update_image(self):
        pixmap = QPixmap(self.image_list[self.current_image]).scaled(600, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_thumbnail_highlight(self):
        start_index = max(0, self.current_image - 2)
        end_index = min(len(self.image_list), start_index + 5)

        for i in range(len(self.thumbnails)):
            self.thumbnails[i].setVisible(start_index <= i < end_index)

        self.thumbnail_highlight_box.setParent(self.thumbnails[self.current_image])
        self.thumbnail_highlight_box.move(0, 0)
        self.thumbnail_highlight_box.show()

    def show_previous_image(self):
        if self.current_image > 0:
            self.current_image -= 1
            self.update_image()
            self.update_thumbnail_highlight()

    def show_next_image(self):
        if self.current_image < len(self.image_list) - 1:
            self.current_image += 1
            self.update_image()
            self.update_thumbnail_highlight()

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent) and source is self:
            self.close()
            return True
        return super().eventFilter(source, event)

class CarBox(QWidget):
    def __init__(self, car_data):
        super().__init__()
        self.image_list = []
        self.current_image_index = 0
        self.car_data = car_data
        self.initUI()

    def initUI(self):
        # Frame that covers the entire grid with a border and rounded corners
        frame = QFrame(self)
        frame.setObjectName("outerFrame")  # Set an object name to target with stylesheet
        frame.setStyleSheet("""
            #outerFrame {
                border: 2px solid #A9A9A9;  /* Border color */
                border-radius: 10px;  /* Rounded corners */
                padding: 5px;  /* Padding inside the frame */
            }
        """)

        # Main Layout as a Grid inside the frame
        main_layout = QGridLayout(frame)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Padding of 5px around the grid
        main_layout.setSpacing(10)  # Spacing between the grid items

        # Image Box (First Column)
        self.img_label = QLabel(self)
        self.img_label.setFixedSize(150, 110)
        self.img_label.setScaledContents(True)
        self.img_label.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.img_label, 0, 0, 3, 1)  # Span 3 rows, 1 column

        # Information Box (Second Column)
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel(self)
        self.location_label = QLabel(self)
        # self.condition_label = QLabel(self)
        self.reserve_label = QLabel(self)
        self.odometer_label = QLabel(self)
        self.transmission_label = QLabel(self)
        self.car_number_label = QLabel(self)
        self.availability_label = QLabel(self)

        # Add word wrap to all labels in the information box
        labels = [
            self.title_label, self.location_label, self.reserve_label, self.odometer_label, 
            self.transmission_label, self.car_number_label, self.availability_label
        ]
        for label in labels:
            label.setWordWrap(True)
            label.setFixedWidth(500)  # Set a fixed width for the labels

        self.info_layout.addWidget(self.title_label)
        # self.info_layout.addWidget(self.condition_label)
        self.info_layout.addWidget(self.location_label)
        self.info_layout.addWidget(self.reserve_label)
        self.info_layout.addWidget(self.odometer_label)
        self.info_layout.addWidget(self.transmission_label)
        self.info_layout.addWidget(self.car_number_label)
        self.info_layout.addWidget(self.availability_label)

        info_widget = QWidget()
        info_widget.setLayout(self.info_layout)
        main_layout.addWidget(info_widget, 0, 1, 3, 1)  # Span 3 rows, 1 column

        # Status Box (Third Column with its own internal grid)
        status_layout = QGridLayout()
        
        status_label = QLabel("Status", self)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        available_label = QLabel("Available", self)
        available_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text

        # "Select" Button with styling
        self.select_button = QPushButton("Select", self)
        self.select_button.setFixedSize(80, 30)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;  /* Red background */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton::hover {
                background-color: #CC0000;  /* Darker red on hover */
            }
            QPushButton::pressed {
                background-color: #990000;  /* Even darker red on press */
            }
        """)
        # self.select_button.clicked.connect(lambda: print("clicked"))

        # Add widgets to the status layout
        status_layout.addWidget(status_label, 0, 0)
        status_layout.addWidget(available_label, 1, 0)
        status_layout.addWidget(self.select_button, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)


        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        main_layout.addWidget(status_widget, 0, 2, 3, 1)  # Span 3 rows, 1 column

        # Center the entire car box frame within its parent layout
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(frame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(outer_layout)
        self.setFixedHeight(200)

    def update_content(self, car_data):
      self.title_label.setText(car_data['model'].upper())
      self.location_label.setText(f"LOCATION: {car_data['location']}")
      self.reserve_label.setText(f"PRICE: GH₵{car_data['price']:,}")
      self.odometer_label.setText(f"ODOMETER: {car_data['odometer']} KM")
      self.transmission_label.setText(f"TRANSMISSION: {car_data['transmission']}")
      self.car_number_label.setText(f"CAR NUMBER: {car_data['car_number']}")
      self.availability_label.setText(f"CAR AVAILABILITY: {car_data['car_availability']}")
      self.image_list = car_data['image_path']
      self.current_image_index = 0 
    #   formatted_price = "{:,}".format(int(price))

      if self.image_list:  # Check if the image_list is not empty
         image_path = self.image_list[self.current_image_index]
        #  print(f"Loading image from {image_path}")

         # Check if the file exists
         if os.path.exists(image_path):
            # print(f"File {image_path} exist")
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
               self.img_label.setPixmap(pixmap)
               self.img_label.setScaledContents(True)
               self.img_label.repaint()  # Force update of the label
            else:
            #    print(f"Failed to load image: {image_path} (Pixmap is null)")
               self.img_label.setText("Image Not Available")
               self.img_label.repaint()  # Force update of the label
         else:
            # print(f"Image path does not exist: {image_path}")
            self.img_label.setText("Image Not Available")
            self.img_label.repaint()  # Force update of the label
      else:
        #  print("Image list is empty. Displaying 'No Image Available'")
         self.img_label.setText("No Image Available")  # Handle the case where there are no images
         self.img_label.repaint()  # Force update of the label

      # Ensure image click opens the popup
      self.img_label.mousePressEvent = self.show_image_popup

    def show_image_popup(self, event):
        if self.image_list:  # Only show popup if there are images
            self.popup = ImagePopup(self.image_list)
            self.popup.exec()

class AuctionWindow(QWidget):
    def __init__(self, car_data_list, cars_per_page=2, parent_frame=None, protection_callback=None):
        super().__init__(parent_frame)
        self.car_data_list = car_data_list
        self.cars_per_page = cars_per_page
        self.current_page = 0
        self.total_pages = (len(self.car_data_list) + cars_per_page - 1) // cars_per_page
        self.parent_frame = parent_frame
        self.protection_callback = protection_callback  # Store the protection_page callback
        self.initUI()

    def initUI(self):
        if self.parent_frame:
            self.main_layout = QVBoxLayout(self.parent_frame)
        else:
            self.main_layout = QVBoxLayout(self)
        
        # Clear existing car boxes
        self.car_boxes = []

        # Add car boxes dynamically based on car_data_list
        for car_data in self.car_data_list:
            car_box = CarBox(car_data)  # Pass car data to each CarBox
            car_box.select_button.clicked.connect(lambda _, data=car_data: self.on_car_selected(data))
            
            # Add the car_box to the layout
            self.car_boxes.append(car_box)
            self.main_layout.addWidget(car_box)

        # Pagination Controls in a Grid Layout
        self.nav_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.nav_widget)

        self.page_label = QLabel("Page", self.nav_widget)

        self.prev_button = QPushButton("←", self.nav_widget)
        self.prev_button.setFixedSize(30, 30)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid red;
                color: red;
                font-size: 14px;
                border-radius: 4px;  /* Rounded corners */
            }
            QPushButton::hover {
                background-color: lightgray;  /* Optional: Change background on hover */
            }
            QPushButton::pressed {
                background-color: darkgray;  /* Optional: Change background when pressed */
            }
        """)
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.show_previous_page)

        self.page_selector = QComboBox(self.nav_widget)
        self.page_selector.addItems([str(i + 1) for i in range(self.total_pages)])
        self.page_selector.currentIndexChanged.connect(self.change_page)
        self.page_selector.setFixedSize(50, 30)
        self.page_selector.setStyleSheet("""
            QComboBox {
               background-color: white;
               border: 1px solid red;
               color: black;
               border-radius: 4px;
               padding-right: 15px; /* Space for the arrow */
               padding-left: 5px;
            }
            QComboBox::drop-down {
                width: 15px;
                background: none;
                border-left: none;
            }
            
            QComboBox::down-arrow {
                image: url(images/arrow/down-arrow.png);  /* Use the relative path */
                width: 12px;  /* Set the width of the image */
                height: 12px;  /* Set the height of the image */
                margin-top: -1px;  /* Adjust to position the arrow vertically */
                margin-right: 5px;  /* Adjust to position the arrow horizontally */
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid lightgray;
                selection-background-color: rgba(0, 0, 0, 128);  /* Dark background with faded opacity */
                color: white; /* Text color */
                min-width: 40px;
            }
        """)

        self.next_button = QPushButton("→", self.nav_widget)
        self.next_button.setFixedSize(30, 30)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid red;
                color: red;
                font-size: 14px;
                border-radius: 4px;  /* Rounded corners */
            }
            QPushButton::hover {
                background-color: lightgray;  /* Optional: Change background on hover */
            }
            QPushButton::pressed {
                background-color: darkgray;  /* Optional: Change background when pressed */
            }
        """)
        self.next_button.setEnabled(self.total_pages > 1)
        self.next_button.clicked.connect(self.show_next_page)

        self.total_pages_label = QLabel(f"of {self.total_pages}", self.nav_widget)
        self.total_pages_label.setStyleSheet("padding-left: 1px;")  # Adjust padding to bring next button closer

        # Add widgets to the grid layout
        self.grid_layout.addWidget(self.page_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(self.prev_button, 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(self.page_selector, 0, 2, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(self.total_pages_label, 0, 3, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(self.next_button, 0, 4, Qt.AlignmentFlag.AlignLeft)

        # Add the nav widget to the main layout, aligned to the lower left
        self.main_layout.addWidget(self.nav_widget, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(self.main_layout)
        self.setWindowTitle('Auction Listings')
        self.update_display()

    def on_car_selected_and_protection(self, car_data):
        car_price = car_data.get('price', 'Unknown')
        
        # Call the protection_page callback
        if self.protection_callback:
            self.protection_callback(car_price)

    def update_display(self):
        start_index = self.current_page * self.cars_per_page
        end_index = min(start_index + self.cars_per_page, len(self.car_data_list))
        for i, car_box in enumerate(self.car_boxes):
            if start_index + i < end_index:
                car_data = self.car_data_list[start_index + i]
                car_box.update_content(car_data)
                
                # Disconnect any existing signals to avoid multiple connections
                try:
                    car_box.select_button.clicked.disconnect()
                except TypeError:
                    pass  # No connections to disconnect

                # Connect the select_button with the correct car_data
                car_box.select_button.clicked.connect(lambda _, data=car_data: self.on_car_selected_and_protection(data))
                car_box.show()
            else:
                car_box.hide()

    def change_page(self, index):
        self.current_page = index
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)
        self.update_display()

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.page_selector.setCurrentIndex(self.current_page)
            self.update_display()

    def show_next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_selector.setCurrentIndex(self.current_page)
            self.update_display()

if __name__ == '__main__':
   app = QApplication(sys.argv)

   # Example car data list
   car_data_list = [
      {
         'image_path': ["images/user_1/img1.jpg", "images/user_1/img2.jpg", "images/user_1/img3.jpg", 
                        "images/user_1/img4.jpg", "images/user_1/img5.jpg", "images/user_1/img6.jpg", 
                        "images/user_1/img7.jpg"],
         'model': '2018 TOYOTA COROLLA SE 4D SEDAN FWD 2.5L',
         'location': 'Tema Newtown',
         'price': '$13,500',
         'reserve': '$14,000',
         'odometer': '45,500 KM',
         'transmission': '4 Cylinder',
         'car_number': 'No Issues Reported',
         'car_availability': 'Automatic, Power Windows, Power Locks, 4 Doors, Leather, AC, Cruise',
      }]

   ex = AuctionWindow(car_data_list, cars_per_page=3)
   ex.show()
   sys.exit(app.exec())