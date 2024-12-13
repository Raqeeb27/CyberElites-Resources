import csv
import logging
import os
from email import encoders
from email.mime.base import MIMEBase


default_html_code = """<!-- <html>
    <body>
        <p><strong>Hello {{name}}</strong>,</p>
        <p>Here's the link to club website <em><a href="https://cyberelites.org" target="_blank">CyberElites</a></em>. Explore more about us here.</p>
        <p>Thank you for being part of our community!</p>
        <p>Best regards,<br><strong>CyberElites Club</strong></p>
    </body>
</html> -->
"""

## ===========================================================================
### Functions

def add_attachment(msg, attachment_path):
    """
    Attaches a file to an email message.

    Args:
        msg (email.mime.multipart.MIMEMultipart): The email message object to which the file will be attached.
        attachment_path (str): The file path of the attachment.

    Returns:
        None

    Raises:
        FileNotFoundError: Logs an error if the file is not found and displays an error message.
    """

    try:
        attachment = MIMEBase("application", "octet-stream")
        with open(attachment_path.strip(), "rb") as file:
            attachment.set_payload(file.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )
        msg.attach(attachment)
    except FileNotFoundError:
        logging.error(f"Attachment not found: {attachment_path}")
        print(f"Attachment not found: {attachment_path}")


def check_attachments(csv_file_path, attachments_dir_path=None, attachment_mode=None, automation_dir_path=None):
    """
    Validates the presence of attachments as specified in a CSV file based on the selected attachment mode.

    Args:
        csv_file_path (str): Path to the CSV file containing attachment details.
        attachments_dir_path (str, optional): Directory path where attachments are stored.
        attachment_mode (str, optional): Mode of attachment ("Common", "Respective", "Other").
        automation_dir_path (str, optional): Directory path for automation-specific files.

    Returns:
        None

    Exits:
        Exits the program if attachments are missing or improperly specified.
    """

    with open(csv_file_path, "r", encoding="utf-8") as csv_file:
        csv_file.seek(0)  # Reset file pointer
        reader = csv.DictReader(csv_file)
        is_missing = False
        
        # Read the common attachments if needed
        if attachment_mode == "Common":
            first_row = next(reader, None)
            if first_row:
                if first_row["Attachments"]:
                    common_attachments = (first_row["Attachments"].split(";"))
                else:
                    print(f"\nThe first row attachment is not specified for the selected Attachment Mode \'Common\'\n")
                    exit(1)
                for attachment in common_attachments:
                    if not attachment or attachment.strip() == "":
                        is_missing = True
                        print(f"\nThe first row attachment is not specified for the selected Attachment Mode \'Common\'")
                    attachment_path = os.path.join(attachments_dir_path, attachment)
                    if not os.path.exists(attachment_path):
                        is_missing = True
                        print(f"\nCommon attachment of first row not found - {attachment}")
                        
        elif attachment_mode == "Respective":
            missing_files =[]
            for row_index, row in enumerate(reader, start=2):
                if row.get("Attachments", ""):
                    attachments = row.get("Attachments", "").split(";")
                    missing_files = [path.strip() for path in attachments if path.strip() and not os.path.exists(os.path.join(attachments_dir_path,path.strip()))]
                else:
                    attachments = []
                    
                if missing_files:
                    is_missing = True                    
                    print(f"Attachment not found - Row Index \'{row_index}\' - {missing_files}")
        
        elif attachment_mode == "Other":
            for row_index, row in enumerate(reader, start=2):
                name = row.get("Full Name", "").title().strip()
                attachments = f"{name.title().strip().replace(' ', '_')}_certificate.pdf"
                
                gen_certs_dir_path = os.path.join(automation_dir_path, "gen_certs_dir_path.txt")
                with open(gen_certs_dir_path, "r") as file:
                    gen_certs_dir_path = file.read()
                    
                attachment_path = os.path.join(gen_certs_dir_path, attachments)
                if not os.path.exists(attachment_path):
                    is_missing = True                    
                    print(f"Attachment not found: Row Index \'{row_index}\' - {attachments}")
                    
        if is_missing:
            print("\nExiting...\n")
            exit(1)


