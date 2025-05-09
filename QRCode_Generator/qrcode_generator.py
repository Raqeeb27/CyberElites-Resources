import os
import re
import sys
# Get the parent directory, add it to python path and import the modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from Utilities.utils import select_font
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from qrcode.image.styles.moduledrawers import CircleModuleDrawer
except ImportError:
    print("This script requires the 'qrcode' and 'pillow' modules.\nPlease install them using 'pip install qrcode pillow' and try again.")
    exit(1)


## ===========================================================================
### Functions

# Function to input QR text
def get_text():
    """
    Prompt the user to input the text to encode in the QR code.

    The function supports multi-line input. Input ends when the user presses
    Enter twice consecutively. If no text is provided, the program exits.

    Returns:
        str: The concatenated multi-line input text to encode in the QR code.

    Raises:
        SystemExit: If no text is provided or the user interrupts the input process.
    """

    print("\nEnter the text to encode as QR (Press Enter \'Twice\' to finish):\n")

    text_lines = []
    enter_pressed = 0

    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            print("\n\nKeyboard Interrupt!\n\nExiting....\n")
            exit(1)

        if not line:
            enter_pressed += 1
            if enter_pressed > 1:
                break
            text_lines.append("")
            continue
        else:
            enter_pressed = 0
        text_lines.append(line.rstrip())

    input_text = '\n'.join(text_lines).strip()

    if input_text.strip() == "":
        print("No Input!!!\nCan't generate QR without input text.\n")
        exit(1)

    return input_text


## --------------------------------------------------------------------------
# Function to generate QR
def standard_qr_gen(input_text, error_correction, bg_color):
    """
    Generate a standard QR code image.

    This function creates a QR code with customizable error correction levels and background colors.
    The generated QR code is resized for consistency.

    Args:
        input_text (str): Text to encode in the QR code.
        error_correction (str): Error correction level ('L', 'M', 'Q', 'H').
        bg_color (str): Background color of the QR code ('white' or 'black').

    Returns:
        PIL.Image.Image: The generated QR code image.

    Raises:
        SystemExit: If an invalid error correction level is provided.
    """

    qr = qrcode.QRCode(
        version=6,
        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
        box_size=10,
        border=2,
    )

    qr.add_data(input_text)
    qr.make(fit=True)

    fg_color = "white" if bg_color == "black" else "black"

    qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    qr_img = qr_img.resize((800, 800), Image.Resampling.LANCZOS)

    qr_image = qr_img.convert('RGB')

    return qr_image


## --------------------------------------------------------------------------
# Function to generate dotted QR
def dots_qr_gen(input_text, error_correction, bg_color):
    """
    Generate a QR code with a dotted module style.

    This function creates a visually styled QR code with circular dots for modules
    and customizable background colors.

    Args:
        input_text (str): Text to encode in the QR code.
        error_correction (str): Error correction level ('L', 'M', 'Q', 'H').
        bg_color (str): Background color of the QR code ('white' or 'black').

    Returns:
        PIL.Image.Image: The styled QR code image.
    """

    # Create a QR Code instance
    qr = qrcode.QRCode(
        version=6,              # Version controls size of QR
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )

    qr.add_data(input_text)
    qr.make(fit=True)

    # Create the QR code with dot modules
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleModuleDrawer(),  # Dots for QR code modules
        color_mask=SolidFillColorMask(front_color=(0,0,0), back_color=(255,255,255)),
    )

    qr_img = qr_img.resize((800, 800), Image.Resampling.LANCZOS)

    # Convert QR code to an editable PIL image
    qr_image = qr_img.convert("RGB")
    if bg_color == "black":
        qr_image = ImageOps.invert(qr_image)

    return qr_image


## --------------------------------------------------------------------------
# Function to get QR Image extension type
def extension_menu():
    """
    Prompt the user to select the file format for the QR code image.

    Displays a menu of options for image file extensions. Returns the selected
    extension and corresponding format.

    Returns:
        tuple: A tuple (extension, format) representing the selected file extension 
               (e.g., 'png', 'jpg') and the image format (e.g., 'PNG', 'JPEG').

    Raises:
        SystemExit: If an invalid option is selected or the user interrupts the process.
    """

    try:
        extension_type = input("\nEnter the image file extension for your QRCode\n  1. JPEG    2. JPG    3. PNG\n  4. GIF     5. TIFF   6. BMP\n  7. Exit without generating QR\n\n --> ").lower().strip()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        exit(1)

    image_format = "JPEG"

    if extension_type in ['1','jpeg','']:
        extension = 'jpeg'

    elif extension_type in ['2','jpg']:
        extension = 'jpg'

    elif extension_type in ['3','png']:
        extension = 'png'
        image_format = "PNG"

    elif extension_type in ['4','gif']:
        extension = 'gif'
        image_format = "GIF"

    elif extension_type in ['5','tiff']:
        extension = 'tiff'
        image_format = "TIFF"

    elif extension_type in ['6','bmp']:
        extension = 'bmp'
        image_format = "BMP"

    elif extension_type in ['7']:
        print("\n\nExiting...\n")
        exit(0)

    else:
        print("\nInvalid extension!!! Please select correct extension from the available options.\n")
        return None, None

    return extension, image_format


