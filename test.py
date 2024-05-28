import fitz  # PyMuPDF: Used for opening and manipulating PDF files
import tkinter as tk  # Tkinter: Used for creating GUI applications in Python
from tkinter import *  # Import all Tkinter classes and constants
from tkinter import ttk, filedialog, simpledialog, \
    messagebox  # ttk for themed widgets, filedialog for file selection dialog, simpledialog for input dialogs
from PyPDF2 import PdfReader, PdfWriter  # PdfReader and PdfWriter: Used for reading and writing PDF files
import os
import platform
import subprocess
# Define a class for our PDF viewer application
class PDFViewer:
    # Initialization method for the PDFViewer class
    def __init__(self, master):
        self.bookmarks = {}

        # master refers to the main window of the Tkinter application
        self.master = master
        self.pdf_path = None  # Path to the currently loaded PDF file
        self.document = None  # PyMuPDF document object
        self.page_number = 0  # Start displaying from the first page
        self.zoom_factor = 1.0

        style = ttk.Style()
        style.configure('Main.TFrame', background='#6FEA99')

        style.layout('Main.TFrame', [
            ('Frame.border', {'sticky': 'nswe', 'border': '1', 'children': [
                ('Frame.padding', {'sticky': 'nswe', 'children': [
                    ('Frame.background', {'sticky': 'nswe'})
                ]})
            ]})
        ])

        self.frm = ttk.Frame(root, padding="3 12 3 12", style='Main.TFrame')
        self.frm.pack(fill='both', expand=True)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_pdf)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Show Text", command=self.show_text_window)
        editmenu.add_command(label="Merge", command=self.merge)
        editmenu.add_command(label="Split", command=self.split_dialog)
        editmenu.add_command(label="Edit Text")
        menubar.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Add Image", command=self.add_image)
        editmenu.add_command(label="Search Text", command=self.search_text)
        editmenu.add_command(label="Encrypt PDF", command=self.encrypt_pdf)
        editmenu.add_command(label="Decrypt PDF", command=self.decrypt_pdf)
        editmenu.add_command(label="Add Bookmark", command=self.add_bookmark)
        editmenu.add_command(label="Remove Bookmark", command=self.remove_bookmark)
        editmenu.add_command(label="Go to Bookmark", command=self.navigate_to_bookmark)
        editmenu.add_command(label="Add Annotation", command=self.add_text_annotation)

        root.config(menu=menubar)

        btn_zoom_in = Button(self.frm, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.place(relx=0.24, rely=0.11)

        btn_prev = Button(self.frm, text="<< Previous", command=self.show_previous_page)
        btn_prev.place(relx=0.278, rely=0.15, anchor='ne')

        btn_zoom_out = Button(self.frm, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.place(relx=0.72, rely=0.11)

        btn_next = Button(self.frm, text="Next >>", command=self.show_next_page)
        btn_next.place(relx=0.72, rely=0.15)

        self.canvas = tk.Canvas(self.frm, bg="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas.config(width=550, height=610)

        self.v_scroll = tk.Scrollbar(self.frm, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scroll = tk.Scrollbar(self.frm, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the canvas to work with the scrollbars
        self.canvas.config(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.frm.bind_all("<MouseWheel>", self.on_mouse_scroll)

        # Setup a label widget for displaying the current page number
        self.page_label = ttk.Label(self.frm, text="")
        self.page_label.pack()

    def on_mouse_scroll(self, event):
        if event.delta < 0:
            self.show_next_page()
        elif event.delta > 0:
            self.show_previous_page()

    def add_text_annotation(self):
        if not self.document:
            return  # Return if no document is loaded

        annotation_text = simpledialog.askstring("Input", "Enter text for annotation:")
        if not annotation_text:
            return  # Return if no text is provided

        page_num = simpledialog.askinteger("Input", "Enter page number for annotation:")
        if not page_num or page_num < 1 or page_num > len(self.document):
            return  # Return if invalid page number is provided

        x = simpledialog.askfloat("Input", "Enter x-coordinate:")
        y = simpledialog.askfloat("Input", "Enter y-coordinate:")
        if x is None or y is None:
            return  # Return if invalid coordinates are provided

        # Open the PDF with PyMuPDF and add the text annotation
        page = self.document.load_page(page_num - 1)
        page.add_freetext_annot(fitz.Rect(x, y, x + 200, y + 50), annotation_text, fontsize=12, rotate=0)
        self.document.save("annotated.pdf")
        self.load_pdf("annotated.pdf")  # Reload the modified PDF
        self.show_page()  # Display the current page

        messagebox.showinfo("Success", f"Annotation added to page {page_num} at ({x}, {y}).")

    def add_bookmark(self):
        if not self.document:
            return  # Return if no document is loaded

        bookmark_name = simpledialog.askstring("Input", "Enter a name for the bookmark:")
        if not bookmark_name:
            return  # Return if no name is provided

        if bookmark_name in self.bookmarks:
            messagebox.showwarning("Warning", "Bookmark name already exists.")
            return

        self.bookmarks[bookmark_name] = self.page_number
        messagebox.showinfo("Success", f"Bookmark '{bookmark_name}' added for page {self.page_number + 1}.")

    def remove_bookmark(self):
        if not self.document:
            return  # Return if no document is loaded

        bookmark_name = simpledialog.askstring("Input", "Enter the name of the bookmark to remove:")
        if not bookmark_name:
            return  # Return if no name is provided

        if bookmark_name in self.bookmarks:
            del self.bookmarks[bookmark_name]
            messagebox.showinfo("Success", f"Bookmark '{bookmark_name}' removed.")
        else:
            messagebox.showwarning("Warning", "Bookmark not found.")

    def navigate_to_bookmark(self):
        if not self.document:
            return  # Return if no document is loaded

        bookmark_name = simpledialog.askstring("Input", "Enter the name of the bookmark to navigate to:")
        if not bookmark_name:
            return  # Return if no name is provided

        if bookmark_name in self.bookmarks:
            self.page_number = self.bookmarks[bookmark_name]
            self.show_page()
            messagebox.showinfo("Success", f"Navigated to bookmark '{bookmark_name}'.")
        else:
            messagebox.showwarning("Warning", "Bookmark not found.")

    def encrypt_pdf(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        password = simpledialog.askstring("Input", "Enter password to encrypt PDF:", show='*')
        if not password:
            return  # Return if no password is provided

        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                           title="Save Encrypted PDF")
            if output_pdf_path:
                with open(output_pdf_path, 'wb') as output_pdf:
                    writer.write(output_pdf)

                messagebox.showinfo("Success", "PDF encrypted and saved successfully.")
            else:
                messagebox.showwarning("Warning", "Save operation cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while encrypting the PDF: {e}")

    def decrypt_pdf(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        password = simpledialog.askstring("Input", "Enter password to decrypt PDF:", show='*')
        if not password:
            return  # Return if no password is provided

        try:
            reader = PdfReader(self.pdf_path)
            if reader.is_encrypted:
                if not reader.decrypt(password):
                    messagebox.showerror("Error", "Incorrect password. Please try again.")
                    return

            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                           title="Save Decrypted PDF")
            if output_pdf_path:
                with open(output_pdf_path, 'wb') as output_pdf:
                    writer.write(output_pdf)

                messagebox.showinfo("Success", "PDF decrypted and saved successfully.")
            else:
                messagebox.showwarning("Warning", "Save operation cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while decrypting the PDF: {e}")

    def search_text(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        search_query = simpledialog.askstring("Input", "Enter text to search:")
        if not search_query:
            return  # Return if no search query is provided

        found = False
        for page_num in range(len(self.document)):
            page = self.document.load_page(page_num)
            text_instances = page.search_for(search_query)
            if text_instances:
                found = True
                self.highlight_text(page_num, text_instances)
                if not self.page_number == page_num:
                    self.page_number = page_num
                    self.show_page()
                break

        if not found:
            messagebox.showinfo("Search Result", f"'{search_query}' not found in the document.")

    def highlight_text(self, page_num, text_instances):
        page = self.document.load_page(page_num)
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.update()
        self.document.save("highlighted.pdf")
        self.load_pdf("highlighted.pdf")
        self.show_page()

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
        self.page_number = 0  # Reset to the first page

    def show_page(self):
        if not self.document:
            return  # Return if no document is loaded

        # Render the current page as a pixmap (an image) with zoom
        page = self.document.load_page(self.page_number)
        mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)  # Create transformation matrix for zoom
        pix = page.get_pixmap(matrix=mat)
        img = PhotoImage(data=pix.tobytes("ppm"))  # Convert the pixmap to a Tkinter PhotoImage

        # Clear the previous image if any
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

    def show_previous_page(self):
        if self.page_number > 0:
            self.page_number -= 1
            self.show_page()  # Update the display to the previous page

    def show_next_page(self):
        if self.page_number < len(self.document) - 1:
            self.page_number += 1
            self.show_page()  # Update the display to the next page

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

    def center_window(self, window):
        window.update_idletasks()  # Update the window's widget tree to ensure dimensions are updated
        screen_width = window.winfo_screenwidth()  # Get the screen width
        screen_height = window.winfo_screenheight()  # Get the screen height
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))  # Get the window size
        x = screen_width // 2 - size[0] // 2  # Calculate x position to center the window
        y = screen_height // 2 - size[1] // 2  # Calculate y position to center the window
        window.geometry("+{}+{}".format(x, y))  # Set the geometry of the window to center it

    def merge(self):
        merger = PdfWriter()  # Create a PdfWriter object
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")], title="Select PDFs to Merge")
        for pdf in file_paths:  # List of PDFs to merge
            merger.append(pdf)  # Append each PDF to the merger

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save Merged PDF")
        if output_path:
            with open(output_path, 'wb') as f:
                merger.write(f)  # Write the merged PDF to a file
        merger.close()  # Close the merger

    def rotate_current_page(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        reader = PdfReader(self.pdf_path)  # Create PdfReader object
        writer = PdfWriter()  # Create PdfWriter object

        for i, page in enumerate(reader.pages):
            if i == self.page_number:
                page.rotate(90)  # Rotate the current page by 90 degrees
            writer.add_page(page)  # Add the page to the writer

        output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save Rotated PDF")
        if output_pdf_path:
            with open(output_pdf_path, 'wb') as output_pdf:
                writer.write(output_pdf)  # Write the rotated PDF to a file

        self.load_pdf(output_pdf_path)  # Load the rotated PDF
        self.show_page()  # Display the rotated page

    def split_dialog(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        ranges_str = simpledialog.askstring("Input", "Enter page ranges to split (e.g., 1-3,4-5):")
        if ranges_str:
            ranges = self.parse_ranges(ranges_str)
            self.split(ranges)

    def parse_ranges(self, ranges_str):
        ranges = []
        for part in ranges_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges.append((start, end))
            else:
                num = int(part)
                ranges.append((num, num))
        return ranges

    def split(self, ranges):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        reader = PdfReader(self.pdf_path)  # Create PdfReader object

        for i, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for j in range(start-1, end):
                writer.add_page(reader.pages[j])

            output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title=f"Save Split PDF {i + 1}")
            if output_pdf_path:
                with open(output_pdf_path, 'wb') as output_pdf:
                    writer.write(output_pdf)  # Write the split PDF to a file
            else:
                break  # Stop if the user cancels the save dialog

    def zoom_in(self):
        if not self.document:
            return  # Return if no document is loaded

        self.zoom_factor *= 1.2  # Increase zoom factor by 20%
        self.show_page()  # Update the display with the new zoom factor

    def add_image(self):
        if not self.pdf_path:
            return  # Return if no PDF is loaded

        # Prompt the user to select an image file
        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")],  # Filter to show only image files
            title="Select Image to Add"  # Title of the file dialog
        )
        if not image_path:
            return  # Return if no image is selected

        page_num = simpledialog.askinteger("Input", "Enter page number to add image:")
        if not page_num or page_num < 1 or page_num > len(self.document):
            return  # Return if invalid page number is provided

        x = simpledialog.askfloat("Input", "Enter x-coordinate:")
        y = simpledialog.askfloat("Input", "Enter y-coordinate:")
        if x is None or y is None:
            return  # Return if invalid coordinates are provided

        # Open the PDF with PyMuPDF and add the image
        page = self.document.load_page(page_num - 1)
        rect = fitz.Rect(x, y, x + 200, y + 200)  # Adjust the size of the image as needed
        page.insert_image(rect, filename=image_path)

        # Save the modified PDF
        output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                       title="Save Modified PDF")
        if output_pdf_path:
            self.document.save(output_pdf_path)
            self.load_pdf(output_pdf_path)  # Reload the modified PDF
            self.show_page()  # Display the current page

        print(f"Image added to page {page_num} at ({x}, {y})")

    def zoom_out(self):
        if not self.document:
            return  # Return if no document is loaded

        self.zoom_factor /= 1.2  # Decrease zoom factor by 20%
        self.show_page()  # Update the display with the new zoom factor

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
