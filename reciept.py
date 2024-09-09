import os
import webbrowser
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDFPreviewApp(QWidget):
    def __init__(self, fname, lname, email, num, car_price, tax, total_fee):
        super().__init__()

        self.fname = fname
        self.lname = lname
        self.email = email
        self.num = num
        self.car_price = car_price
        self.tax = tax
        self.total_fee = total_fee

        self.initUI()

    def initUI(self):
        self.button = QPushButton("Preview Receipt", self)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; /* Blue color */
                color: white;              /* White text */
                border: none;              /* No border */
                padding: 10px 20px;        /* Padding inside the button */
                border-radius: 5px;        /* Rounded corners */
                font-size: 16px;           /* Font size */
            }
            QPushButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
            }
        """)

        self.setGeometry(100, 100, 300, 100)
        self.button.clicked.connect(self.preview_pdf)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.setWindowTitle("Preview")
        self.show()

    def generate_pdf(self, file_path):
        # Generate the PDF using reportlab
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # Add content to the PDF
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 100, "EZDrive Car Rental Reservation details")

        c.setFont("Helvetica", 12)
        c.drawString(100, height - 130, self.fname.title())
        c.drawString(200, height - 130, self.lname.title())
        c.drawString(100, height - 150, self.email)
        c.drawString(100, height - 170, self.num)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 250, "Payments details")

        c.setFont("Helvetica", 12)
        c.drawString(100, height - 280, "Car rental fee")
        c.drawString(100, height - 300, "Taxes and fees")
        c.drawString(100, height - 320, "Other")

        c.drawString(300, height - 280, f"GHS{self.car_price:,}")
        c.drawString(300, height - 300, f"GHS{self.tax:,}")
        c.drawString(300, height - 320, "-")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 380, "Total")
        c.drawString(300, height - 380, f"GHS{self.total_fee:,}")

        c.setFont("Helvetica", 12)
        c.drawString(100, height - 420, "Paid")
        c.drawString(100, height - 450, "The total price includes all the mandatory taxes and fees")

        c.drawString(300, height - 420, f"GHS{self.total_fee:,}")


        c.setFont("Helvetica", 10)
        c.drawString(100, height - 480, "Expedia support")
        c.drawString(100, height - 500, "Contact  Expedia support if need help managing this itinenary.")
        c.drawString(100, height - 520, "(@ezdrivegh@gmail.com)")


        # Save the PDF
        c.save()

    def preview_pdf(self):
        # Generate the PDF in a temporary location
        temp_pdf_path = os.path.join(os.path.expanduser("~"), "temp_invoice.pdf")
        self.generate_pdf(temp_pdf_path)
        

        # Open the PDF in the default web browser
        webbrowser.open_new(temp_pdf_path)

        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = PDFPreviewApp()
    app.exec()