## --------------------------------------------------------------------------
# Function to add an image to the center of the QR Code
def add_center_image(qr_image, bg_color):
    """
    Overlay a center image on the QR code.

    Adds a predefined image to the center of the QR code, dynamically scaling it
    relative to the size of the QR code.

    Args:
        qr_image (PIL.Image.Image): The QR code image.
        bg_color (str): Background color of the QR code ('white' or 'black').

    Returns:
        PIL.Image.Image: The QR code image with the center image overlaid.

    Raises:
        Exception: If there is an error in adding the center image.
    """

    # try:
        # center_image_path = input("\nEnter the Full path of the image to place at the center of the QR code (or press Enter to skip): ").strip()
    # except KeyboardInterrupt:
        # print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        # exit(1)

    center_image = "White_border_circle.png" if bg_color == "white" else "White_bg_circle.png"
    center_image_path = os.path.join(LOGOS_DIRECTORY_PATH, center_image)

    if not center_image_path or center_image_path.strip() == "":
        return qr_image

    try:
        center_image = Image.open(center_image_path)
        qr_width, qr_height = qr_image.size

        # Dynamically scale center image
        scale_factor = 4 #min(4, qr_width // 75)
        center_img_width = qr_width // scale_factor
        center_img_height = qr_height // scale_factor
        center_image = center_image.resize((center_img_width, center_img_height), Image.Resampling.LANCZOS)

        # Place the center image
        pos = ((qr_width - center_img_width) // 2, (qr_height - center_img_height) // 2)
        qr_image.paste(center_image, pos, mask=center_image if center_image.mode == 'RGBA' else None)

    except Exception as e:
        print(f"\nFailed to add center image: {e}\n")

    return qr_image


## --------------------------------------------------------------------------
# Function to add a title to the QR Code
def add_title(qr_image, title, bg_color):
    """
    Add a title above the QR code.

    Creates a new image with additional space at the top for a title, which is
    centered and styled with a specified font and color.

    Args:
        qr_image (PIL.Image.Image): The QR code image.
        title (str): The text to display as the title.
        bg_color (str): Background color of the QR code ('white' or 'black').

    Returns:
        PIL.Image.Image: The QR code image with the title added.
    """

    font_file = select_font(FONTS_DIRECTORY_PATH)
    FONT_SIZE = 60
    font_file_path = os.path.join(FONTS_DIRECTORY_PATH, font_file)

    try:
        font = ImageFont.truetype(font_file_path, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(qr_image)
    title_bbox = draw.textbbox((0, 0), title, font=font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1] + 5

    fill_color = "white" if bg_color == "black" else "black"

    # Create a new image with extra space for the title
    new_image = Image.new("RGB", (qr_image.width, qr_image.height + title_height + 10), bg_color)
    draw = ImageDraw.Draw(new_image)

    # Draw the title at the top center
    text_position = ((new_image.width - title_width) // 2, 2)
    draw.text(text_position, title, fill=fill_color, font=font)

    # Paste the QR code below the title
    new_image.paste(qr_image, (0, title_height + 10))

    return new_image


## --------------------------------------------------------------------------
# Function manage all QR creation tasks
def generate_qrcode():
    """
    Manage the entire QR code creation process.

    This function handles:
    - Collecting input text from the user.
    - Selecting error correction levels and QR styles.
    - Generating the QR code with optional styling.
    - Adding an optional center image and title.
    - Saving the QR code image to a file with the selected format.

    Returns:
        str: The path to the saved QR code image.

    Raises:
        SystemExit: If any step in the process encounters an error or the user interrupts.
    """

    # Get input text from the user
    input_text = get_text()

    # Get the QR Error Correction Level
    # try:
        # error_correction = input("\nSelect Error Correction level (Low-L, Medium-M, Quartile-Q, High-H): ").upper().strip()
    # except KeyboardInterrupt:
        # print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        # exit(1)

    error_correction = "H"

    if error_correction not in ['L','M','Q','H']:
        print("\nInvalid Input! Please select from L, M, Q, H\nQR code creation failed.\n")
        exit(1)

    try:
        qr_style = int(input("Select the QR style:\n  1. Standard\n  2. Dots\n\n---> "))
        if qr_style not in [1, 2]:
            raise ValueError()

        background_color = int(input("\nSelect the QR Background color:\n  1. White\n  2. Black\n\n---> "))
        if background_color not in [1, 2]:
            raise ValueError()

    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        exit(1)
    except:
        print("\nInvalid Input!!!\nEnter the number corresponding to the style\n\nExiting....\n")
        exit(1)

    try:
        qr_func = standard_qr_gen if qr_style == 1 else dots_qr_gen
        bg_color = "black" if background_color == 2 else "white"
        qr_image = qr_func(input_text, error_correction, bg_color)
    except Exception as e:
        print(f"\nOops! There was an error in creating QR.\n{e}\n")
        exit(1)

    # Add center image to the QR code
    qr_image = add_center_image(qr_image, bg_color)

    try:
        title = input("\nEnter the title to add at the top of the QR code (or press Enter to skip): ").strip()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        exit(1)

    if title:
        qr_image = add_title(qr_image, title, bg_color)
    try:
        filename = input("\nEnter the filename for the QR code image: ").strip()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt!\n\nExiting....\n")
        exit(1)

    if re.search(FORBIDDEN_CHARS, filename):
        print("\nInvalid filename! QR code creation failed.\nFilename can't contain \\/:*?\"<>| symbols\n")
        exit(1)

    if not filename:
        filename = "qrcode"
        print("Filename not specified! Naming the file as \'qrcode\'")

    # Get the extension type
    extension, image_format = extension_menu()
    while extension is None:
        extension, image_format = extension_menu()

    os.makedirs(QRCODES_DIRECTORY_PATH, exist_ok=True)
    qr_image_path =  os.path.join(QRCODES_DIRECTORY_PATH, f"{filename}.{extension}")

    # Handle if QR Code Image has existing filename
    counter = 1
    while os.path.exists(qr_image_path):
        qr_image_path = os.path.join(QRCODES_DIRECTORY_PATH, f"{filename}({counter}).{extension}")
        counter += 1

    try:
        # Save the QR Code
        qr_image.save(qr_image_path, format=image_format)
    except Exception as e:
        print(f"\nAn Error occured while saving the QRCode file.\n{e}\n\nExiting....\n")

    return qr_image_path


### ===========================================================================
## Main
#

if __name__ == "__main__":
    """
    Main entry point for the QR Code Generator script.

    This script generates a QR code based on user input and offers various customization options:
    - Supports standard and dotted QR code styles.
    - Allows customization of error correction levels, background colors, and file formats.
    - Optionally overlays a center image and/or a title on the QR code.
    - Saves the final QR code image to a user-specified file.

    The script expects to be run from the root of the repository or within specific directories
    (Resources or QRCode_Generator). Paths are adjusted dynamically to locate resources like
    fonts, logos, and output directories.

    Raises:
        SystemExit: If an error occurs during the QR code generation process or if
                    invalid input is provided.
    """

    FORBIDDEN_CHARS = r'[\/:*?"<>|]'

    if os.getcwd()[-9:] == "Resources":
        QRCODES_GENERATOR_DIRECTORY_PATH = os.path.join(os.getcwd(), 'QRCode_Generator')
        FONTS_DIRECTORY_PATH = os.path.join(os.getcwd(), 'Fonts')

    elif os.getcwd()[-16:] == "QRCode_Generator":
        QRCODES_GENERATOR_DIRECTORY_PATH = os.getcwd()
        ROOT_REPO_PATH = os.path.join(os.getcwd(), '..')
        FONTS_DIRECTORY_PATH = os.path.join(ROOT_REPO_PATH, 'Fonts')

    else:
        print("\nPlease change your working directory to the main repository.\n\nExiting...\n")
        exit(1)

    LOGOS_DIRECTORY_PATH = os.path.join(QRCODES_GENERATOR_DIRECTORY_PATH, 'Logos')
    QRCODES_DIRECTORY_PATH = os.path.join(QRCODES_GENERATOR_DIRECTORY_PATH, 'QRCodes')

    print("\n" + " QR Code Generator ".center(29, "-"))

    qr_image_path = generate_qrcode()

    print(f"\nQR code \"{qr_image_path[len(QRCODES_GENERATOR_DIRECTORY_PATH) + 1:]}\" created successfully!\n")
