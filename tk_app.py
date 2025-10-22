import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from receptionist import get_greeting, parse_party_size, find_table_for_party
from receptionist.db import init_db, list_tables
import json
import os


class AccessibleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Receptionist Robot - Accessible Desktop')
        self.geometry('900x700')
        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.large_font = False
        self.high_contrast = False

        self._create_widgets()
        init_db()
        self.refresh_tables()

    def _create_widgets(self):
        # Menu
        menubar = tk.Menu(self)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Toggle High Contrast (Ctrl+H)', command=self.toggle_contrast)
        view_menu.add_command(label='Toggle Large Font (Ctrl+L)', command=self.toggle_large_font)
        menubar.add_cascade(label='View', menu=view_menu)
        menubar.add_command(label='Presentation', command=self.open_presentation)
        self.config(menu=menubar)

        # Keyboard shortcuts
        self.bind('<Control-h>', lambda e: self.toggle_contrast())
        self.bind('<Control-l>', lambda e: self.toggle_large_font())
        self.bind('<Control-p>', lambda e: self.open_presentation())

        # Top frame: greeting and status
        top = ttk.Frame(self)
        top.pack(fill='x', padx=12, pady=8)
        self.greet_btn = ttk.Button(top, text='Greet Guest (G)', command=self.greet)
        self.greet_btn.pack(side='left')
        self.bind('g', lambda e: self.greet())

        self.status_var = tk.StringVar(value='Ready')
        self.status_label = ttk.Label(top, textvariable=self.status_var)
        self.status_label.pack(side='left', padx=12)

        # Middle: guest input -> NLP -> find table
        mid = ttk.Frame(self)
        mid.pack(fill='x', padx=12, pady=8)
        ttk.Label(mid, text='Guest phrase:').pack(side='left')
        self.guest_entry = ttk.Entry(mid, width=50)
        self.guest_entry.pack(side='left', padx=8)
        self.find_btn = ttk.Button(mid, text='Find Table (Enter)', command=self.handle_request)
        self.find_btn.pack(side='left')
        self.guest_entry.bind('<Return>', lambda e: self.handle_request())

        # Left: table list
        bottom = ttk.Frame(self)
        bottom.pack(fill='both', expand=True, padx=12, pady=8)

        left = ttk.Frame(bottom)
        left.pack(side='left', fill='y')
        ttk.Label(left, text='Tables:').pack(anchor='nw')
        self.table_list = tk.Listbox(left, width=25, height=20)
        self.table_list.pack(side='left', fill='y')

        # Right: canvas to show path / presentation viewer
        right = ttk.Frame(bottom)
        right.pack(side='left', fill='both', expand=True, padx=12)

        ttk.Label(right, text='Map / Robot view:').pack(anchor='nw')
        self.canvas = tk.Canvas(right, bg='white')
        self.canvas.pack(fill='both', expand=True)

        # Announcements area for screen readers (textual)
        ann_frame = ttk.Frame(self)
        ann_frame.pack(fill='x', padx=12, pady=(0,12))
        ttk.Label(ann_frame, text='Announcements:').pack(anchor='w')
        self.ann_text = tk.Text(ann_frame, height=4, wrap='word')
        self.ann_text.pack(fill='x')
        self.ann_text.configure(state='disabled')

    def announce(self, text: str):
        # Append announcement to the text area and set status
        self.ann_text.configure(state='normal')
        self.ann_text.insert('end', text + '\n')
        self.ann_text.see('end')
        self.ann_text.configure(state='disabled')
        self.status_var.set(text)

    def greet(self):
        msg = get_greeting()
        self.announce(msg)

    def handle_request(self):
        text = self.guest_entry.get().strip()
        if not text:
            messagebox.showinfo('Input needed', 'Please type the guest phrase (e.g. "a table for six").')
            return
        party = parse_party_size(text)
        if party is None:
            self.announce('Could not parse party size. Please clarify.')
            return
        self.announce(f'Parsed party size: {party}')
        res = find_table_for_party(int(party))
        if not res:
            self.announce('No table available for that size.')
            return
        self.announce(f'Reserved table(s): {", ".join(res)}')
        self.refresh_tables()

    def refresh_tables(self):
        self.table_list.delete(0, 'end')
        rows = list(list_tables())
        for r in rows:
            self.table_list.insert('end', f"{r['table_id']} — {r['status']} (cap {r['capacity']})")
        self.draw_map(rows)

    def draw_map(self, rows):
        # Simple grid representation
        self.canvas.delete('all')
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 400
        cols = 10
        rowsc = 8
        tile_w = w / cols
        tile_h = h / rowsc
        # Draw grid
        for i in range(cols):
            for j in range(rowsc):
                x0 = i*tile_w
                y0 = j*tile_h
                x1 = x0 + tile_w
                y1 = y0 + tile_h
                self.canvas.create_rectangle(x0, y0, x1, y1, outline='#ddd')
        # Draw tables as labeled rectangles at arbitrary locations
        coords = {'T1':(2,2),'T2':(4,2),'T3_A':(7,3),'T3_B':(7,4),'T4':(3,5)}
        for t in rows:
            tid = t['table_id']
            st = t['status']
            cap = t['capacity']
            if tid in coords:
                cx,cy = coords[tid]
                x0 = cx*tile_w
                y0 = cy*tile_h
                x1 = x0 + tile_w*1.5
                y1 = y0 + tile_h*0.8
                fill = '#28a745' if st=='Available' else '#dc3545'
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline='#000')
                self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text=f"{tid}\n({cap})", fill='white')

    def toggle_contrast(self):
        self.high_contrast = not self.high_contrast
        if self.high_contrast:
            style = ttk.Style()
            self.configure(bg='black')
            style.configure('.', background='black', foreground='white')
            self.announce('High contrast mode enabled')
        else:
            self.configure(bg='SystemButtonFace')
            self.announce('High contrast mode disabled')

    def toggle_large_font(self):
        self.large_font = not self.large_font
        base = ('Helvetica', 14) if self.large_font else ('Helvetica', 10)
        self.option_add('*Font', base)
        self.announce('Large font enabled' if self.large_font else 'Large font disabled')

    def open_presentation(self):
        # small modal to pick version and show slides
        base = os.path.join(os.path.dirname(__file__), 'versions')
        files = [f[:-5] for f in os.listdir(base) if f.endswith('.json')]
        if not files:
            messagebox.showinfo('No versions', 'No presentation versions found')
            return
        win = tk.Toplevel(self)
        win.title('Presentation')
        win.geometry('800x600')
        sel = tk.StringVar(value=files[0])
        ttk.Label(win, text='Version:').pack()
        version_cb = ttk.Combobox(win, values=files, textvariable=sel)
        version_cb.pack()
        slide_frame = ttk.Frame(win)
        slide_frame.pack(fill='both', expand=True)
        title_lbl = ttk.Label(slide_frame, text='', font=('Helvetica', 16, 'bold'))
        title_lbl.pack(pady=8)
        content_txt = tk.Text(slide_frame, wrap='word')
        content_txt.pack(fill='both', expand=True)

        def load_version(v):
            path = os.path.join(base, v + '.json')
            with open(path, 'r') as fh:
                doc = json.load(fh)
            win.slides = doc.get('slides', [])
            win.idx = 0
            show()

        def show():
            if not hasattr(win, 'slides') or not win.slides:
                return
            s = win.slides[win.idx]
            title_lbl.config(text=s.get('title',''))
            content_txt.delete('1.0','end')
            content_txt.insert('1.0', s.get('content',''))

        def prev():
            if win.idx>0:
                win.idx -= 1
                show()

        def nxt():
            if win.idx < len(win.slides)-1:
                win.idx += 1
                show()

        btns = ttk.Frame(win)
        btns.pack()
        ttk.Button(btns, text='Previous (Left)', command=prev).pack(side='left')
        ttk.Button(btns, text='Next (Right)', command=nxt).pack(side='left')

        version_cb.bind('<<ComboboxSelected>>', lambda e: load_version(sel.get()))
        load_version(files[0])

    def on_close(self):
        self.destroy()


if __name__ == '__main__':
    app = AccessibleApp()
    app.mainloop()
