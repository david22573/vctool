import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
import subprocess
import threading
import concurrent.futures

UNCHECKED_BALLOT = '☐'
CHECKED_BALLOT = '☑'

class FileSearchEngine(ttk.Frame):

    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.term_var = ttk.StringVar(value='md')
        self.type_var = ttk.StringVar(value='endswidth')
        self.check_var = ttk.BooleanVar(value=True)

        # header and labelframe option container
        option_text = "Complete the form to begin your search"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row()
        self.create_term_row()
        self.create_type_row()
        self.create_conversion_row()
        self.create_results_view()

        self.progressbar = ttk.Progressbar(
            master=self,
            mode=INDETERMINATE,
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row,
            text="Browse",
            command=self.on_browse,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="Term", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row,
            text="Search",
            command=self.on_search,
            bootstyle=OUTLINE,
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_type_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="Type", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row,
            text="Contains",
            variable=self.type_var,
            value="contains"
        )
        contains_opt.pack(side=LEFT)

        startswith_opt = ttk.Radiobutton(
            master=type_row,
            text="StartsWith",
            variable=self.type_var,
            value="startswith"
        )
        startswith_opt.pack(side=LEFT, padx=15)

        endswith_opt = ttk.Radiobutton(
            master=type_row,
            text="EndsWith",
            variable=self.type_var,
            value="endswith"
        )
        endswith_opt.pack(side=LEFT)
        endswith_opt.invoke()

    def create_conversion_row(self):
        """Add conversion row to labelframe"""
        self.conversion_var = ttk.StringVar(value='mkv_to_webm')
        conversion_row = ttk.Frame(self.option_lf)
        conversion_row.pack(fill=X, expand=YES)
        conversion_lbl = ttk.Label(conversion_row, text="Conversion", width=10)
        conversion_lbl.pack(side=LEFT, padx=10, pady=10)

        mkv_to_webm_opt = ttk.Radiobutton(
            master=conversion_row,
            text="MKV to WEBM",
            variable=self.conversion_var,
            value="mkv_to_webm"
        )
        mkv_to_webm_opt.pack(side=LEFT)
        mkv_to_webm_opt.invoke()

        mp4_to_webm_opt = ttk.Radiobutton(
            master=conversion_row,
            text="MP4 to WEBM",
            variable=self.conversion_var,
            value="mp4_to_webm"
        )
        mp4_to_webm_opt.pack(side=LEFT, padx=15)

        conversion_btn = ttk.Button(
            master=conversion_row,
            text="Convert",
            command=self.on_convert,
            width=8
        )
        conversion_btn.pack(side=LEFT, padx=5, pady=10)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self,
            bootstyle=INFO,
            columns=[0, 1, 2, 3, 4, 5],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='Name', anchor=W)
        self.resultview.heading(1, text='Modified', anchor=W)
        self.resultview.heading(2, text='Type', anchor=E)
        self.resultview.heading(3, text='Size', anchor=E)
        self.resultview.heading(4, text='Path', anchor=W)
        self.resultview.heading(5, text='Convert', anchor=W)
        self.resultview.column(
            column=0,
            anchor=W,
            width=utility.scale_size(self, 125),
            stretch=False
        )
        self.resultview.column(
            column=1,
            anchor=W,
            width=utility.scale_size(self, 140),
            stretch=False
        )
        self.resultview.column(
            column=2,
            anchor=E,
            width=utility.scale_size(self, 50),
            stretch=False
        )
        self.resultview.column(
            column=3,
            anchor=E,
            width=utility.scale_size(self, 50),
            stretch=False
        )
        self.resultview.column(
            column=4,
            anchor=W,
            width=utility.scale_size(self, 300)
        )
        self.resultview.column(
            column=5,
            anchor=CENTER,
            width=utility.scale_size(self, 100),
            stretch=False
        )

        self.resultview.bind('<ButtonRelease-1>', self.tree_bindings)
        
    def select_all(self, event):
        iids = self.resultview.get_children()
        iid = self.resultview.identify_row(event.y)
        col = self.resultview.identify_column(event.x)
        first_row = iids[0]
        if iid == iids[0] and col == "#{}".format(len(self.resultview["columns"])):
            tag = self.resultview.item(first_row, "tags")[0]
            if tag == 'checked':
                for row in self.resultview.get_children():
                    self.resultview.item(row, tags=['checked'])
                    self.resultview.set(row, column=5, value=CHECKED_BALLOT)
            elif tag == 'unchecked':
                for row in self.resultview.get_children():
                    self.resultview.item(row, tags=['unchecked'])
                    self.resultview.set(row, column=5, value=UNCHECKED_BALLOT)


    def toggle_check(self, event):
        try:
            row_id = self.resultview.identify_row(event.y)
            tag = self.resultview.item(row_id, "tags")[0]
            if tag == 'checked':
                self.resultview.item(row_id, tags=['unchecked'])
                self.resultview.set(row_id, column=5, value=UNCHECKED_BALLOT)
            else:
                self.resultview.set(row_id, column=5, value=CHECKED_BALLOT)
                self.resultview.item(row_id, tags=['checked'])
        except IndexError:
            pass
        
    def tree_bindings(self, event):
        self.toggle_check(event)
        self.select_all(event)

    def on_browse(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        if path:
            self.path_var.set(path)
            dir_path = self.path_var.get()
            print(dir_path)

    def on_search(self):
        """Search for a term based on the search type"""
        self.resultview.delete(*self.resultview.get_children())

        search_term = self.term_var.get()
        search_path = self.path_var.get()
        search_type = self.type_var.get()

        if search_term == '':
            return

        # start search in another thread to prevent UI from locking
        Thread(
            target=FileSearchEngine.file_search,
            args=(search_term, search_path, search_type),
            daemon=True
        ).start()

        iid = self.resultview.insert(
            parent='',
            index=END
        )
        self.resultview.item(iid, open=True)
        self.after(100, lambda: self.check_queue(iid))

    def on_convert(self):
        print('hello')
        # Get the selected conversion option
        conversion_option = self.conversion_var.get()
        files = self.get_files_to_convert()
        # Create a new thread for the file processing task
        Thread(
            target=self.process_files,
            args=(conversion_option, files,),
            daemon=True
        ).start()
        self.progressbar.start(10)
        
        
    def process_files(self, conversion_option, files):
        # Define a function to convert a single file
        def convert_file(file):
            # Construct the output file name
            output_file = file.with_suffix('.webm')

            if conversion_option == 'mkv_to_webm':
                # Convert from MKV to WEBM using ffmpeg
                cmd = ['ffmpeg', '-i', file.as_posix(), '-c:v', 'libvpx-vp9', '-c:a', 'libopus', '-preset', 'superfast', '-cpu-used', '4', '-deadline', 'realtime', output_file.as_posix()]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif conversion_option == 'mp4_to_webm':
                # Convert from MP4 to WEBM using ffmpeg
                cmd = ['ffmpeg', '-i', file.as_posix(), '-c:v', 'libvpx-vp9', '-c:a', 'libopus', '-preset', 'superfast', '-cpu-used', '4', '-deadline', 'realtime', output_file.as_posix()]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Use a ThreadPoolExecutor to convert the files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            # Submit the conversion tasks to the executor
            futures = [executor.submit(convert_file, file) for file in files]

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

            self.progressbar.stop()
            
    
    def get_files_to_convert(self):
        # Get the list of checked rows
        checked_rows = []
        for row in self.resultview.tag_has('checked'):
            print('checked')
            checked_rows.append(row)

        # Get the path from the checked rows
        files = []
        for row in checked_rows[1:]:
            path = self.resultview.item(row, 'values')[4]
            print(path)
            files.append(pathlib.Path(path))

        return files

    def check_queue(self, iid):
        """Check file queue and print results if not empty"""
        if all([
            FileSearchEngine.searching,
            not FileSearchEngine.queue.empty()
        ]):
            filename = FileSearchEngine.queue.get()
            self.update_idletasks()
            self.insert_row(filename, iid)
            self.after(100, lambda: self.check_queue(iid))
        elif all([
            not FileSearchEngine.searching,
            not FileSearchEngine.queue.empty()
        ]):
            while not FileSearchEngine.queue.empty():
                filename = FileSearchEngine.queue.get()
                self.insert_row(filename, iid)
            self.update_idletasks()
            self.progressbar.stop()
            for row in self.resultview.get_children():
                self.resultview.set(row, 5, UNCHECKED_BALLOT)
                self.resultview.item(row, tags=['unchecked'])
            self.resultview.yview_moveto(0)
        elif all([
            FileSearchEngine.searching,
            FileSearchEngine.queue.empty()
        ]):
            self.after(100, lambda: self.check_queue(iid))


    def insert_row(self, file, iid):
        """Insert new row in tree search results"""
        try:
            _stats = file.stat()
            _name = file.stem
            _timestamp = datetime.datetime.fromtimestamp(_stats.st_mtime)
            _modified = _timestamp.strftime(r'%m/%d/%Y %I:%M:%S%p')
            _type = file.suffix.lower()
            _size = FileSearchEngine.convert_size(_stats.st_size)
            _path = file.as_posix()
            iid = self.resultview.insert(
                parent='',
                index=END,
                values=(_name, _modified, _type, _size, _path)
            )
            self.resultview.selection_set(iid)
            self.resultview.see(iid)
        except OSError:
            return

    @staticmethod
    def file_search(term, search_path, search_type):
        """Recursively search directory for matching files"""
        FileSearchEngine.set_searching(1)
        if search_type == 'contains':
            FileSearchEngine.find_contains(term, search_path)
        elif search_type == 'startswith':
            FileSearchEngine.find_startswith(term, search_path)
        elif search_type == 'endswith':
            FileSearchEngine.find_endswith(term, search_path)

    @staticmethod
    def find_contains(term, search_path):
        """Find all files that contain the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if term in file:
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def find_startswith(term, search_path):
        """Find all files that start with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.startswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def find_endswith(term, search_path):
        """Find all files that end with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.endswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def set_searching(state=False):
        """Set searching status"""
        FileSearchEngine.searching = state

    @staticmethod
    def convert_size(size):
        """Convert bytes to mb or kb depending on scale"""
        kb = size // 1000
        mb = round(kb / 1000, 1)
        if kb > 1000:
            return f'{mb:,.1f} MB'
        else:
            return f'{kb:,d} KB'


if __name__ == '__main__':

    app = ttk.Window("File Search Engine", "superhero")
    FileSearchEngine(app)
    app.mainloop()
