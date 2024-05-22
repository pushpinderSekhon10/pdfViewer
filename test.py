import fitz  # PyMuPDF: Used for opening and manipulating PDF files
import tkinter as tk  # Tkinter: Used for creating GUI applications in Python
from tkinter import *  # Import all Tkinter classes and constants
from tkinter import ttk, filedialog  # ttk for themed widgets, filedialog for file selection dialog
from PyPDF2 import PdfReader, PdfWriter  # PdfReader and PdfWriter: Used for reading and writing PDF files

# Define a class for our PDF viewer application
class PDFViewer:
    # Initialization method for the PDFViewer class
    def __init__(self, master):
        # master refers to the main window of the Tkinter application
        self.master = master
        self.pdf_path = None  # Path to the currently loaded PDF file
        self.document = None  # PyMuPDF document object
        self.page_number = 0  # Start displaying from the first page
        self.zoom = 1
        self.zoom_factor = 1
        self.width = 550
        self.height = 610

        style = ttk.Style()
        style.configure('Main.TFrame', background='#6FEA99')

        style.layout('Main.TFrame', [
            ('Frame.border', {'sticky': 'nswe', 'border': '1', 'children': [
                ('Frame.padding', {'sticky': 'nswe', 'children': [
                    ('Frame.background', {'sticky': 'nswe'})
                ]})
            ]})
        ])

        frm = ttk.Frame(root, padding="3 12 3 12", style='Main.TFrame')
        frm.pack(fill='both', expand=True)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_pdf)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        root.config(menu=menubar)

        btn_zoom_in = Button(frm, text="Zoom In", command=self.zoom_in).place(relx=0.24, rely=0.11)

        btn_prev = Button(frm, text="<< Previous", command=self.show_previous_page).place(relx=0.278, rely=0.15, anchor='ne')

        btn_text = Button(frm, text="Show Text", command=self.show_text_window)

        btn_merge = Button(frm, text="Merge PDFs", command=self.merge)

        btn_rotate = Button(frm, text="Rotate Page", command=self.rotate_current_page)

        self.canvas = tk.Canvas(frm, bg="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas.config(width=550, height=610)

        btn_zoom_out = Button(frm, text="Zoom Out", command=self.zoom_out).place(relx=0.72, rely=0.11)
        btn_next = Button(frm, text="Next >>", command=self.show_next_page).place(relx=0.72, rely=0.15)

        self.v_scroll = tk.Scrollbar(frm, orient=tk.VERTICAL, command=self.canvas.yview)
        #self.v_scroll

        self.h_scroll = tk.Scrollbar(frm, orient=tk.HORIZONTAL, command=self.canvas.xview)
        #self.h_scroll

        # Configure the canvas to work with the scrollbars
        self.canvas.config(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Setup a label widget for displaying the current page number
        self.page_label = ttk.Label(frm, text="")
        #self.page_label

    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")],  # Filter to show only PDF files
            title="Open PDF File"  # Title of the file dialog
        )
        if file_path:
            self.load_pdf(file_path)  # Load the selected PDF file
            self.show_page()  # Display the first page of the loaded PDF

    def load_pdf(self, pdf_path):
        self.pdf_path = pdf_path  # Store the path of the loaded PDF
        self.document = fitz.open(pdf_path)  # Open the PDF file using PyMuPDF
        self.page_number = self.page_number  # open current page number on rotated pdf

    def show_page(self):
        if not self.document:
            return  # Return if no document is loaded

        # Render the current page as a pixmap (an image) with zoom
        page = self.document.load_page(self.page_number)
        self.width = page.rect.width
        self.height = page.rect.height

        mat = fitz.Matrix(self.zoom, self.zoom)  # Create transformation matrix for zoom

        pix = page.get_pixmap(matrix=mat)

        img = PhotoImage(data=pix.tobytes("ppm"))  # Convert the pixmap to a Tkinter PhotoImage

        # Clear the previous image if any
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas.config(width=self.width, height=self.height)
        self.canvas.delete("all")

        # Create a label to display the image and add it to the canvas
        self.image_label = Label(self.canvas, image=img)
        self.image_label.image = img  # Keep a reference to avoid garbage collection
        self.image_label.pack()

        # Add the image label to the canvas
        self.canvas.create_window((0, 0), window=self.image_label, anchor='nw')

        # Update the scroll region to encompass the new image
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Update the page label with the current page
        self.page_label.config(text=f"Page {self.page_number + 1} of {len(self.document)}")

    # Method to show the previous page of the PDF
    def show_previous_page(self):
        if self.page_number > 0:
            self.page_number -= 1
            self.show_page()  # Update the display to the previous page

    # Method to show the next page of the PDF
    def show_next_page(self):
        if self.page_number < len(self.document) - 1:
            self.page_number += 1
            self.show_page()  # Update the display to the next page

    # Method to show the text of the current PDF page
    def show_text_window(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        reader = PdfReader(self.pdf_path)  # Create PdfReader object using PyPDF2
        page = reader.pages[self.page_number]  # Extract the current page of the PDF
        text = page.extract_text()  # Extract text from the current page

        text_window = tk.Toplevel(self.master)  # Create a new window for displaying text
        text_window.title(f"Text Content of Page {self.page_number + 1}")  # Set window title
        text_area = tk.Text(text_window, wrap="word")  # Create a text widget
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Pack the text widget

        scrollbar = tk.Scrollbar(text_window, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Add a vertical scrollbar
        text_area['yscrollcommand'] = scrollbar.set  # Link scrollbar to the text widget

        text_area.insert(tk.END, text if text else "No text found on this page.")  # Insert text
        self.center_window(text_window)  # Center the text window

    # Method to center a window on the screen
    def center_window(self, window):
        window.update_idletasks()  # Update the window's widget tree to ensure dimensions are updated
        screen_width = window.winfo_screenwidth()  # Get the screen width
        screen_height = window.winfo_screenheight()  # Get the screen height
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))  # Get the window size
        x = screen_width // 2 - size[0] // 2  # Calculate x position to center the window
        y = screen_height // 2 - size[1] // 2  # Calculate y position to center the window
        window.geometry("+{}+{}".format(x, y))  # Set the geometry of the window to center it

    # Method to merge PDFs
    def merge(self):
        merger = PdfWriter()  # Create a PdfWriter object
        for pdf in ['sample-1.pdf', 'test.pdf']:  # List of PDFs to merge
            merger.append(pdf)  # Append each PDF to the merger

        merger.write("merged-pdf.pdf")  # Write the merged PDF to a file
        merger.close()  # Close the merger

    # Method to rotate the current page of the PDF
    def rotate_current_page(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        reader = PdfReader(self.pdf_path)  # Create PdfReader object
        writer = PdfWriter()  # Create PdfWriter object

        for i, page in enumerate(reader.pages):
            if i == self.page_number:
                page.rotate(90)  # Rotate the current page by 90 degrees
            writer.add_page(page)  # Add the page to the writer

        output_pdf_path = 'rotated_sample.pdf'  # Output path for the rotated PDF
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)  # Write the rotated PDF to a file
        print(f"Page {self.page_number + 1} rotated and saved as {output_pdf_path}")

        self.load_pdf(output_pdf_path)  # Load the rotated PDF
        self.show_page()  # Display the rotated page

    # Method to zoom in
    def zoom_in(self):
        if not self.document:
            return  # Return if no document is loaded

        self.zoom_factor *= 1.2  # Increase zoom factor by 20%
        self.show_page()  # Update the display with the new zoom factor

    # Method to zoom out
    def zoom_out(self):
        if not self.document:
            return  # Return if no document is loaded

        self.zoom_factor /= 1.2  # Decrease zoom factor by 20%
        self.show_page()  # Update the display with the new zoom factor

    # Method to handle resizing of the canvas
    def on_resize(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))  # Update the scroll region

# Create the main window for the application
root = tk.Tk()
root.title("PDF Viewer")  # Set the window title
root.geometry("1400x1000")  # Set the initial window size to be larger

# Create an instance of the PDFViewer class with the main window and initial PDF file
app = PDFViewer(root)

# Start the Tkinter event loop
root.mainloop()  # Run the main event loop
