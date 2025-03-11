import os
import pandas as pd
import smtplib
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["TEMPLATE_FOLDER"] = "static/"
app.config["SECRET_KEY"] = "your_secret_key"  # For form security

EMAIL_SENDER = "krushanakumbhar314@gmail.com"
EMAIL_PASSWORD = "owxd jvyo zycb dpta" # Your email password

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Function to generate a certificate
def generate_certificate(name, template_path, output_file):
    width, height = A4
    pdf = canvas.Canvas(output_file, pagesize=landscape(A4))

    # Add template as background
    pdf.drawImage(template_path, 0, 0, width, height)

    # Add recipient's name
    pdf.setFont("Helvetica-Bold", 35)
    pdf.drawCentredString(width / 2, height - 350, name)

    # Add the date
    pdf.setFont("Helvetica", 20)
    date_str = datetime.now().strftime("%d %B %Y")
    pdf.drawCentredString(width / 2, height - 450, f"Date: {date_str}")

    pdf.save()

# Function to send email with certificate
def send_email(recipient_email, recipient_name, certificate_path):
    msg = EmailMessage()
    msg["Subject"] = "Your Certificate of Achievement"
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg.set_content(f"Dear {recipient_name},\n\nCongratulations! Please find your certificate attached.\n\nBest regards,\nYour Organization")

    with open(certificate_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(certificate_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    
    print(f"Email sent to {recipient_email}")

# Route for file upload
@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        excel_file = request.files["excel"]
        template_file = request.files["template"]
        x_position = float(request.form["x_position"])
        y_position = float(request.form["y_position"])


        if excel_file and template_file:
            excel_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(excel_file.filename))
            template_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(template_file.filename))

            excel_file.save(excel_path)
            template_file.save(template_path)

            df = pd.read_excel(excel_path)

            for _, row in df.iterrows():
                name = row["Name"]
                email = row["Email"]
                cert_filename = f"{app.config['UPLOAD_FOLDER']}certificate_{name.replace(' ', '_')}.pdf"

                generate_certificate(name, template_path, cert_filename, x_position, y_position)
                send_email(email, name, cert_filename)

            return render_template("success.html")

    return render_template("index.html")

# Function to generate a certificate with custom positioning
def generate_certificate(name, template_path, output_file, x_position, y_position):
    width, height = A4
    pdf = canvas.Canvas(output_file, pagesize=landscape(A4))

    pdf.drawImage(template_path, 0, 0, width, height)

    pdf.setFont("Helvetica-Bold", 35)
    pdf.drawCentredString(x_position, y_position, name)  # Use dragged position

    pdf.save()


if __name__ == "__main__":
    app.run(debug=True)
