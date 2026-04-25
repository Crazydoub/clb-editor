import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import xml.etree.ElementTree as ET
import copy
import shutil

class CLBEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("LightBurn CLB Editor")
        self.root.geometry("1200x650")

        style = ttk.Style()
        style.theme_use("clam")

        self.tree = None
        self.filepath = None

        self.current_material = None
        self.current_entry = None

        self.undo_stack = []
        self.redo_stack = []

        self.slider_widgets = {}

        # MACHINE MODE
        self.machine_var = tk.StringVar(value="Diode")

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        # === TOP ===
        top = ttk.Frame(main)
        top.pack(fill="x")

        ttk.Button(top, text="📂 Ouvrir", command=self.open_file).pack(side="left")
        ttk.Button(top, text="💾 Enregistrer", command=self.save).pack(side="left")
        ttk.Button(top, text="↩️ Undo", command=self.undo).pack(side="left")
        ttk.Button(top, text="↪️ Redo", command=self.redo).pack(side="left")

        ttk.Label(top, text="Machine").pack(side="left", padx=10)
        combo = ttk.Combobox(top, textvariable=self.machine_var,
                             values=["Diode","CO2","Galvo"],
                             width=8, state="readonly")
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self.update_speed_range())

        ttk.Label(top, text="mm/s").pack(side="right", padx=10)

        # === BODY ===
        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        # === MATERIALS ===
        mat_frame = ttk.LabelFrame(body, text="Matériaux")
        mat_frame.pack(side="left", fill="y")
        mat_frame.config(width=220)

        self.mat_list = tk.Listbox(mat_frame)
        self.mat_list.pack(fill="both", expand=True)

        self.mat_list.bind("<<ListboxSelect>>", self.select_material)
        self.mat_list.bind("<Double-Button-1>", self.rename_material)

        ttk.Button(mat_frame, text="➕ Matériau", command=self.add_material).pack(fill="x")
        ttk.Button(mat_frame, text="📄 Dupliquer", command=self.duplicate_material).pack(fill="x")
        ttk.Button(mat_frame, text="🔤 Trier A→Z", command=self.sort_materials).pack(fill="x")
        ttk.Button(mat_frame, text="❌ Supprimer", command=self.delete_material).pack(fill="x")

        # === ENTRIES ===
        entry_frame = ttk.LabelFrame(body, text="Profils")
        entry_frame.pack(side="left", fill="y")
        entry_frame.config(width=300)

        self.entry_list = tk.Listbox(entry_frame)
        self.entry_list.pack(fill="both", expand=True)

        self.entry_list.bind("<<ListboxSelect>>", self.select_entry)

        ttk.Button(entry_frame, text="➕ Profil", command=self.add_entry).pack(fill="x")
        ttk.Button(entry_frame, text="📄 Dupliquer", command=self.duplicate_entry).pack(fill="x")
        ttk.Button(entry_frame, text="🔤 Nom", command=self.sort_entries_name).pack(fill="x")
        ttk.Button(entry_frame, text="📏 Épaisseur", command=self.sort_entries_thickness).pack(fill="x")
        ttk.Button(entry_frame, text="⚙️ Type", command=self.sort_entries_type).pack(fill="x")
        ttk.Button(entry_frame, text="❌ Supprimer", command=self.delete_entry).pack(fill="x")

        # === EDIT ===
        edit = ttk.LabelFrame(body, text="Édition")
        edit.pack(side="left", fill="both", expand=True)

        self.fields = {}

        def add_field(label, key, row):
            ttk.Label(edit, text=label).grid(row=row, column=0, sticky="w")
            e = ttk.Entry(edit)
            e.grid(row=row, column=1, sticky="ew")
            self.fields[key] = e

        add_field("Épaisseur", "Thickness", 0)
        add_field("Description", "Desc", 1)
        add_field("NoThickTitle", "NoThickTitle", 2)

        self.type_var = tk.StringVar()
        ttk.Label(edit, text="Type").grid(row=3, column=0)
        ttk.Combobox(edit, textvariable=self.type_var,
                     values=["Cut","Scan","Image"],
                     state="readonly").grid(row=3, column=1)

        def add_slider(label, key, row, minv, maxv):
            if key == "speed":
                label += " (mm/s)"

            ttk.Label(edit, text=label).grid(row=row, column=0)

            var = tk.IntVar()
            scale = ttk.Scale(edit, from_=minv, to=maxv)
            scale.grid(row=row, column=1, sticky="ew")

            entry = ttk.Entry(edit, width=8)
            entry.grid(row=row, column=2)

            def sync_scale(val):
                v = int(float(val))
                var.set(v)
                entry.delete(0, tk.END)
                entry.insert(0, str(v))

            def sync_entry(event):
                try:
                    v = int(entry.get())
                    scale.set(v)
                    var.set(v)
                except:
                    pass

            scale.configure(command=sync_scale)
            entry.bind("<KeyRelease>", sync_entry)

            self.slider_widgets[key] = (scale, entry, var)
            return var

        self.speed = add_slider("Vitesse","speed",4,1,100)
        self.minPower = add_slider("Puissance Min","minPower",5,0,100)
        self.maxPower = add_slider("Puissance Max","maxPower",6,0,100)
        self.interval = add_slider("Intervalle","interval",7,0,1)

        ttk.Button(edit, text="Appliquer", command=self.apply_changes)\
            .grid(row=8, column=0, columnspan=3, sticky="ew")

        edit.columnconfigure(1, weight=1)

    # === MACHINE ===
    def update_speed_range(self):
        max_speed = {"Diode":100,"CO2":500,"Galvo":2000}.get(self.machine_var.get(),100)
        scale, _, _ = self.slider_widgets["speed"]
        scale.config(from_=1, to=max_speed)

    # === SAFE ===
    def check_tree(self):
        if self.tree is None:
            messagebox.showerror("Erreur", "Aucun fichier chargé")
            return False
        return True


    # === UNDO ===
    def save_state(self):
        if self.tree is not None:
            self.undo_stack.append(copy.deepcopy(self.tree))
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
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
        if not self.check_tree(): return
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
            shutil.copy(self.filepath, self.filepath + ".bak")
            ET.indent(self.tree, space="    ")
            self.tree.write(self.filepath, encoding="utf-8", xml_declaration=True)

    # === MATERIAL ===
    def populate_materials(self):
        if not self.check_tree(): return
        self.mat_list.delete(0, tk.END)
        for m in self.tree.getroot().findall("Material"):
            self.mat_list.insert(tk.END, m.attrib.get("name"))

    def select_material(self, event):
        if not self.check_tree(): return
        idx = self.mat_list.curselection()
        if idx:
            self.current_material = self.tree.getroot().findall("Material")[idx[0]]
            self.populate_entries()

    def add_material(self):
        if not self.check_tree(): return
        name = simpledialog.askstring("Nom","Nom matériau")
        if name:
            self.save_state()
            ET.SubElement(self.tree.getroot(),"Material",{"name":name})
            self.populate_materials()

    def duplicate_material(self):
        if self.current_material is None: return
        self.save_state()
        new_mat = copy.deepcopy(self.current_material)
        new_mat.attrib["name"] += " (copy)"
        self.tree.getroot().append(new_mat)
        self.populate_materials()

    def sort_materials(self):
        if not self.check_tree(): return
        self.save_state()
        root = self.tree.getroot()
        mats = root.findall("Material")
        mats_sorted = sorted(mats, key=lambda m: m.attrib.get("name","").lower())
        for m in mats: root.remove(m)
        for m in mats_sorted: root.append(m)
        self.populate_materials()

    def delete_material(self):
        if self.current_material is not None:
            self.save_state()
            self.tree.getroot().remove(self.current_material)
            self.populate_materials()

    def rename_material(self, event):
        if not self.check_tree(): return
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
            t = cut.attrib.get("type","?")
            self.entry_list.insert(tk.END,
                f"{t} | {e.attrib.get('Thickness')} | {e.attrib.get('Desc')} | {e.attrib.get('NoThickTitle','')}")

    def select_entry(self, event):
        idx = self.entry_list.curselection()
        if idx:
            self.current_entry = self.current_material.findall("Entry")[idx[0]]
            self.load_entry()

    def add_entry(self):
        if self.current_material is None: return
        self.save_state()

        e = ET.SubElement(self.current_material,"Entry",
            {"Thickness":"-1.0000","Desc":"New","NoThickTitle":""})

        cut = ET.SubElement(e,"CutSetting",{"type":"Scan"})

        for tag,val in [
            ("index","0"),("name",""),("LinkPath",""),
            ("speed","100"),("minPower","0"),("maxPower","50"),("maxPower2","0"),
            ("interval","0"),("priority","0"),
            ("tabCount","1"),("tabCountMax","1")
        ]:
            ET.SubElement(cut,tag,{"Value":val})

        self.populate_entries()

    def duplicate_entry(self):
        if self.current_entry is not None:
            self.save_state()
            self.current_material.append(copy.deepcopy(self.current_entry))
            self.populate_entries()

    def delete_entry(self):
        if self.current_entry is not None:
            self.save_state()
            self.current_material.remove(self.current_entry)
            self.populate_entries()

    def sort_entries_name(self):
        if self.current_material is None: return
        self.save_state()
        entries = self.current_material.findall("Entry")
        sorted_entries = sorted(entries, key=lambda e: e.attrib.get("Desc","").lower())
        for e in entries: self.current_material.remove(e)
        for e in sorted_entries: self.current_material.append(e)
        self.populate_entries()

    def sort_entries_thickness(self):
        if self.current_material is None: return
        self.save_state()
        def get_th(e):
            try: return float(e.attrib.get("Thickness",0))
            except: return 0
        entries = self.current_material.findall("Entry")
        sorted_entries = sorted(entries, key=get_th)
        for e in entries: self.current_material.remove(e)
        for e in sorted_entries: self.current_material.append(e)
        self.populate_entries()

    def sort_entries_type(self):
        if self.current_material is None: return
        self.save_state()
        def get_type(e):
            cut = e.find("CutSetting")
            return cut.attrib.get("type","") if cut is not None else ""
        entries = self.current_material.findall("Entry")
        sorted_entries = sorted(entries, key=get_type)
        for e in entries: self.current_material.remove(e)
        for e in sorted_entries: self.current_material.append(e)
        self.populate_entries()

    def load_entry(self):
        cut = self.current_entry.find("CutSetting")

        def get(tag):
            el = cut.find(tag)
            return int(float(el.attrib["Value"])) if el else 0

        for k in ["Thickness","Desc","NoThickTitle"]:
            self.fields[k].delete(0, tk.END)
            self.fields[k].insert(0, self.current_entry.attrib.get(k,""))

        self.type_var.set(cut.attrib.get("type","Scan"))

        self.set_slider("speed", get("speed"))
        self.set_slider("minPower", get("minPower"))
        self.set_slider("maxPower", get("maxPower"))
        self.set_slider("interval", get("interval"))

    def set_slider(self,key,value):
        scale, entry, var = self.slider_widgets[key]
        v=int(value)
        scale.set(v)
        var.set(v)
        entry.delete(0,tk.END)
        entry.insert(0,str(v))

    def apply_changes(self):
        if not self.current_entry: return

        self.save_state()

        for k in ["Thickness","Desc","NoThickTitle"]:
            self.current_entry.attrib[k] = self.fields[k].get()

        cut = self.current_entry.find("CutSetting")
        cut.attrib["type"] = self.type_var.get()

        def setv(tag,val):
            el=cut.find(tag)
            if el is None:
                el=ET.SubElement(cut,tag)
            el.attrib["Value"]=str(int(val))

        setv("speed", self.speed.get())
        setv("minPower", self.minPower.get())
        setv("maxPower", self.maxPower.get())
        setv("interval", self.interval.get())

        self.populate_entries()

if __name__ == "__main__":
    root = tk.Tk()
    CLBEditor(root)
    root.mainloop()
    