def check_body_template(body_template_path):
    """
    Verifies the validity of an HTML email body template file.

    Args:
        body_template_path (str): Path to the HTML body template file.

    Returns:
        None

    Exits:
        Exits the program if the file is empty, commented entirely, or corrupted.
    """

    try:
        with open(body_template_path, "r") as body_file:
            lines = body_file.readlines()
            lines = [line for line in lines if line.strip()]
    except:
        print("\nError in reading HTML file.\nPlease ensure that the file is not corrupted!\n\nExiting...\n")
        exit(1)
        
    if not lines:
        print("\nEmpty HTML body template file\nPlease enter valid HTML contents and check it's rendering before script execution.\n\nExiting...\n")
        exit(1)

    if all(line.lstrip().startswith("<!--") and line.rstrip().endswith("-->") for line in lines):
        print("\nEvery line is commented in HTML body template file\nPlease enter valid HTML contents and check it's rendering before script execution.\n\nExiting...\n")
        exit(1)

    if lines[0].startswith("<!--") and lines[-1].strip().endswith("-->"):
        print("\nThe body template file has contents commented.\nPlease enter valid HTML contents and check it's rendering before script execution.\n\nExiting...\n")
        exit(1)
        

def check_csv(csv_file_path, attachment_mode, additional_column=None):
    """
    Checks the integrity and content of a CSV file, ensuring required columns and data are present.

    Args:
        csv_file_path (str): Path to the CSV file.
        attachment_mode (str): The attachment mode ("Respective", "Common").
        additional_column (str, optional): Additional required column name.

    Returns:
        None

    Exits:
        Exits the program if the CSV file is missing required columns, contains invalid rows, or is corrupted.
    """

    # Open the CSV file
    with open(csv_file_path, "r", encoding="utf-8") as csv_file:
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        try:
            # Check if the file is not empty and contains rows after the header
            rows = list(reader)
        except:
            print("\nError in reading CSV file.\nEnsure that the file is not corrupted.\n\nExiting...\n")
            exit(1)
        
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        if not rows or reader.fieldnames is None:  # If rows is empty, only the header or completely empty file
            print("\nThe CSV file is either empty or only contains the header.\n")
            exit(1)

        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        required_columns = {"Full Name", "Email"}
        if additional_column:
            required_columns.add(additional_column)
        missing_columns = required_columns - set(reader.fieldnames or [])
        try:
            if missing_columns:
                raise ValueError(f"\nMissing required columns in the CSV file: {', '.join(missing_columns)}\n")

            if attachment_mode in {"Respective", "Common"} and "Attachments" not in reader.fieldnames:
                raise ValueError(f"\nThe 'Attachments' column is required for the selected ATTACHMENT_MODE i.e \'{attachment_mode}\'\n")
        except Exception as e:
            print(f"\nError:{e}")
            exit(1)
        
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        invalid_rows = []
        for row_index, row in enumerate(reader, start=2):
            if row.get("Full Name", "") is None or row.get("Email", "") is None:
                invalid_rows.append(row_index)
                continue
            if row.get("Full Name", "").strip() == "" or row.get("Email", "").strip() == "":
                invalid_rows.append(row_index)

        if invalid_rows:
            print(f"\nFull Name or Email not found in Row Index - {invalid_rows}\n")
            exit(1)


def check_gmail_app_password(gmail_app_password_file):
    """
    Validates the Gmail application password stored in a file.

    Args:
        gmail_app_password_file (str): Path to the file containing the Gmail application password.

    Returns:
        str: The Gmail application password.

    Exits:
        Exits the program if the password file is missing, corrupted, or contains invalid data.
    """

    try:
        # Read the names from the file
        with open(gmail_app_password_file, 'r') as file:
            lines = file.readlines()
            password = [line.strip() for line in lines if line.strip()]
            if len(password) != 1 or password[0].count(" ") != 0:
                print("\nError in gmail app password!!\nInput password in a single line and without any spaces.\n\nExiting...\n")
                exit(1)
        return password[0]
            
    except FileNotFoundError:
        print("\nError in reading password file!\nPlease ensure that the file exists at correct location.\n\nExiting...\n")
        exit(1)
    except Exception as e:
        print(f"\nError in reading password file!\n{e}\nPlease ensure that the file is not corrupted.\n\nExiting...\n")
        exit(1)


