import csv
import os
import tkinter as tk
import customtkinter as ctk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.fm_multi_level_model import FmmlxModel
from src.fmmlx_mlm_structure.fm_object import FmmlxObject
from src.fmmlx_mlm_structure.fm_slot import FmmlxSlot


@dataclass
class CsvImportPreview:
    file_path: str
    delimiter: str
    header: List[str]
    data_rows: List[List[str]]
    row_count: int
    column_count: int
    header_detected: bool
    warnings: List[str]
    errors: List[str]


@dataclass
class XmlImportPreview:
    file_path: str
    errors: List[str]
    model: Optional[FmmlxModel] = None


class AutoMLMApp(tk.Tk):
    """First GUI slice: guarded import workflow and model inspection."""

    STEP_TITLES = {
        1: "Upload File or Select Example",
        2: "Inspect Model",
        3: "Conduct Model Deepening Analysis",
        4: "Apply Changes Operation",
        5: "Export Model",
    }

    def __init__(self):
        super().__init__()
        self.title("AutoMLM")
        self.geometry("1220x760")
        self.minsize(1000, 650)

        self.current_model: Optional[FmmlxModel] = None
        self.current_file_path: Optional[str] = None
        self.csv_preview: Optional[CsvImportPreview] = None
        self.xml_preview: Optional[XmlImportPreview] = None
        self.selected_csv_columns: Dict[str, tk.BooleanVar] = {}
        self.tree_item_payload: Dict[str, object] = {}
        self.step_unlocked = {1: True, 2: False, 3: False, 4: False, 5: False}
        self.current_step = 1

        self._configure_style()
        self._build_layout()
        self._show_import_page()

    def _configure_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f7f8fb")
        self.style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        self.style.configure("TLabel", background="#f7f8fb", foreground="#1f2937", font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background="#ffffff")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subtitle.TLabel", foreground="#5b6472")
        self.style.configure("Step.TButton", anchor="w", padding=(12, 10))
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        self.style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = ttk.Frame(self, padding=(12, 14))
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.configure(width=280)

        ttk.Label(self.sidebar, text="New Model Workflow", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 12))
        self.step_buttons: Dict[int, ttk.Button] = {}
        for step, title in self.STEP_TITLES.items():
            button = ttk.Button(
                self.sidebar,
                text=self._step_button_text(step),
                style="Step.TButton",
                command=lambda selected_step=step: self._try_open_step(selected_step),
            )
            button.pack(fill="x", pady=4)
            self.step_buttons[step] = button

        self.content = ttk.Frame(self, padding=18)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

    def _step_button_text(self, step: int) -> str:
        state = "open" if self.step_unlocked.get(step) else "locked"
        if step == self.current_step:
            state = "current"
        return f"{step}. {self.STEP_TITLES[step]}\n   {state}"

    def _refresh_steps(self):
        for step, button in self.step_buttons.items():
            button.configure(text=self._step_button_text(step))
            button.state(["!disabled"] if self.step_unlocked.get(step) else ["disabled"])

    def _try_open_step(self, step: int):
        if not self.step_unlocked.get(step):
            return
        if step == 1:
            self._show_import_page()
        elif step == 2:
            self._show_model_page()

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _show_import_page(self):
        self.current_step = 1
        self._refresh_steps()
        self._clear_content()

        ttk.Label(self.content, text="Step 1 of 5: Upload File", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="Import CSV or FMMLx/XML files. A model can only be created when validation succeeds.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        body = ttk.Frame(self.content)
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(2, weight=1)

        file_card = self._card(body)
        file_card.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=(0, 12))
        file_card.columnconfigure(1, weight=1)
        ttk.Label(file_card, text="Selected File", style="Card.TLabel", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )
        self.file_path_var = tk.StringVar(value=self.current_file_path or "")
        ttk.Entry(file_card, textvariable=self.file_path_var).grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8))
        ttk.Button(file_card, text="Browse...", command=self._browse_file).grid(row=1, column=2, sticky="e")
        ttk.Button(file_card, text="Validate File", command=self._validate_current_file).grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )

        validation_card = self._card(body)
        validation_card.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=(0, 12))
        validation_card.columnconfigure(0, weight=1)
        ttk.Label(validation_card, text="Validation Results", style="Card.TLabel", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.validation_table = ttk.Treeview(validation_card, columns=("value",), show="tree headings", height=9)
        self.validation_table.heading("#0", text="Check")
        self.validation_table.heading("value", text="Result")
        self.validation_table.column("#0", width=150, anchor="w")
        self.validation_table.column("value", width=180, anchor="w")
        self.validation_table.grid(row=1, column=0, sticky="nsew")

        mapping_card = self._card(body)
        mapping_card.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(0, 12))
        mapping_card.columnconfigure(0, weight=1)
        ttk.Label(mapping_card, text="Column Selection", style="Card.TLabel", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.mapping_table = ttk.Treeview(
            mapping_card,
            columns=("include", "name", "type"),
            show="headings",
            height=7,
        )
        for col, label, width in [("include", "Include", 80), ("name", "Column Name", 240), ("type", "Data Type", 140)]:
            self.mapping_table.heading(col, text=label)
            self.mapping_table.column(col, width=width, anchor="w")
        self.mapping_table.grid(row=1, column=0, sticky="ew")
        self.mapping_table.bind("<ButtonRelease-1>", self._toggle_column_selection)

        preview_card = self._card(body)
        preview_card.grid(row=2, column=0, columnspan=2, sticky="nsew")
        preview_card.columnconfigure(0, weight=1)
        preview_card.rowconfigure(1, weight=1)
        ttk.Label(preview_card, text="Preview", style="Card.TLabel", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.preview_container = ttk.Frame(preview_card)
        self.preview_container.grid(row=1, column=0, sticky="nsew")
        self.preview_container.columnconfigure(0, weight=1)
        self.preview_container.rowconfigure(0, weight=1)

        actions = ttk.Frame(self.content)
        actions.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        actions.columnconfigure(0, weight=1)
        self.create_button = ttk.Button(
            actions,
            text="Create Model and Continue",
            style="Primary.TButton",
            command=self._create_model,
        )
        self.create_button.grid(row=0, column=1, sticky="e")
        self.create_button.state(["disabled"])

        if self.current_file_path:
            self._validate_current_file()
        else:
            self._render_empty_preview("Select a CSV or XML file to start.")

    def _card(self, parent) -> ttk.Frame:
        return ttk.Frame(parent, style="Card.TFrame", padding=12)

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Supported files", "*.csv *.xml"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("All files", "*.*"),
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self._validate_current_file()

    def _validate_current_file(self):
        file_path = self.file_path_var.get().strip()
        self.current_file_path = file_path or None
        self.csv_preview = None
        self.xml_preview = None
        self.selected_csv_columns.clear()
        self._clear_tree(self.validation_table)
        self._clear_tree(self.mapping_table)

        if not file_path:
            self._set_validation_rows([("Status", "No file selected")])
            self._render_empty_preview("Select a CSV or XML file to start.")
            self.create_button.state(["disabled"])
            return

        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".csv":
            self.csv_preview = self._build_csv_preview(file_path)
            self._render_csv_validation(self.csv_preview)
            self._render_csv_mapping(self.csv_preview)
            self._render_csv_preview(self.csv_preview)
            can_create = not self.csv_preview.errors and self.csv_preview.header_detected
        elif extension == ".xml":
            self.xml_preview = self._build_xml_preview(file_path)
            self._render_xml_validation(self.xml_preview)
            self._render_xml_preview(self.xml_preview)
            can_create = not self.xml_preview.errors
        else:
            self._set_validation_rows([("File type", extension or "unknown"), ("Status", "Unsupported file type")])
            self._render_empty_preview("Only CSV and XML files are supported.")
            can_create = False

        self.create_button.state(["!disabled"] if can_create else ["disabled"])

    def _build_csv_preview(self, file_path: str) -> CsvImportPreview:
        warnings: List[str] = []
        errors: List[str] = []
        helper_model = FmmlxModel()

        try:
            with open(file_path, "r", newline="", encoding="utf-8-sig") as csv_file:
                dialect = helper_model._get_csv_dialect(csv_file)
                reader = csv.reader(csv_file, dialect, skipinitialspace=True)
                rows = [[value.strip().strip('"') for value in row] for row in reader if row]
                delimiter = dialect.delimiter
        except FileNotFoundError:
            return CsvImportPreview(file_path, "", [], [], 0, 0, False, warnings, [f"File not found: {file_path}"])
        except Exception as exc:
            return CsvImportPreview(file_path, "", [], [], 0, 0, False, warnings, [f"Could not read CSV: {exc}"])

        if not rows:
            return CsvImportPreview(file_path, delimiter, [], [], 0, 0, False, warnings, ["CSV file is empty."])

        header = rows[0]
        data_rows = rows[1:]
        column_count = len(header)
        header_detected = helper_model._first_row_looks_like_header(header, data_rows)

        if column_count == 0:
            errors.append("CSV header must contain at least one column.")
        if not header_detected:
            errors.append("No valid header was detected. The first row looks like data, not attribute names.")

        for row_number, row in enumerate(data_rows, start=2):
            if len(row) != column_count:
                errors.append(
                    f"Row {row_number} has {len(row)} values, but the header has {column_count} values."
                )
                break

        if len(data_rows) == 0:
            warnings.append("CSV has a header but no data rows.")

        return CsvImportPreview(
            file_path=file_path,
            delimiter=delimiter,
            header=header,
            data_rows=data_rows,
            row_count=len(data_rows),
            column_count=column_count,
            header_detected=header_detected,
            warnings=warnings,
            errors=errors,
        )

    def _build_xml_preview(self, file_path: str) -> XmlImportPreview:
        try:
            return XmlImportPreview(file_path=file_path, errors=[], model=FmmlxModel(file_path=file_path))
        except Exception as exc:
            return XmlImportPreview(file_path=file_path, errors=[str(exc)], model=None)

    def _render_csv_validation(self, preview: CsvImportPreview):
        delimiter_name = {";": "Semicolon (;)", ",": "Comma (,)", "\t": "Tab", "|": "Pipe (|)"}.get(
            preview.delimiter, preview.delimiter
        )
        rows = [
            ("File type", "CSV"),
            ("Header detected", "Yes" if preview.header_detected else "No"),
            ("Delimiter", delimiter_name),
            ("Rows", str(preview.row_count)),
            ("Columns", str(preview.column_count)),
            ("Status", "Ready" if not preview.errors and preview.header_detected else "Blocked"),
            ("Warnings", "; ".join(preview.warnings) if preview.warnings else "None"),
            ("Errors", "; ".join(preview.errors) if preview.errors else "None"),
        ]
        self._set_validation_rows(rows)

    def _render_xml_validation(self, preview: XmlImportPreview):
        model = preview.model
        rows = [
            ("File type", "XML"),
            ("Status", "Ready" if not preview.errors else "Blocked"),
            ("Errors", "; ".join(preview.errors) if preview.errors else "None"),
        ]
        if model is not None:
            rows.extend(
                [
                    ("Path", model.path_name),
                    ("Classes", str(len(model.get_all_flat_classes()))),
                    ("Objects", str(len(model.get_all_pure_objects()))),
                    ("Associations", str(len(model.associations))),
                    ("Links", str(len(model.links))),
                    ("Enums", str(len(model.enums))),
                ]
            )
        self._set_validation_rows(rows)

    def _set_validation_rows(self, rows: List[tuple]):
        self._clear_tree(self.validation_table)
        for key, value in rows:
            self.validation_table.insert("", "end", text=key, values=(value,))

    def _render_csv_mapping(self, preview: CsvImportPreview):
        self._clear_tree(self.mapping_table)
        helper_model = FmmlxModel()
        for col_index, column_name in enumerate(preview.header):
            values = [row[col_index] for row in preview.data_rows if col_index < len(row)]
            data_type = helper_model._get_csv_attribute_type(values).split("::")[-1]
            selected = tk.BooleanVar(value=True)
            self.selected_csv_columns[column_name] = selected
            self.mapping_table.insert("", "end", iid=column_name, values=("[x]", column_name, data_type))

    def _toggle_column_selection(self, event):
        region = self.mapping_table.identify("region", event.x, event.y)
        column = self.mapping_table.identify_column(event.x)
        item = self.mapping_table.identify_row(event.y)
        if region != "cell" or column != "#1" or item not in self.selected_csv_columns:
            return
        selected = self.selected_csv_columns[item]
        selected.set(not selected.get())
        current_values = list(self.mapping_table.item(item, "values"))
        current_values[0] = "[x]" if selected.get() else "[ ]"
        self.mapping_table.item(item, values=current_values)
        self.create_button.state(["!disabled"] if self._has_selected_columns() else ["disabled"])

    def _has_selected_columns(self) -> bool:
        if self.csv_preview is None or self.csv_preview.errors or not self.csv_preview.header_detected:
            return False
        return any(var.get() for var in self.selected_csv_columns.values())

    def _render_csv_preview(self, preview: CsvImportPreview):
        self._clear_preview_container()
        columns = ["row"] + preview.header
        table = ttk.Treeview(self.preview_container, columns=columns, show="headings", height=8)
        for column in columns:
            table.heading(column, text=column)
            table.column(column, width=110 if column != "row" else 50, anchor="w")
        for idx, row in enumerate(preview.data_rows[:10], start=1):
            padded_row = row + [""] * max(0, len(preview.header) - len(row))
            table.insert("", "end", values=[idx] + padded_row[: len(preview.header)])
        table.grid(row=0, column=0, sticky="nsew")
        self._attach_scrollbars(self.preview_container, table)

    def _render_xml_preview(self, preview: XmlImportPreview):
        self._clear_tree(self.mapping_table)
        self._clear_preview_container()
        table = ttk.Treeview(self.preview_container, columns=("kind", "name", "count"), show="headings", height=8)
        for column, label, width in [("kind", "Element", 180), ("name", "Model Path / Name", 360), ("count", "Count", 100)]:
            table.heading(column, text=label)
            table.column(column, width=width, anchor="w")
        if preview.model is not None:
            model = preview.model
            table.insert("", "end", values=("Path", model.path_name, ""))
            table.insert("", "end", values=("Classes", "", len(model.get_all_flat_classes())))
            table.insert("", "end", values=("Objects", "", len(model.get_all_pure_objects())))
            table.insert("", "end", values=("Attributes", "", self._count_attributes(model)))
            table.insert("", "end", values=("Slots", "", self._count_slots(model)))
            table.insert("", "end", values=("Associations", "", len(model.associations)))
            table.insert("", "end", values=("Links", "", len(model.links)))
            table.insert("", "end", values=("Enums", "", len(model.enums)))
        table.grid(row=0, column=0, sticky="nsew")
        self._attach_scrollbars(self.preview_container, table)

    def _render_empty_preview(self, text: str):
        self._clear_preview_container()
        ttk.Label(self.preview_container, text=text, style="Card.TLabel").grid(row=0, column=0, sticky="w")

    def _clear_preview_container(self):
        for child in self.preview_container.winfo_children():
            child.destroy()

    def _attach_scrollbars(self, parent, table: ttk.Treeview, row: int = 0):
        y_scroll = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        x_scroll = ttk.Scrollbar(parent, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=row, column=1, sticky="ns")
        x_scroll.grid(row=row + 1, column=0, sticky="ew")

    def _create_model(self):
        if not self.current_file_path:
            messagebox.showerror("Import blocked", "Select a file first.")
            return

        try:
            extension = os.path.splitext(self.current_file_path)[1].lower()
            if extension == ".csv":
                selected_columns = [
                    column for column, selected in self.selected_csv_columns.items() if selected.get()
                ]
                if not selected_columns:
                    messagebox.showerror("Import blocked", "Select at least one CSV column.")
                    return
                self.current_model = FmmlxModel(
                    file_path=self.current_file_path,
                    selected_csv_columns=selected_columns,
                )
            elif extension == ".xml":
                self.current_model = self.xml_preview.model if self.xml_preview and self.xml_preview.model else FmmlxModel(
                    file_path=self.current_file_path
                )
            else:
                raise ValueError("Only CSV and XML files are supported.")
        except Exception as exc:
            messagebox.showerror("Import failed", str(exc))
            self.step_unlocked[2] = False
            self._refresh_steps()
            return

        self.step_unlocked[2] = True
        self._show_model_page()

    def _show_model_page(self):
        if self.current_model is None:
            return
        self.current_step = 2
        self._refresh_steps()
        self._clear_content()

        ttk.Label(self.content, text="Step 2 of 5: Inspect Model", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="Review the imported or generated model structure and content.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        model = self.current_model
        body = ttk.Frame(self.content)
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(1, weight=1)

        summary = self._card(body)
        summary.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        for i in range(7):
            summary.columnconfigure(i, weight=1)
        metrics = self._model_metrics(model)
        for idx, (label, value) in enumerate(metrics):
            metric = ttk.Frame(summary, style="Card.TFrame", padding=8)
            metric.grid(row=0, column=idx, sticky="ew", padx=4)
            ttk.Label(metric, text=label, style="Card.TLabel", font=("Segoe UI", 9)).pack(anchor="center")
            ttk.Label(metric, text=str(value), style="Card.TLabel", font=("Segoe UI", 16, "bold")).pack(anchor="center")

        tree_card = self._card(body)
        tree_card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        tree_card.columnconfigure(0, weight=1)
        tree_card.rowconfigure(1, weight=1)
        ttk.Label(tree_card, text="Model Structure", style="Card.TLabel", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.model_tree = ttk.Treeview(tree_card, show="tree", height=18)
        self.model_tree.grid(row=1, column=0, sticky="nsew")
        self.model_tree.bind("<<TreeviewSelect>>", self._show_selected_details)
        self._attach_scrollbars(tree_card, self.model_tree, row=1)

        detail_card = self._card(body)
        detail_card.grid(row=1, column=1, sticky="nsew")
        detail_card.columnconfigure(0, weight=1)
        detail_card.rowconfigure(1, weight=1)
        self.detail_title = ttk.Label(detail_card, text="Details", style="Card.TLabel", font=("Segoe UI", 10, "bold"))
        self.detail_title.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.detail_table = ttk.Treeview(detail_card, columns=("name", "value", "type"), show="headings", height=18)
        for col, label, width in [("name", "Name", 200), ("value", "Value", 280), ("type", "Type", 160)]:
            self.detail_table.heading(col, text=label)
            self.detail_table.column(col, width=width, anchor="w")
        self.detail_table.grid(row=1, column=0, sticky="nsew")
        self._attach_scrollbars(detail_card, self.detail_table, row=1)

        actions = ttk.Frame(self.content)
        actions.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        actions.columnconfigure(1, weight=1)
        ttk.Button(actions, text="Back to Import", command=self._show_import_page).grid(row=0, column=0, sticky="w")
        ttk.Button(actions, text="Export XML...", style="Primary.TButton", command=self._export_xml).grid(
            row=0, column=2, sticky="e"
        )

        self._populate_model_tree(model)

    def _populate_model_tree(self, model: FmmlxModel):
        self.tree_item_payload.clear()
        root_text = model.path_name or os.path.basename(self.current_file_path or "Model")
        root_id = self.model_tree.insert("", "end", text=f"Model: {root_text}", open=True)
        self.tree_item_payload[root_id] = model

        levels: Dict[int, List[FmmlxObject]] = {}
        for obj in model.mlm_objects:
            levels.setdefault(obj.level, []).append(obj)

        for level in sorted(levels.keys(), reverse=True):
            level_id = self.model_tree.insert(root_id, "end", text=f"Level {level}", open=True)
            for obj in sorted(levels[level], key=lambda item: item.object_name):
                obj_id = self.model_tree.insert(level_id, "end", text=obj.object_name, open=level > 0)
                self.tree_item_payload[obj_id] = obj

                if obj.attr_list:
                    attrs_id = self.model_tree.insert(obj_id, "end", text=f"Attributes ({len(obj.attr_list)})")
                    for attr in obj.attr_list:
                        attr_id = self.model_tree.insert(
                            attrs_id,
                            "end",
                            text=f"{attr.attr_name}: {attr.attr_type_short}",
                        )
                        self.tree_item_payload[attr_id] = attr

                if obj.slot_list:
                    slots_id = self.model_tree.insert(obj_id, "end", text=f"Slots ({len(obj.slot_list)})")
                    for slot in obj.slot_list[:20]:
                        slot_id = self.model_tree.insert(slots_id, "end", text=f"{slot.slot_name}: {slot.value}")
                        self.tree_item_payload[slot_id] = slot
                    if len(obj.slot_list) > 20:
                        self.model_tree.insert(slots_id, "end", text="...")

        self.model_tree.selection_set(root_id)
        self._render_model_details(model)

    def _show_selected_details(self, _event):
        selected = self.model_tree.selection()
        if not selected:
            return
        payload = self.tree_item_payload.get(selected[0])
        if isinstance(payload, FmmlxModel):
            self._render_model_details(payload)
        elif isinstance(payload, FmmlxObject):
            self._render_object_details(payload)
        elif isinstance(payload, FmmlxAttribute):
            self._render_attribute_details(payload)
        elif isinstance(payload, FmmlxSlot):
            self._render_slot_details(payload)

    def _render_model_details(self, model: FmmlxModel):
        self.detail_title.configure(text="Model Details")
        self._set_detail_rows(
            [
                ("Path", model.path_name, ""),
                ("Classes", len(model.get_all_flat_classes()), ""),
                ("Objects", len(model.get_all_pure_objects()), ""),
                ("Attributes", self._count_attributes(model), ""),
                ("Slots", self._count_slots(model), ""),
                ("Associations", len(model.associations), ""),
                ("Links", len(model.links), ""),
                ("Enums", len(model.enums), ""),
            ]
        )

    def _render_object_details(self, obj: FmmlxObject):
        self.detail_title.configure(text=f"Object Details: {obj.object_name}")
        rows = [
            ("Full name", obj.full_name, ""),
            ("Level", obj.level, ""),
            ("Class", obj.class_of_object.object_name if obj.class_of_object else "", ""),
            ("Abstract", obj.is_abstract, ""),
        ]
        rows.extend((slot.slot_name, slot.value, self._slot_type(slot)) for slot in obj.slot_list)
        self._set_detail_rows(rows)

    def _render_attribute_details(self, attr: FmmlxAttribute):
        self.detail_title.configure(text=f"Attribute Details: {attr.attr_name}")
        self._set_detail_rows(
            [
                ("Name", attr.attr_name, ""),
                ("Type", attr.attr_type, attr.attr_type_short),
                ("Instantiation level", attr.inst_level, ""),
                ("Owner", attr.owner.object_name if attr.owner else "", ""),
            ]
        )

    def _render_slot_details(self, slot: FmmlxSlot):
        self.detail_title.configure(text=f"Slot Details: {slot.slot_name}")
        self._set_detail_rows(
            [
                ("Name", slot.slot_name, ""),
                ("Value", slot.value, self._slot_type(slot)),
                ("Owner", slot.owner.object_name if slot.owner else "", ""),
                ("Attribute", slot.attribute.attr_name if slot.attribute else "", ""),
            ]
        )

    def _set_detail_rows(self, rows):
        self._clear_tree(self.detail_table)
        for name, value, value_type in rows:
            self.detail_table.insert("", "end", values=(name, value, value_type))

    def _export_xml(self):
        if self.current_model is None:
            return
        default_name = f"{os.path.splitext(os.path.basename(self.current_file_path or 'model'))[0]}_export.xml"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xml",
            initialfile=default_name,
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not filepath:
            return
        try:
            self.current_model.export_xml(filepath=filepath, project_name=self.current_model.path_name or "Root::Export")
            messagebox.showinfo("Export complete", f"XML exported to:\n{filepath}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))

    def _model_metrics(self, model: FmmlxModel):
        return [
            ("Classes", len(model.get_all_flat_classes())),
            ("Objects", len(model.get_all_pure_objects())),
            ("Attributes", self._count_attributes(model)),
            ("Slots", self._count_slots(model)),
            ("Associations", len(model.associations)),
            ("Links", len(model.links)),
            ("Enums", len(model.enums)),
        ]

    def _count_attributes(self, model: FmmlxModel) -> int:
        return sum(len(obj.attr_list) for obj in model.mlm_objects)

    def _count_slots(self, model: FmmlxModel) -> int:
        return sum(len(obj.slot_list) for obj in model.mlm_objects)

    def _slot_type(self, slot: FmmlxSlot) -> str:
        if slot.attribute is not None:
            return slot.attribute.attr_type_short
        return type(slot.value).__name__

    def _clear_tree(self, tree: ttk.Treeview):
        for item in tree.get_children():
            tree.delete(item)


def run():
    app = AutoMLMApp()
    app.mainloop()
