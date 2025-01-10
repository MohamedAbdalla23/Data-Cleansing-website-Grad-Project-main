import pandas as pd
import csv
import re
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import phonenumbers
from validate_email_address import validate_email

def validate_email_custom(email):
    return validate_email(email)

def validate_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed_phone)
    except phonenumbers.NumberParseException:
        return False

def normalize_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return 'Invalid'

def validate_name(name):
    pattern = r"^[a-zA-Z\s'-]+$"
    return re.match(pattern, name) is not None

def process_csv(file_path):
    original_data = []
    cleaned_data = []
    invalid_count = 0
    total_count = 0

    with open(file_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        for row in reader:
            total_count += 1
            original_row = row.copy()

            # Dynamic validation based on the presence of specific fields
            if 'email' in row:
                email = row['email'].strip()
                if not validate_email_custom(email):
                    row['email'] = 'Invalid'
                    invalid_count += 1

            if 'phone' in row:
                phone = row['phone'].strip()
                if not validate_phone(phone):
                    row['phone'] = 'Invalid'
                    invalid_count += 1

            if 'name' in row:
                name = row['name'].strip()
                if not validate_name(name):
                    row['name'] = 'Invalid'
                    invalid_count += 1

            original_data.append(original_row)
            cleaned_data.append(row)

    invalid_percentage = (invalid_count / (total_count * len(fieldnames))) * 100 if total_count > 0 else 0
    plot_url = create_invalid_format_chart(invalid_percentage)

    return fieldnames, original_data, cleaned_data, invalid_count, total_count, plot_url

def create_invalid_format_chart(invalid_percentage):
    plt.figure(figsize=(5, 5))
    plt.pie([invalid_percentage, 100 - invalid_percentage], labels=['Invalid', 'Valid'], colors=['red', 'green'], autopct='%1.1f%%')
    plt.title('Invalid Format Percentage')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    plot_url = base64.b64encode(image_png).decode('utf-8')
    return plot_url

def handle_invalid_format(file, upload_folder):
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    fieldnames, original_data, cleaned_data, invalid_count, total_count, plot_url = process_csv(file_path)
    os.remove(file_path)
    return fieldnames, original_data, cleaned_data, invalid_count, total_count, plot_url
