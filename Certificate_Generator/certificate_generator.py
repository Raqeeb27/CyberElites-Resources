try:
    from PyPDF2 import PdfWriter, PdfReader
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    print("This script requires the 'reportlab' and 'PyPDF2' modules.\nPlease install them using \'pip install reportlab PyPDF2\' and try again.")
    exit(1)
import os


## ===========================================================================
### Functions

# Function to get list of files with specific extension within a directory
def get_files(directory, extension):
    """
    Retrieves a list of files with a given extension from the specified directory.

    Args:
        directory (str): The directory path to search for files.
        extension (str): The file extension to filter by (e.g., 'pdf', 'txt').

    Returns:
        list: A list of filenames with the specified extension in the given directory.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    
    pdf_files = [file for file in os.listdir(directory) if file.endswith(f'.{extension.lower()}')]
    return pdf_files

## --------------------------------------------------------------------------
# Function to select desired font
def select_font():
    """
    Prompts the user to select a TrueType font from the available fonts in the FONTS_DIRECTORY_PATH.

    Returns:
        str: The filename of the selected font.

    Raises:
        SystemExit: If the user input is invalid or an exception occurs.
    """
    
    font_dict = {}
    truetype_font_files = get_files(FONTS_DIRECTORY_PATH, 'TTF')
    
    if len(truetype_font_files) < 1:
        print(f"\nNo fonts available in \"Fonts\" directory.\nPlease add any TTF files to Fonts directory and try again\n\nExiting....\n")
        exit(1)

    print("\nSelect a font for the Names:")
    for index, font_name in enumerate(truetype_font_files):
        print(f"{index + 1}. {font_name[:-4]}")
        font_dict[index + 1] = font_name
    try:
        font = int(input("\n--> "))
        font_file = font_dict[font]
    except:
        print("\nInvalid Input! Please select correct font index.\n\nExiting...\n")
        exit(1)

    return font_file

## --------------------------------------------------------------------------
# Function to get the correct file for certificate genetation
def get_single_file(directory_name, directory, extension):
    """
    Ensures there is a single file with the specified extension in the directory.
    Exits the program if there are none or multiple files.

    Args:
        directory_name (str): The name of the directory (for error messages).
        directory (str): The directory to search for the file.
        extension (str): The file extension to search for.

    Returns:
        str: The single file name with the specified extension.
    """
    
    files = get_files(directory, extension)
    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        print(f"\nCannot read multiple {extension.upper()} files.")
    else:
        print(f"\nFailed to read from {extension.upper()} file.")
        
    print(f"Please provide a single {extension.upper()} file within the \"{directory_name}\" directory.\n\nExiting....\n")
    exit(1)

## --------------------------------------------------------------------------
# Function to read the contents of the file
def read_wordlist(file_path):
    """
    Reads the contents of a wordlist file, returning a list of lines.

    Args:
        file_path (str): The path to the wordlist file.

    Returns:
        list: A list of lines read from the file, or an empty list if the file does not exist.
    """
    
    try:
        with open(file_path, 'r') as file:
            contents = file.readlines()
        return contents
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return []

## --------------------------------------------------------------------------
# Function to generate the certificates with appropriate names
def create_certificate(template_file_path, wordlist_file_path, position, font_path, font_size, font_color):
    """
    Creates certificates by merging names from a wordlist with a template PDF.

    Args:
        template_file_path (str): Path to the template PDF file.
        wordlist_file_path (str): Path to the wordlist file containing names.
        position (tuple): (x, y) coordinates for text placement.
        font_path (str): Path to the custom font file.
        font_size (int): Font size for the names.
        font_color (str): Hex color code for the font color.
    """
    
    # Register the custom font
    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
    
    # Read and print the contents of the file
    wordlist_contents = read_wordlist(wordlist_file_path)
    
    # Define a single temporary file path
    tmp_file = os.path.join(TEMPORARY_DIRECTORY_PATH, "tmp_certificate.pdf")

    for name in wordlist_contents:
        name = name.strip()
        if not name:
            continue
        
        filename = "_".join(name.split())

        # Create a canvas and set the custom font, size, and color
        new_canvas = canvas.Canvas(tmp_file, pagesize=landscape(A4))
        new_canvas.setFont('CustomFont', font_size)
        new_canvas.setFillColor(HexColor(font_color))
        
        # Calculate the width of the name text
        text_width = pdfmetrics.stringWidth(name, 'CustomFont', font_size)
        
        # Calculate the x position to center the text
        centered_x = position[0] - (text_width / 2)
        
        # Draw the name centered at the given position
        new_canvas.drawString(centered_x, position[1], name)
        new_canvas.save()

        # Merge the canvas with the template
        packet = open(tmp_file, "rb")
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(template_file_path, "rb"))
        output = PdfWriter()

        # Add the "watermark" (the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        with open(f"{OUTPUT_DIRECTORY_PATH}/{filename}_certificate.pdf", "wb") as outputStream:
            output.write(outputStream)
        
        # Clear the canvas for the next iteration (Certificate)
        new_canvas = None

### ===========================================================================
## Main 
#

if __name__ == "__main__":
    
    if os.getcwd()[-9:] == "Resources":
        CERTIFICATE_GENERATOR_DIRECTORY_PATH = os.path.join(os.getcwd(), 'Certificate_Generator')
        
    elif os.getcwd()[-21:] == "Certificate_Generator":
        CERTIFICATE_GENERATOR_DIRECTORY_PATH = os.getcwd()
        
    else:
        print("\nPlease change your working directory to the main repository.\n\nExiting...\n")
        exit(1)
    
    FONTS_DIRECTORY_PATH = os.path.join(CERTIFICATE_GENERATOR_DIRECTORY_PATH, 'Fonts')
    TEMPLATE_DIRECTORY_PATH = os.path.join(CERTIFICATE_GENERATOR_DIRECTORY_PATH, 'Certificate_Template')
    WORDLIST_DIRECTORY_PATH = os.path.join(CERTIFICATE_GENERATOR_DIRECTORY_PATH, 'Wordlist')
    TEMPORARY_DIRECTORY_PATH = os.path.join(CERTIFICATE_GENERATOR_DIRECTORY_PATH, 'tmp')
    OUTPUT_DIRECTORY_PATH = os.path.join(CERTIFICATE_GENERATOR_DIRECTORY_PATH, 'Generated_Certificates')
    
    print("\n" + " Certificate Generator ".center(35, "-"))

    font_file = select_font()
    font_file_path = os.path.join(FONTS_DIRECTORY_PATH, font_file)

    os.makedirs(TEMPLATE_DIRECTORY_PATH, exist_ok=True)
    os.makedirs(WORDLIST_DIRECTORY_PATH, exist_ok=True)
    
    pdf_files = get_files(TEMPLATE_DIRECTORY_PATH, 'PDF')
    template_file = get_single_file('Certificate_Template', TEMPLATE_DIRECTORY_PATH, 'PDF')
    template_file_path = os.path.join(TEMPLATE_DIRECTORY_PATH, template_file)

    text_files = get_files(WORDLIST_DIRECTORY_PATH, 'TXT')
    wordlist_file = get_single_file('Wordlist', WORDLIST_DIRECTORY_PATH, 'TXT')
    wordlist_file_path = os.path.join(WORDLIST_DIRECTORY_PATH, wordlist_file)

    os.makedirs(TEMPORARY_DIRECTORY_PATH, exist_ok=True)
    os.makedirs(OUTPUT_DIRECTORY_PATH, exist_ok=True)
    
    font_size = 50
    font_color = "#55D3E2"
    position = (420, 375)

    create_certificate(template_file_path, wordlist_file_path, position, font_file_path, font_size, font_color)
    
    print("\nCertificates generation successfull!\n\nSaved all certificates to \"Generated_Certificates\" directory\n")
