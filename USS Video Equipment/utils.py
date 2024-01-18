# utils.py
import tkinter as tk
from tkinter import font as tkFont  # Add this line to import the font module
from PIL import Image, ImageTk
import os
import webbrowser

def open_hyperlink(url):
    """
    Opens a hyperlink in the default web browser.

    :param url: URL to be opened.
    """
    webbrowser.open(url)

def get_column_index(cursor, column_name):
    """
    Gets the index of a column in a database cursor's description.

    :param cursor: Database cursor.
    :param column_name: Name of the column.
    :return: Index of the column or None.
    """
    for i, col_info in enumerate(cursor.description):
        if col_info[0] == column_name:
            return i
    return None

def initialize_fonts():
    """
    Initializes and returns fonts for the application.

    :return: Tuple of (bold_font, value_font).
    """
    heading_font = tkFont.Font(family="Helvetica", size=14, weight="bold", underline=1)
    bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
    value_font = tkFont.Font(family="Helvetica", size=12)
    return heading_font, bold_font, value_font

def display_image(image_frame, item_name):
    """
    Displays an image in the specified frame. Clears the previous image if any.

    :param image_frame: Frame where the image is to be displayed.
    :param item_name: Name of the item whose image is to be displayed.
    """
    # Clear the previous image
    for widget in image_frame.winfo_children():
        widget.destroy()
        
    found_image = False
    for extension in ['.png', '.jpg']:
        image_path = os.path.join('Pics', f'{item_name}{extension}')
        if os.path.exists(image_path):
            found_image = True
            break
        
    if found_image:
        try:
            image = Image.open(image_path)
            max_size = 400
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(image_frame, image=photo, anchor="w")
            image_label.image = photo
            image_label.grid(row=0, column=0, sticky='w')
        except Exception as e:
            print(f"Error displaying image: {e}")
            error_label = tk.Label(image_frame, text="Error displaying image", anchor="w")
            error_label.grid(row=0, column=0, sticky='w')
    else:
        no_image_label = tk.Label(image_frame, text="No Image Available", anchor="w")
        no_image_label.grid(row=0, column=0, sticky='w')
        
        
