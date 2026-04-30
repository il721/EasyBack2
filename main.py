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

        self.sources = []  # Список словарей: {"source": path, "dest": path}
        self.default_dest = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # Секция выбора источников и их назначений
        frame_top = tk.LabelFrame(self.root, text="Список бэкапа (Источник -> Назначение)", padx=10,
                                  pady=10)
        frame_top.pack(fill="both", expand=True, padx=10, pady=5)

        # Используем Treeview для отображения колонок
        columns = ("source", "dest")
        self.tree = ttk.Treeview(frame_top, columns=columns, show="headings")
        self.tree.heading("source", text="Источник")
        self.tree.heading("dest", text="Назначение")
        self.tree.column("source", width=350)
        self.tree.column("dest", width=350)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_top)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="Добавить файл", command=self.add_file).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Добавить папку", command=self.add_folder).pack(side="left",
                                                                                  padx=2)
        tk.Button(btn_frame, text="Удалить выбранные", command=self.remove_selected).pack(
            side="left", padx=2)

        tk.Button(btn_frame, text="Сохранить список", command=self.save_list).pack(side="right",
                                                                                   padx=2)
        tk.Button(btn_frame, text="Загрузить список", command=self.load_list).pack(side="right",
                                                                                   padx=2)

        # Секция редактирования пути назначения для выбранных элементов
        frame_edit = tk.LabelFrame(self.root, text="Настройка назначения для выбранных", padx=10,
                                   pady=10)
        frame_edit.pack(fill="x", padx=10, pady=5)

        self.edit_dest_var = tk.StringVar()
        tk.Entry(frame_edit, textvariable=self.edit_dest_var).pack(side="left", fill="x",
                                                                   expand=True, padx=5)
        tk.Button(frame_edit, text="Обзор", command=self.browse_edit_dest).pack(side="left", padx=2)
        tk.Button(frame_edit, text="Применить к выбранным",
                  command=self.apply_dest_to_selected).pack(side="left", padx=2)

        # Секция выбора назначения по умолчанию (для новых элементов)
        frame_mid = tk.LabelFrame(self.root, text="Назначение по умолчанию (для новых элементов)",
                                  padx=10, pady=10)
        frame_mid.pack(fill="x", padx=10, pady=5)

        tk.Entry(frame_mid, textvariable=self.default_dest).pack(side="left", fill="x", expand=True,
                                                                 padx=5)
        tk.Button(frame_mid, text="Обзор", command=self.browse_default_dest).pack(side="right")

        # Кнопка запуска и статус
        self.btn_start = tk.Button(self.root, text="ЗАПУСТИТЬ БЭКАП", bg="#4CAF50", fg="white",
                                   font=("Arial", 12, "bold"), command=self.start_backup_thread)
        self.btn_start.pack(pady=10, fill="x", padx=15)

        self.status_label = tk.Label(self.root, text="Готов к работе", fg="blue")
        self.status_label.pack()

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=5)

    def add_file(self):
        files = filedialog.askopenfilenames(title="Выберите файлы")
        for f in files:
            dest = self.default_dest.get()
            item = {"source": f, "dest": dest}
            self.sources.append(item)
            self.tree.insert("", tk.END, values=(f, dest))

    def add_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            dest = self.default_dest.get()
            item = {"source": folder, "dest": dest}
            self.sources.append(item)
            self.tree.insert("", tk.END, values=(folder, dest))

    def remove_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        # Получаем индексы выбранных элементов
        indices = [self.tree.index(item) for item in selected_items]
        # Сортируем индексы в обратном порядке, чтобы удаление не влияло на последующие индексы
        indices.sort(reverse=True)

        for index in indices:
            self.sources.pop(index)

        for item in selected_items:
            self.tree.delete(item)

    def browse_default_dest(self):
        folder = filedialog.askdirectory(title="Выберите папку для бэкапа по умолчанию")
        if folder:
            self.default_dest.set(folder)

    def browse_edit_dest(self):
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.edit_dest_var.set(folder)

    def apply_dest_to_selected(self):
        selected_items = self.tree.selection()
        new_dest = self.edit_dest_var.get()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите элементы в списке!")
            return
        if not new_dest:
            messagebox.showwarning("Внимание", "Введите или выберите путь назначения!")
            return

        for item in selected_items:
            index = self.tree.index(item)
            self.sources[index]["dest"] = new_dest
            self.tree.item(item, values=(self.sources[index]["source"], new_dest))

    def save_list(self):
        if not self.sources:
            messagebox.showwarning("Внимание", "Список пуст!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"),
                                                            ("All files", "*.*")],
                                                 title="Сохранить список как")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.sources, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "Список успешно сохранен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить список: {e}")

    def load_list(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить список")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_sources = json.load(f)

                self.sources = []
                # Очистка tree
                for item in self.tree.get_children():
                    self.tree.delete(item)

                missing_paths = []
                for item in loaded_sources:
                    # item теперь словарь {"source": ..., "dest": ...}
                    source = item.get("source")
                    dest = item.get("dest", "")
                    if os.path.exists(source):
                        self.sources.append({"source": source, "dest": dest})
                        self.tree.insert("", tk.END, values=(source, dest))
                    else:
                        missing_paths.append(source)

                if missing_paths:
                    messagebox.showwarning("Внимание",
                                           f"Некоторые исходные пути не найдены и пропущены:\n" + "\n".join(
                                               missing_paths[:5]))
                else:
                    messagebox.showinfo("Успех", "Список успешно загружен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить список: {e}")

    def start_backup_thread(self):
        if not self.sources:
            messagebox.showwarning("Внимание", "Добавьте хотя бы один файл или папку!")
            return

        # Проверка, что у всех элементов указано назначение
        for item in self.sources:
            if not item["dest"]:
                messagebox.showwarning("Внимание", f"Укажите путь назначения для: {item['source']}")
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

                self.status_label.config(text=f"Копирование: {name}")
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
            self.status_label.config(text="Бэкап успешно завершен!", fg="green")
            messagebox.showinfo("Готово", "Все файлы успешно скопированы по указанным путям.")

        except Exception as e:
            self.status_label.config(text="Ошибка!", fg="red")
            messagebox.showerror("Ошибка", f"Произошел сбой: {str(e)}")

        finally:
            self.btn_start.config(state="normal")
            self.progress['value'] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
