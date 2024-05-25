import tkinter as tk

class ScrolledCanvas(tk.Frame):

    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)

        # create canvas
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='news')  # changed

        # create right scrollbar and connect to canvas Y
        self._vertical_bar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        if vertical:
            self._vertical_bar.grid(row=0, column=1, sticky='ns')
        self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # create bottom scrollbar and connect to canvas X
        self._horizontal_bar = tk.Scrollbar(self, orient='horizontal', command=self._canvas.xview)
        if horizontal:
            self._horizontal_bar.grid(row=1, column=0, sticky='we')
        self._canvas.configure(xscrollcommand=self._horizontal_bar.set)

        self.inner = None

        # autoresize inner frame
        self.columnconfigure(0, weight=1)  # changed
        self.rowconfigure(0, weight=1)  # changed

        # self.inner.bind('<Configure>', self.resize)

    def resize(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def add(self, widget):
        self.inner = widget
        widget.master = self._canvas
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', self.resize)