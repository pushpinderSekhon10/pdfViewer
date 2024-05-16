import fitz  # PyMuPDF
import tkinter as tk
from tkinter import *
from tkinter import ttk

from PyPDF2 import PdfReader, PdfWriter

# Define a class for our PDF viewer application
class PDFViewer:
    # Initialization method for the PDFViewer class
    def __init__(self, master, pdf_path):
        # master refers to the main window of the Tkinter application
        # pdf_path is the path to the PDF file to be displayed
        self.master = master
        self.pdf_path = pdf_path
        self.document = fitz.open(pdf_path)  # Open the PDF file using PyMuPDF
        self.page_number = 0  # Start displaying from the first page

        frm = tk.Frame(master, width="1000", height="1000", bd="10",bg="#6FEA99")
        frm.pack()
        # Setup a label widget for displaying the current page number
        self.page_label = Label(master, text="")
        self.page_label.pack()  # Pack the label widget into the master widget

        # Setup a label widget for displaying the image of the PDF page
        self.image_label = Label(master)
        self.image_label.pack()  # Pack the image label into the master widget

        # Setup a button for navigating to the previous page
        btn_prev = Button(frm, text="<< Previous", command=self.show_previous_page)
        btn_prev.pack(side=tk.LEFT)  # Place the button on the left side of the window

        # Setup a button for navigating to the next page
        btn_next = Button(frm, text="Next >>", command=self.show_next_page)
        btn_next.pack(side=tk.RIGHT)  # Place the button on the right side of the window

        # Setup a button to show the text of the current PDF page
        btn_text = Button(frm, text="Show Text", command=self.show_text_window)
        btn_text.pack(side=tk.BOTTOM)

        # Display the initial page
        self.show_page()
        self.center_window(master)

    # Method to update the display with the current page
    def show_page(self):
        # Render the current page as a pixmap (an image)
        page = self.document.load_page(self.page_number)
        pix = page.get_pixmap()
        img = PhotoImage(data=pix.tobytes("ppm"))  # Convert the pixmap to a Tkinter PhotoImage

        # Update the page label and image label with the current page
        self.page_label.config(text=f"Page {self.page_number + 1} of {len(self.document)}")
        self.image_label.config(image=img)
        self.image_label.image = img  # Keep a reference to avoid garbage collection


    # Method to show the previous page of the PDF
    def show_previous_page(self):
        # Decrease the page number if it's not the first page
        if self.page_number > 0:
            self.page_number -= 1
            self.show_page()  # Update the display to the previous page

    # Method to show the next page of the PDF
    def show_next_page(self):
        # Increase the page number if it's not the last page
        if self.page_number < len(self.document) - 1:
            self.page_number += 1
            self.show_page()  # Update the display to the next page

    def show_text_window(self):
        reader = PdfReader("sample-1.pdf")  # this will create PdfReader object using pypdf2
        page = reader.pages[self.page_number]  # this will extract the first page of the pdf
        text = page.extract_text()

        text_window = tk.Toplevel(self.master)
        text_window.title(f"Text Content of Page {self.page_number + 1}")
        text_area = tk.Text(text_window, wrap="word")
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(text_window, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area['yscrollcommand'] = scrollbar.set

        # Insert text into the text area
        text_area.insert(tk.END, text if text else "No text found on this page.")

        self.center_window(text_window)

    def center_window(self, window):
        # Update the window's widget tree to ensure dimensions are updated
        window.update_idletasks()

        # Calculate the position for the window to be centered
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2

        # Set the geometry of the window including the new x and y coordinates
        window.geometry("+{}+{}".format(x, y))

    def merge(self):
        merger = PdfWriter()
        for pdf in ['sample-1.pdf', 'test.pdf']:
            merger.append(pdf)

        merger.write("merged-pdf.pdf")
        merger.close()
# Create the main window for the application
root = tk.Tk()
root.title("PDF Viewer")  # Set the window title

# Create an instance of the PDFViewer class with the main window and path to the PDF
app = PDFViewer(root, 'sample-1.pdf')

# Start the Tkinter event loop
root.mainloop()
