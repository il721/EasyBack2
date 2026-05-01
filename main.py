import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import threading
import json
from datetime import datetime


class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Backup Tool")
        self.root.geometry("800x600")

        self.sources = []  # List of dictionaries: {"source": path, "dest": path}
        self.default_dest = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # Section for selecting sources and their destinations
        frame_top = tk.LabelFrame(self.root, text="Backup List (Source -> Destination)", padx=10,
                                  pady=10)
        frame_top.pack(fill="both", expand=True, padx=10, pady=5)

        # Use Treeview to display columns
        columns = ("source", "dest")
        self.tree = ttk.Treeview(frame_top, columns=columns, show="headings")
        self.tree.heading("source", text="Source")
        self.tree.heading("dest", text="Destination")
        self.tree.column("source", width=350)
        self.tree.column("dest", width=350)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_top)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="Add File", command=self.add_file).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side="left",
                                                                                  padx=2)
        tk.Button(btn_frame, text="Delete Selected", command=self.remove_selected).pack(
            side="left", padx=2)

        tk.Button(btn_frame, text="Save List", command=self.save_list).pack(side="right",
                                                                                   padx=2)
        tk.Button(btn_frame, text="Load List", command=self.load_list).pack(side="right",
                                                                                   padx=2)

        # Section for editing the destination path for selected items
        frame_edit = tk.LabelFrame(self.root, text="Set Destination for Selected", padx=10,
                                   pady=10)
        frame_edit.pack(fill="x", padx=10, pady=5)

        self.edit_dest_var = tk.StringVar()
        tk.Entry(frame_edit, textvariable=self.edit_dest_var).pack(side="left", fill="x",
                                                                   expand=True, padx=5)
        tk.Button(frame_edit, text="Browse", command=self.browse_edit_dest).pack(side="left", padx=2)
        tk.Button(frame_edit, text="Apply to Selected",
                  command=self.apply_dest_to_selected).pack(side="left", padx=2)

        # Section for selecting the default destination (for new items)
        frame_mid = tk.LabelFrame(self.root, text="Default Destination (for new items)",
                                  padx=10, pady=10)
        frame_mid.pack(fill="x", padx=10, pady=5)

        tk.Entry(frame_mid, textvariable=self.default_dest).pack(side="left", fill="x", expand=True,
                                                                 padx=5)
        tk.Button(frame_mid, text="Browse", command=self.browse_default_dest).pack(side="right")

        # Start button and status
        self.btn_start = tk.Button(self.root, text="START BACKUP", bg="#4CAF50", fg="white",
                                   font=("Arial", 12, "bold"), command=self.start_backup_thread)
        self.btn_start.pack(pady=10, fill="x", padx=15)

        self.status_label = tk.Label(self.root, text="Ready", fg="blue")
        self.status_label.pack()

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=5)

    def add_file(self):
        files = filedialog.askopenfilenames(title="Select Files")
        for f in files:
            dest = self.default_dest.get()
            item = {"source": f, "dest": dest}
            self.sources.append(item)
            self.tree.insert("", tk.END, values=(f, dest))

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            dest = self.default_dest.get()
            item = {"source": folder, "dest": dest}
            self.sources.append(item)
            self.tree.insert("", tk.END, values=(folder, dest))

    def remove_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        # Get indices of selected items
        indices = [self.tree.index(item) for item in selected_items]
        # Sort indices in reverse order so that deletion does not affect subsequent indices
        indices.sort(reverse=True)

        for index in indices:
            self.sources.pop(index)

        for item in selected_items:
            self.tree.delete(item)

    def browse_default_dest(self):
        folder = filedialog.askdirectory(title="Select Default Backup Folder")
        if folder:
            self.default_dest.set(folder)

    def browse_edit_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.edit_dest_var.set(folder)

    def apply_dest_to_selected(self):
        selected_items = self.tree.selection()
        new_dest = self.edit_dest_var.get()
        if not selected_items:
            messagebox.showwarning("Attention", "Select items in the list!")
            return
        if not new_dest:
            messagebox.showwarning("Attention", "Enter or select a destination path!")
            return

        for item in selected_items:
            index = self.tree.index(item)
            self.sources[index]["dest"] = new_dest
            self.tree.item(item, values=(self.sources[index]["source"], new_dest))

    def save_list(self):
        if not self.sources:
            messagebox.showwarning("Attention", "The list is empty!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"),
                                                            ("All files", "*.*")],
                                                 title="Save List As")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.sources, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "List saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save list: {e}")

    def load_list(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load List")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_sources = json.load(f)

                self.sources = []
                # Clear tree
                for item in self.tree.get_children():
                    self.tree.delete(item)

                missing_paths = []
                for item in loaded_sources:
                    # item is now a dictionary {"source": ..., "dest": ...}
                    source = item.get("source")
                    dest = item.get("dest", "")
                    if os.path.exists(source):
                        self.sources.append({"source": source, "dest": dest})
                        self.tree.insert("", tk.END, values=(source, dest))
                    else:
                        missing_paths.append(source)

                if missing_paths:
                    messagebox.showwarning("Attention",
                                           f"Some source paths were not found and were skipped:\n" + "\n".join(
                                               missing_paths[:5]))
                else:
                    messagebox.showinfo("Success", "List loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load list: {e}")

    def start_backup_thread(self):
        if not self.sources:
            messagebox.showwarning("Attention", "Add at least one file or folder!")
            return

        # Check that all items have a destination specified
        for item in self.sources:
            if not item["dest"]:
                messagebox.showwarning("Attention", f"Specify destination path for: {item['source']}")
                return

        self.btn_start.config(state="disabled")
        threading.Thread(target=self.perform_backup, daemon=True).start()

    def perform_backup(self):
        try:
            total = len(self.sources)

            for i, item in enumerate(self.sources):
                path = item["source"]
                dest = item["dest"]
                name = os.path.basename(path)

                self.status_label.config(text=f"Copying: {name}")
                self.progress['value'] = (i / total) * 100

                os.makedirs(dest, exist_ok=True)
                target_path = os.path.join(dest, name)

                if os.path.isdir(path):
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(path, target_path)
                else:
                    shutil.copy2(path, target_path)

            self.progress['value'] = 100
            self.status_label.config(text="Backup completed successfully!", fg="green")
            messagebox.showinfo("Done", "All files have been successfully copied to the specified paths.")

        except Exception as e:
            self.status_label.config(text="Error!", fg="red")
            messagebox.showerror("Error", f"A failure occurred: {str(e)}")

        finally:
            self.btn_start.config(state="normal")
            self.progress['value'] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
