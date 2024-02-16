import os
import string
from email import message_from_file
from email.header import decode_header
from email.utils import parsedate
import base64
import re
import msvcrt  # Modul for keyboard manipulation for Windows.

def decode_subject(subject):
    decoded, encoding = decode_header(subject)[0]
    if encoding is not None:
        return decoded.decode(encoding)
    else:
        return decoded

def clean_filename(filename):
    # Delete invalid characters.
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return cleaned_filename

def get_unique_filename(output_folder, cleaned_filename):
    base, extension = os.path.splitext(cleaned_filename)
    index = 1
    new_filename = f"{base}{extension}"
    new_path = os.path.join(output_folder, new_filename)
    while os.path.exists(new_path):
        new_filename = f"{base} ({index}){extension}"
        new_path = os.path.join(output_folder, new_filename)
        index += 1
    return new_filename

def extract_attachments(eml_path, output_folder):
    success_count = 0
    error_count = 0
    errors = []

    with open(eml_path, 'r', encoding='utf-8', errors='ignore') as eml_file:
        msg = message_from_file(eml_file)

        subject = decode_subject(msg.get('Subject', 'No Subject'))
        date = parsedate(msg.get('Date', ''))

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                decoded_filename = decode_subject(filename)
                cleaned_filename = clean_filename(decoded_filename)
                
                output_folder_path = output_folder
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                attachment_path = os.path.join(output_folder_path, cleaned_filename)
                attachment_path = get_unique_filename(output_folder_path, attachment_path)

                try:
                    with open(attachment_path, 'wb') as attachment_file:
                        if part.get('Content-Transfer-Encoding', '').lower() == 'base64':
                            attachment_file.write(base64.b64decode(part.get_payload()))
                        else:
                            attachment_file.write(part.get_payload())
                    print(f"Attachment '{cleaned_filename}' saved successfully.")
                    success_count += 1
                except Exception as e:
                    errors.append((cleaned_filename, eml_path))
                    error_count += 1

    return success_count, error_count, errors

def process_folder(eml_folder, output_folder):
    eml_files = [f for f in os.listdir(eml_folder) if f.endswith('.eml')]
    
    total_success_count = 0
    total_error_count = 0
    all_errors = []

    for eml_file in eml_files:
        eml_path = os.path.join(eml_folder, eml_file)
        try:
            success_count, error_count, errors = extract_attachments(eml_path, output_folder)
            total_success_count += success_count
            total_error_count += error_count
            all_errors.extend(errors)
        except Exception as e:
            print(f"Error processing '{eml_file}': {e}")

    return total_success_count, total_error_count, all_errors

if __name__ == "__main__":
    while True:
        eml_folder = input("Enter the path to the folder containing EML files: ")
        output_folder = r"C:\Users\YOURNAME\Documents\EML\OUTPUT"  # Change the OUTPUT FOLDER here. <------------

        total_success_count, total_error_count, all_errors = process_folder(eml_folder, output_folder)

        print("\nAttachments have been extracted.")
        print(f"Report of unsuccessful attachments:")
        for error in all_errors:
            print(f"Error saving attachment '{error[0]}' in file '{error[1]}'")
        print(f"\nTotal successful extractions: {total_success_count}")
        print(f"Total unsuccessful extractions: {total_error_count}")

        print("Press Enter to restart or press ESC to close the console.")
        
        # keys
        key = msvcrt.getch()
        if key == b'\r':
            continue
        elif key == b'\x1b':
            break
