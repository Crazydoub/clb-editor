import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import xml.etree.ElementTree as ET
import copy

class CLBEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("LightBurn CLB Editor")

        self.tree = None
        self.filepath = None

        self.current_material = None
        self.current_entry = None

        self.undo_stack = []
        self.redo_stack = []

        self.slider_widgets = {}

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        # === TOP ===
        top = ttk.Frame(main)
        top.pack(fill="x")

        ttk.Button(top, text="📂 Ouvrir", command=self.open_file).pack(side="left")
        ttk.Button(top, text="💾 Enregistrer", command=self.save).pack(side="left")
        ttk.Button(top, text="↩️ Undo", command=self.undo).pack(side="left")
        ttk.Button(top, text="↪️ Redo", command=self.redo).pack(side="left")

        # === BODY ===
        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        # === MATERIALS ===
        mat_frame = ttk.LabelFrame(body, text="Matériaux")
        mat_frame.pack(side="left", fill="y")
        mat_frame.pack_propagate(False)
        mat_frame.config(width=200)

        self.mat_list = tk.Listbox(mat_frame, width=25)
        self.mat_list.pack(fill="y", expand=True)

        self.mat_list.bind("<<ListboxSelect>>", self.select_material)
        self.mat_list.bind("<Double-Button-1>", self.rename_material)

        ttk.Button(mat_frame, text="➕ Matériau", command=self.add_material).pack(fill="x")
        ttk.Button(mat_frame, text="❌ Supprimer", command=self.delete_material).pack(fill="x")

        # === ENTRIES ===
        entry_frame = ttk.LabelFrame(body, text="Profils")
        entry_frame.pack(side="left", fill="y")
        entry_frame.pack_propagate(False)
        entry_frame.config(width=300)

        self.entry_list = tk.Listbox(entry_frame, width=45)
        self.entry_list.pack(fill="y", expand=True)

        self.entry_list.bind("<<ListboxSelect>>", self.select_entry)

        ttk.Button(entry_frame, text="➕ Profil", command=self.add_entry).pack(fill="x")
        ttk.Button(entry_frame, text="📄 Dupliquer", command=self.duplicate_entry).pack(fill="x")
        ttk.Button(entry_frame, text="❌ Supprimer profil", command=self.delete_entry).pack(fill="x")

        # === EDIT ===
        edit = ttk.LabelFrame(body, text="Édition")
        edit.pack(side="left", fill="both", expand=True)
        edit.pack_propagate(False)

        self.fields = {}

        def add_field(label, key, row):
            ttk.Label(edit, text=label).grid(row=row, column=0, sticky="w")
            e = ttk.Entry(edit)
            e.grid(row=row, column=1, sticky="ew")
            self.fields[key] = e

        add_field("Épaisseur", "Thickness", 0)
        add_field("Description", "Desc", 1)

        self.type_var = tk.StringVar()
        ttk.Label(edit, text="Type").grid(row=2, column=0)
        ttk.Combobox(edit, textvariable=self.type_var,
                     values=["Cut","Scan","Image"],
                     state="readonly").grid(row=2, column=1)

        def add_slider(label, key, row, minv, maxv):
            ttk.Label(edit, text=label).grid(row=row, column=0)

            var = tk.DoubleVar()
            scale = ttk.Scale(edit, from_=minv, to=maxv, variable=var)
            scale.grid(row=row, column=1, sticky="ew")

            entry = ttk.Entry(edit, width=8)
            entry.grid(row=row, column=2)

            def sync(val):
                v = round(float(val), 2)
                var.set(v)
                entry.delete(0, tk.END)
                entry.insert(0, str(v))

            scale.configure(command=sync)

            self.slider_widgets[key] = (scale, entry)
            return var

        self.speed = add_slider("Vitesse","speed",3,0,1000)
        self.minPower = add_slider("Puissance Min","minPower",4,0,100)
        self.maxPower = add_slider("Puissance Max","maxPower",5,0,100)
        self.interval = add_slider("Intervalle","interval",6,0,1)

        ttk.Button(edit, text="Appliquer", command=self.apply_changes)\
            .grid(row=7, column=0, columnspan=3, sticky="ew")

        edit.columnconfigure(1, weight=1)

    # === UNDO ===
    def save_state(self):
        if self.tree is not None:
            self.undo_stack.append(copy.deepcopy(self.tree))
            self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.tree)
            self.tree = self.undo_stack.pop()
            self.refresh()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.tree)
            self.tree = self.redo_stack.pop()
            self.refresh()

    def refresh(self):
        self.populate_materials()
        self.entry_list.delete(0, tk.END)

    # === FILE ===
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CLB","*.clb")])
        if path:
            self.tree = ET.parse(path)
            self.filepath = path
            self.populate_materials()

    def save(self):
        if self.filepath:
            self.tree.write(self.filepath)

    # === MATERIAL ===
    def populate_materials(self):
        self.mat_list.delete(0, tk.END)
        for m in self.tree.getroot().findall("Material"):
            self.mat_list.insert(tk.END, m.attrib.get("name"))

    def select_material(self, event):
        idx = self.mat_list.curselection()
        if idx:
            self.current_material = self.tree.getroot().findall("Material")[idx[0]]
            self.populate_entries()

    def add_material(self):
        self.save_state()
        name = simpledialog.askstring("Nom","Nom matériau")
        if name:
            ET.SubElement(self.tree.getroot(),"Material",{"name":name})
            self.populate_materials()

    def delete_material(self):
        if self.current_material is not None:
            self.save_state()
            self.tree.getroot().remove(self.current_material)
            self.populate_materials()

    def rename_material(self, event):
        idx = self.mat_list.nearest(event.y)
        mat = self.tree.getroot().findall("Material")[idx]
        new = simpledialog.askstring("Rename","Nom",initialvalue=mat.attrib["name"])
        if new:
            self.save_state()
            mat.attrib["name"] = new
            self.populate_materials()

    # === ENTRIES ===
    def populate_entries(self):
        self.entry_list.delete(0, tk.END)
        for e in self.current_material.findall("Entry"):
            cut = e.find("CutSetting")
            t = cut.attrib.get("type","?") if cut is not None else "?"
            self.entry_list.insert(tk.END,
                f"{t} | {e.attrib.get('Thickness')} | {e.attrib.get('Desc')}")

    def select_entry(self, event):
        idx = self.entry_list.curselection()
        if idx:
            self.current_entry = self.current_material.findall("Entry")[idx[0]]
            self.load_entry()

    def add_entry(self):
        self.save_state()
        e = ET.SubElement(self.current_material,"Entry",{"Thickness":"1","Desc":"New"})
        cut = ET.SubElement(e,"CutSetting",{"type":"Cut"})
        ET.SubElement(cut,"speed",{"Value":"100"})
        ET.SubElement(cut,"minPower",{"Value":"50"})
        ET.SubElement(cut,"maxPower",{"Value":"50"})
        ET.SubElement(cut,"interval",{"Value":"0.1"})
        self.populate_entries()

    def duplicate_entry(self):
        if self.current_entry is not None:
            self.save_state()
            self.current_material.append(copy.deepcopy(self.current_entry))
            self.populate_entries()

    def delete_entry(self):
        if self.current_entry is not None:
            if messagebox.askyesno("Suppression","Supprimer ce profil ?"):
                self.save_state()
                self.current_material.remove(self.current_entry)
                self.populate_entries()

    # === LOAD ENTRY ===
    def load_entry(self):
        cut = self.current_entry.find("CutSetting")

        def get(tag):
            el = cut.find(tag)
            return float(el.attrib["Value"]) if el is not None else 0

        self.fields["Thickness"].delete(0, tk.END)
        self.fields["Thickness"].insert(0, self.current_entry.attrib.get("Thickness",""))

        self.fields["Desc"].delete(0, tk.END)
        self.fields["Desc"].insert(0, self.current_entry.attrib.get("Desc",""))

        self.type_var.set(cut.attrib.get("type","Cut"))

        self.set_slider("speed", get("speed"))
        self.set_slider("minPower", get("minPower"))
        self.set_slider("maxPower", get("maxPower"))
        self.set_slider("interval", get("interval"))

    def set_slider(self, key, value):
        scale, entry = self.slider_widgets[key]
        try:
            v = float(value)
        except:
            v = 0
        scale.set(v)
        entry.delete(0, tk.END)
        entry.insert(0, str(v))

    # === APPLY ===
    def apply_changes(self):
        if self.current_entry is None:
            return

        self.save_state()

        th = self.fields["Thickness"].get().strip() or "-1"
        self.current_entry.attrib["Thickness"] = th
        self.current_entry.attrib["Desc"] = self.fields["Desc"].get()

        cut = self.current_entry.find("CutSetting")
        cut.attrib["type"] = self.type_var.get()

        def setv(tag,val):
            el = cut.find(tag)
            if el is None:
                el = ET.SubElement(cut, tag)
            el.attrib["Value"] = str(val)

        setv("speed", self.speed.get())
        setv("minPower", self.minPower.get())
        setv("maxPower", self.maxPower.get())
        setv("interval", self.interval.get())

        self.populate_entries()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x650")
    CLBEditor(root)
    root.mainloop()