# Function to get list of files with specific extension within a directory
def get_files(directory, extension):
    """
    Retrieves a list of files with a specified extension from a directory.

    Args:
        directory (str): Directory path to search for files.
        extension (str): File extension to filter (e.g., 'pdf', 'txt').

    Returns:
        list: List of filenames with the specified extension.

    Raises:
        FileNotFoundError: Displays an error message if the directory does not exist.
    """
    
    try:
        files_list = [file for file in os.listdir(directory) if file.endswith(f'.{extension.lower()}')]
    except FileNotFoundError as e:
        print(f"\nError reading template file: {e}")
        exit(1)
        
    return files_list


## --------------------------------------------------------------------------
# Function to get the correct file for certificate genetation
def get_single_file(directory_name, directory, extension):
    """
    Ensures a single file with the specified extension exists in a directory.

    Args:
        directory_name (str): Name of the directory (used for error messages).
        directory (str): Path to the directory.
        extension (str): File extension to search for.

    Returns:
        str: The filename of the single file with the specified extension.

    Exits:
        Exits the program if no file or multiple files with the specified extension are found.
    """
    
    files = get_files(directory, extension)
    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        print(f"\nCannot read multiple {extension.upper()} files.")
    else:
        print(f"\nFailed to read from {extension.upper()} file.")
        
        if extension == "TXT":
            try:
                wordlist_file_path = os.path.join(directory, "wordlist.txt")
                with open(wordlist_file_path, 'w') as f:
                    pass
                print("\nCreating an empty 'wordlist.txt' file in 'Wordlist' directory, add contents to it execute the script again!\n")
            except IOError as e:
                print(f"Error creating 'wordlist.txt' file: {e}")
        
    print(f"Please provide a single {extension.upper()} file within the \"{directory_name}\" directory.\n")
    exit(1)


def initialize_necessary_files(body_template_file=None, log_file=None, gmail_app_password_file=None):
    """
    Creates necessary files if they do not already exist.

    Args:
        body_template_file (str, optional): Path to the HTML body template file.
        log_file (str, optional): Path to the log file.
        gmail_app_password_file (str, optional): Path to the Gmail application password file.

    Returns:
        None
    """

    for file in [body_template_file, log_file, gmail_app_password_file]:
        if file is None:
            continue
        if not os.path.exists(file):
            with open(file, 'w') as f:
                if file == body_template_file:
                    
                    f.write(default_html_code)


# === FUNCTION: READ EMAIL BODY TEMPLATE ===
def read_email_body_template(body_template_file):
    """
    Reads the content of an HTML email body template file.

    Args:
        body_template_file (str): Path to the HTML body template file.

    Returns:
        str: The content of the HTML body template.

    Exits:
        Exits the program if the file is corrupted or cannot be read.
    """

    try:
        with open(body_template_file, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading HTML body template file\n{e}")
        print(f"\nError reading HTML body template file\n{e}\n\nExiting...\n")
        exit(1)
        
        
## --------------------------------------------------------------------------
# Function to read the contents of the file
def read_wordlist(file_path):
    """
    Reads and validates the content of a wordlist file.

    Args:
        file_path (str): Path to the wordlist file.

    Returns:
        list: List of validated and sorted lines from the wordlist.

    Exits:
        Exits the program if the wordlist contains invalid characters or is empty.
    """
    
    forbidden_chars = set('<>\"?|/\\:*')

    names = sort_wordlist(file_path)
    
    # Check each name for forbidden characters
    line_error = False
    print()
    for line_number, line in enumerate(names, start=1):
        if any(char in forbidden_chars for char in line):
            print(f"Error: The wordlist file contains forbidden characters on - line {line_number}: ('{line.strip()}').")
            line_error = True
                    
    if line_error:
        print("Please remove any of the following characters from the wordlist: < > \" ? | / \\ : *\n\nExiting...\n")
        exit(1)
    
    if not names:
        print("\nEmpty Wordlist file!\nEnsure that Wordlist TXT files has correct Names.\n\nExiting...\n")
        exit(1)
            
    return names


## --------------------------------------------------------------------------
# Function to select desired font
def select_font(fonts_directory_path):
    """
    Prompts the user to select a TrueType font from a directory.

    Args:
        fonts_directory_path (str): Directory path containing font files.

    Returns:
        str: The filename of the selected font.

    Exits:
        Exits the program if no fonts are available or the user input is invalid.
    """
    
    font_dict = {}
    truetype_font_files = sorted(get_files(fonts_directory_path, 'TTF'))
    
    if len(truetype_font_files) < 1:
        print(f"\nNo fonts available in \"Fonts\" directory.\nPlease add any valid TTF files to Fonts directory and try again\n\nExiting....\n")
        exit(1)

    print("\nSelect a font for the Names:")
    for index, font_name in enumerate(truetype_font_files):
        print(f"  {index + 1}. {font_name[:-4]}")
        font_dict[index + 1] = font_name
    try:
        font = int(input("\n--> "))
        font_file = font_dict[font]
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt!\n\nExiting...\n")
        exit(1)
    except Exception as e:
        print("\n\nInvalid Input!\nPlease select correct font index.\n\nExiting...\n")
        exit(1)

    return font_file


## --------------------------------------------------------------------------
# Function to sort the provided wordlist file
def sort_csv(file_path):
    """
    Sorts the content of a CSV file based on the second column (or alphabetically if not applicable).

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        None

    Exits:
        Exits the program if the file is empty, corrupted, or cannot be sorted.
    """

    try:
        # Read the file and split into lines
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            rows = txt_file.readlines()
            
        # Extract header and data rows
        header = rows.pop(0).strip()
        data_rows = [row.strip() for row in rows if row.strip()]
    except Exception as e:
        print(f"\nError in reading TXT file!\nPlease ensure that the file is not corrupted.\n\nExiting...\n")
        exit(1)
        
    if not data_rows:
        print("\nEmpty CSV file!\nNo valid rows in the file to sort!\n\nExiting...\n")
        exit(1)
        
    if data_rows[0].count(",") == 1:
        sorted_data = sorted(row.strip() for row in rows if row.strip())
    else:
        sorted_data = sorted(data_rows, key=lambda row: row.split(',')[1].strip())

    # Combine header with sorted data
    sorted_rows = [header] + sorted_data
    try:

        # Overwrite the file with sorted data
        with open(file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(sorted_rows))

    except Exception as e:
        print(f"\nError sorting the file.\nMake sure that the file isn't open!\n{e}\nExiting...\n")
        exit(1)

    

## --------------------------------------------------------------------------
# Function to sort the provided wordlist file
def sort_wordlist(file_path):
    """
    Sorts the content of a wordlist file alphabetically.

    Args:
        file_path (str): Path to the wordlist file.

    Returns:
        list: List of sorted lines from the wordlist.

    Exits:
        Exits the program if the file is empty, corrupted, or cannot be sorted.
    """

    try:
        # Read the names from the file
        with open(file_path, 'r') as file:
            names = file.readlines()
    except:
        print("\nError in reading TXT wordlist!\nPlease ensure that the file is not corrupted.\n\nExiting...\n")
        exit(1)

    # Strip whitespace and sort the names
    sorted_names = sorted(name.title().strip() for name in names if name.strip())

    try:
        with open(file_path, 'w') as output_file:
            output_file.write('\n'.join(sorted_names))
    except:
        print("\nError sorting the wordlist file.\nMake sure that the file isn't open!\n\nExiting...\n")
        exit(1)

    return sorted_names 