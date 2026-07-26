import csv
import os
import random
import re
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from typing import Dict, List, Optional

import customtkinter as ctk

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


@dataclass
class LoadedModel:
    name: str
    source_file: str
    file_type: str
    model: FmmlxModel
    uploaded: str = ""
    last_worked_on: str = ""


class AutoMLMApp(ctk.CTk):
    COLUMN_WIDTH_INCLUDE = 100
    COLUMN_WIDTH_NAME = 280
    COLUMN_WIDTH_TYPE = 220
    COLUMN_WIDTH_EXAMPLES = 600
    TABLE_HEADER_HEIGHT = 46
    TABLE_ROW_HEIGHT = 50

    VALIDATION_ICON_WIDTH = 34
    VALIDATION_LABEL_WIDTH = 170
    VALIDATION_VALUE_WIDTH = 170
    VALIDATION_ROW_HEIGHT = 42

    STEP_TITLES = {
        1: "Upload File or Select Example",
        2: "Inspect Model",
        3: "Conduct Model Deepening Analysis",
        4: "Apply Change Operations",
        5: "Export Model",
    }

    LOCKED_DESCRIPTIONS = {
        3: "Planned analysis step. Locked in this prototype.",
        4: "Planned operation step. Locked in this prototype.",
        5: "Export is available from Inspect Model for now.",
    }

    STEP_DESCRIPTIONS = {
        1: "Upload a CSV or XML file. This will be the source for your model.",
        2: "Review the imported or generated model structure and content.",
        3: "Analyze the model to identify abstraction and deepening opportunities.",
        4: "Apply selected operations to refine and update the model.",
        5: "Export the final model to XML or other formats.",
    }

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("AutoMLM")
        self.geometry("1500x900")
        self.minsize(1220, 760)

        self.colors = {
            "app_bg": "#f5f7fb",
            "surface": "#ffffff",
            "surface_alt": "#f8fafc",
            "border": "#e2e8f0",
            "text": "#0f172a",
            "muted": "#64748b",
            "primary": "#155EEF",
            "primary_hover": "#0F4FD6",
            "primary_soft": "#EAF2FF",
            "success": "#16a34a",
            "success_soft": "#ecfdf3",
            "disabled": "#cbd5e1",
            "disabled_bg": "#f1f5f9",
            "danger": "#dc2626",
            "danger_soft": "#fff1f2",
        }
        self.configure(fg_color=self.colors["app_bg"])

        self.current_model: Optional[FmmlxModel] = None
        self.current_file_path: Optional[str] = None
        self.csv_preview: Optional[CsvImportPreview] = None
        self.xml_preview: Optional[XmlImportPreview] = None
        self.selected_csv_columns: Dict[str, tk.BooleanVar] = {}
        self.tree_item_payload: Dict[str, object] = {}
        self.loaded_models: List[LoadedModel] = []
        self.step_unlocked = {1: True, 2: False, 3: False, 4: False, 5: False}
        self.step_completed = {1: False, 2: False, 3: False, 4: False, 5: False}
        self.current_step = 1
        self.active_top_tab = "new"
        self._detail_load_token = 0
        self._detail_batch_after_id = None
        self._detail_loading_overlay = None
        self.column_selection_expanded = False
        self.all_columns_selected_var = tk.BooleanVar(value=True)

        self._configure_ttk_style()
        self._build_layout()
        self._show_import_page()

    def _configure_ttk_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Segoe UI is the native, highly readable Windows interface font.
        self.style.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#0f172a",
            rowheight=32,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "Treeview.Heading",
            background="#f8fafc",
            foreground="#334155",
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 12, "bold"),
            padding=(10, 8),
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#0f172a")],
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#eef2f7")],
        )

        # Removes the heavy classic Tk border around the table body.
        self.style.layout(
            "Treeview",
            [("Treeview.treearea", {"sticky": "nswe"})],
        )

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(
            self,
            fg_color=self.colors["surface"],
            corner_radius=0,
            height=66,
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(2, weight=1)

        self.new_model_tab = ctk.CTkButton(
            self.header,
            text="⊕  New Model",
            width=122,
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["surface_alt"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=14),
            command=self._show_import_page,
        )
        self.new_model_tab.grid(row=0, column=0, padx=(24, 8), pady=12)

        self.models_tab = ctk.CTkButton(
            self.header,
            text="▦  Models Overview",
            width=158,
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["surface_alt"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=14),
            command=self._show_models_overview_page,
        )
        self.models_tab.grid(row=0, column=1, padx=(0, 8), pady=12)

        self.shell = ctk.CTkFrame(
            self,
            fg_color=self.colors["app_bg"],
            corner_radius=0,
        )
        self.shell.grid(row=1, column=0, sticky="nsew")
        self.shell.grid_columnconfigure(1, weight=1)
        self.shell.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self.shell,
            width=310,
            fg_color=self.colors["surface"],
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.workflow_title = ctk.CTkLabel(
            self.sidebar,
            text="New Model Workflow",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.workflow_title.pack(fill="x", padx=20, pady=(24, 14))

        self.step_cards: Dict[int, ctk.CTkFrame] = {}
        self.step_number_labels: Dict[int, ctk.CTkLabel] = {}
        self.step_title_labels: Dict[int, ctk.CTkLabel] = {}
        self.step_description_labels: Dict[int, ctk.CTkLabel] = {}
        self.step_state_labels: Dict[int, ctk.CTkLabel] = {}

        for step in self.STEP_TITLES:
            self._build_step_card(step)

        sidebar_note = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_note.pack(fill="x", side="bottom", padx=20, pady=24)

        ctk.CTkLabel(
            sidebar_note,
            text="ⓘ",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(size=15),
        ).grid(row=0, column=0, sticky="nw", padx=(0, 8))

        ctk.CTkLabel(
            sidebar_note,
            text=(
                "Steps are completed in order.\n"
                "The next step becomes available after\n"
                "the current step is finished successfully."
            ),
            justify="left",
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(size=11),
        ).grid(row=0, column=1, sticky="w")

        self.content = ctk.CTkFrame(
            self.shell,
            fg_color=self.colors["app_bg"],
            corner_radius=0,
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=24, pady=22)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

    def _build_step_card(self, step: int):
        card = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["surface"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"],
            height=112,
        )
        card.pack(fill="x", padx=14, pady=6)
        card.pack_propagate(False)
        card.grid_columnconfigure(1, weight=1)

        number = ctk.CTkLabel(
            card,
            text=str(step),
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#94a3b8",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        )
        number.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=(15, 0), sticky="n")

        title = ctk.CTkLabel(
            card,
            text=self.STEP_TITLES[step],
            justify="left",
            anchor="w",
            wraplength=205,
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        )
        title.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(14, 2))

        description = ctk.CTkLabel(
            card,
            text=self.STEP_DESCRIPTIONS[step],
            justify="left",
            anchor="nw",
            wraplength=205,
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        description.grid(row=1, column=1, sticky="new", padx=(0, 12), pady=(0, 2))

        state = ctk.CTkLabel(
            card,
            text="Locked",
            anchor="w",
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        state.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=(0, 10))

        for widget in (card, number, title, description, state):
            widget.bind(
                "<Button-1>",
                lambda _event, selected_step=step: self._try_open_step(selected_step),
            )

        self.step_cards[step] = card
        self.step_number_labels[step] = number
        self.step_title_labels[step] = title
        self.step_description_labels[step] = description
        self.step_state_labels[step] = state

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _show_workflow_sidebar(self):
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.content.grid_configure(row=0, column=1, columnspan=1, sticky="nsew", padx=18, pady=18)

    def _hide_workflow_sidebar(self):
        self.sidebar.grid_remove()
        self.content.grid_configure(row=0, column=0, columnspan=2, sticky="nsew", padx=18, pady=18)

    def _set_top_tab(self, active: str):
        self.active_top_tab = active
        for button, is_active in (
                (self.new_model_tab, active == "new"),
                (self.models_tab, active == "models"),
        ):
            button.configure(
                fg_color=self.colors["primary_soft"] if is_active else "transparent",
                hover_color="#e8f0ff" if is_active else self.colors["surface_alt"],
                text_color=self.colors["primary"] if is_active else self.colors["text"],
                border_width=1 if is_active else 0,
                border_color="#bfdbfe" if is_active else self.colors["surface"],
            )

    def _step_button_text(self, step: int) -> str:
        prefix = "✓" if self.step_completed.get(step) else str(step)
        return f"{prefix}  {self.STEP_TITLES[step]}"

    def _refresh_steps(self):
        for step, card in self.step_cards.items():
            is_current = step == self.current_step
            is_unlocked = self.step_unlocked.get(step, False)
            is_completed = self.step_completed.get(step, False)

            if is_current:
                card.configure(
                    fg_color="#EDF4FF",
                    border_color=self.colors["primary"],
                    border_width=1,
                )
                self.step_number_labels[step].configure(
                    text=str(step),
                    fg_color=self.colors["primary"],
                    text_color="#ffffff",
                )
                self.step_title_labels[step].configure(text_color=self.colors["primary"])
                self.step_description_labels[step].configure(text_color="#475569")
                self.step_state_labels[step].configure(
                    text="Current",
                    text_color=self.colors["primary"],
                )
            elif is_completed:
                card.configure(
                    fg_color=self.colors["surface"],
                    border_color="#bbf7d0",
                    border_width=1,
                )
                self.step_number_labels[step].configure(
                    text="✓",
                    fg_color=self.colors["success"],
                    text_color="#ffffff",
                )
                self.step_title_labels[step].configure(text_color=self.colors["text"])
                self.step_description_labels[step].configure(text_color=self.colors["muted"])
                self.step_state_labels[step].configure(
                    text="Completed",
                    text_color=self.colors["success"],
                )
            elif is_unlocked:
                card.configure(
                    fg_color=self.colors["surface"],
                    border_color=self.colors["border"],
                    border_width=1,
                )
                self.step_number_labels[step].configure(
                    text=str(step),
                    fg_color="#64748b",
                    text_color="#ffffff",
                )
                self.step_title_labels[step].configure(text_color=self.colors["text"])
                self.step_description_labels[step].configure(text_color=self.colors["muted"])
                self.step_state_labels[step].configure(
                    text="Available",
                    text_color=self.colors["primary"],
                )
            else:
                card.configure(
                    fg_color=self.colors["disabled_bg"],
                    border_color=self.colors["border"],
                    border_width=1,
                )
                self.step_number_labels[step].configure(
                    text=str(step),
                    fg_color="#cbd5e1",
                    text_color="#ffffff",
                )
                self.step_title_labels[step].configure(text_color="#94a3b8")
                self.step_description_labels[step].configure(text_color="#a8b2c1")
                self.step_state_labels[step].configure(
                    text="🔒  Locked",
                    text_color="#94a3b8",
                )

    def _try_open_step(self, step: int):
        if not self.step_unlocked.get(step):
            return
        if step == 1:
            self._show_import_page()
        elif step == 2:
            self._show_model_page()

    def _show_import_page(self):
        self.current_step = 1
        self._show_workflow_sidebar()
        self._set_top_tab("new")
        self._refresh_steps()
        self._clear_content()

        self._page_header(
            "Step 1 of 5: Upload File or Select Example",
            "Import a CSV or FMMLx/XML file. Validation starts automatically after a file is selected.",
        )

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------------
        # File input card
        # -------------------------------------------------------------
        self.file_card = self._card(body)
        file_card = self.file_card
        file_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        file_card.grid_columnconfigure(0, weight=1)

        self._card_title(file_card, "File Input").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 10)
        )

        tab_row = ctk.CTkFrame(file_card, fg_color="transparent")
        tab_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        tab_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            tab_row,
            text="⇧  Upload File",
            height=38,
            corner_radius=7,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._browse_file,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            tab_row,
            text="▱  Select Example",
            height=38,
            corner_radius=7,
            fg_color=self.colors["surface_alt"],
            hover_color="#EEF2F7",
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._select_example_file,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self._card_title(file_card, "Selected File").grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 7)
        )

        file_row = ctk.CTkFrame(file_card, fg_color="transparent")
        file_row.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))
        file_row.grid_columnconfigure(0, weight=1)

        self.file_path_var = tk.StringVar(value=self.current_file_path or "")
        self.file_entry = ctk.CTkEntry(
            file_row,
            textvariable=self.file_path_var,
            height=40,
            corner_radius=7,
            border_color=self.colors["border"],
            fg_color="#F8FAFC",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            file_row,
            text="Browse...",
            width=105,
            height=40,
            corner_radius=7,
            fg_color=self.colors["primary_soft"],
            hover_color="#DBEAFE",
            text_color=self.colors["primary"],
            border_width=1,
            border_color="#AFCBFF",
            command=self._browse_file,
        ).grid(row=0, column=1)

        # -------------------------------------------------------------
        # Validation card
        # -------------------------------------------------------------
        self.validation_card = self._card(body)
        validation_card = self.validation_card
        validation_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 12))
        validation_card.grid_columnconfigure(0, weight=1)

        validation_header = ctk.CTkFrame(validation_card, fg_color="transparent")
        validation_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))

        self._card_title(validation_header, "Validation Results").pack(
            side="left"
        )

        self.validation_rows_frame = ctk.CTkFrame(
            validation_card,
            fg_color="transparent",
        )
        self.validation_rows_frame.grid(
            row=1, column=0, sticky="nsew", padx=16, pady=(0, 12)
        )
        self.validation_rows_frame.grid_columnconfigure(2, weight=1)

        # -------------------------------------------------------------
        # Column selection card
        # -------------------------------------------------------------
        selection_card = self._card(body)
        selection_card.grid(
            row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 0)
        )
        selection_card.grid_columnconfigure(0, weight=1)
        selection_card.grid_rowconfigure(3, weight=1)

        selection_header = ctk.CTkFrame(selection_card, fg_color="transparent")
        selection_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 2))
        selection_header.grid_columnconfigure(0, weight=1)

        self._card_title(selection_header, "Column Selection").grid(
            row=0, column=0, sticky="w"
        )

        self.expand_columns_button = ctk.CTkButton(
            selection_header,
            text="Expand  ↑",
            width=112,
            height=32,
            corner_radius=7,
            fg_color="#F8FAFC",
            hover_color="#EEF2F7",
            text_color=self.colors["primary"],
            border_width=1,
            border_color="#B8D2FF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._toggle_column_selection_size,
        )
        self.expand_columns_button.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            selection_card,
            text="Selected columns become attributes of the generated class.",
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

        # One shared grid for header and all data cells.
        # This keeps every value exactly aligned under its column heading.
        self.column_table_wrapper = ctk.CTkFrame(
            selection_card,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=0,
        )
        self.column_table_wrapper.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 14),
        )
        self.column_table_wrapper.grid_columnconfigure(0, weight=1)
        self.column_table_wrapper.grid_rowconfigure(0, weight=1)

        self.column_canvas = tk.Canvas(
            self.column_table_wrapper,
            background="#FFFFFF",
            highlightthickness=0,
            bd=0,
            height=290,
        )
        self.column_canvas.grid(row=0, column=0, sticky="nsew")

        self.column_scrollbar = ctk.CTkScrollbar(
            self.column_table_wrapper,
            orientation="vertical",
            command=self.column_canvas.yview,
            width=14,
            button_color="#AFCBFF",
            button_hover_color=self.colors["primary"],
        )
        self.column_scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 0))
        self.column_canvas.configure(yscrollcommand=self.column_scrollbar.set)

        # Mouse wheel / touchpad scrolling while the pointer is over
        # the Column Selection area.
        self.column_canvas.bind("<Enter>", self._bind_column_scroll_events)
        self.column_canvas.bind("<Leave>", self._unbind_column_scroll_events)

        self.column_table = None
        self.column_canvas_window = None
        self._reset_column_table(self.TABLE_HEADER_HEIGHT + 76)


        actions = ctk.CTkFrame(self.content, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        actions.grid_columnconfigure(0, weight=1)

        self.create_button = ctk.CTkButton(
            actions,
            text="Create Model and Continue  →",
            width=240,
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._create_model,
        )
        self.create_button.grid(row=0, column=1, sticky="e")
        self._set_create_button_enabled(False)

        if self.current_file_path:
            self._validate_current_file()
        else:
            self._render_empty_preview("Select a CSV or XML file to start.")

    def _show_model_page(self):
        if self.current_model is None:
            return

        self.current_step = 2
        self.step_completed[2] = True
        self.step_unlocked[3] = True
        self._show_workflow_sidebar()
        self._set_top_tab("new")
        self._refresh_steps()
        self._clear_content()

        self._page_header(
            "Step 2 of 5: Inspect Model",
            "Review the imported or generated model structure and content.",
        )

        model = self.current_model

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=0, minsize=390)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------------
        # Summary metrics in the requested order.
        # -------------------------------------------------------------
        summary = ctk.CTkFrame(body, fg_color="transparent")
        summary.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        summary_items = [
            ("Classes", len(model.get_all_flat_classes()), "#2563EB"),
            ("Attributes", self._count_attributes(model), "#7C3AED"),
            ("Enumerations", len(model.enums), "#F59E0B"),
            ("Associations", len(model.associations), "#64748B"),
            ("Objects", len(model.get_all_pure_objects()), "#16A34A"),
            ("Slots", self._count_slots(model), "#EA580C"),
            ("Links", len(model.links), "#0891B2"),
        ]

        for index, (label, value, value_color) in enumerate(summary_items):
            summary.grid_columnconfigure(index, weight=1)
            self._metric_card_no_icon(
                summary,
                label,
                value,
                value_color,
            ).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 5, 0 if index == len(summary_items) - 1 else 5),
            )

        # -------------------------------------------------------------
        # Model structure
        # -------------------------------------------------------------
        tree_card = self._card(body)
        tree_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 14),
        )
        tree_card.grid_columnconfigure(0, weight=1)
        tree_card.grid_rowconfigure(2, weight=1)

        self._card_title(tree_card, "Model Structure").grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(14, 8),
        )

        search_frame = ctk.CTkFrame(
            tree_card,
            fg_color="#F8FAFC",
            corner_radius=7,
            border_width=1,
            border_color=self.colors["border"],
            height=38,
        )
        search_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10),
        )
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="⌕",
            width=30,
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI Symbol",
                size=16,
            ),
        ).grid(
            row=0,
            column=0,
            padx=(6, 0),
        )

        self.model_search_var = tk.StringVar()
        self.model_search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.model_search_var,
            placeholder_text="Search in model...",
            height=34,
            corner_radius=0,
            border_width=0,
            fg_color="transparent",
            text_color=self.colors["text"],
            placeholder_text_color="#94A3B8",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.model_search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 8),
        )
        self.model_search_var.trace_add(
            "write",
            lambda *_args: self._filter_model_tree(),
        )

        tree_container = ctk.CTkFrame(
            tree_card,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=0,
        )
        tree_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16),
        )
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        self.model_tree = self._tree(
            tree_container,
            show="tree",
            height=18,
        )
        self.model_tree.tag_configure(
            "model_root",
            font=("Segoe UI", 12, "bold"),
            foreground="#0F172A",
        )
        self.model_tree.tag_configure(
            "level_class",
            font=("Segoe UI", 11, "bold"),
            foreground="#2563EB",
        )
        self.model_tree.tag_configure(
            "level_object",
            font=("Segoe UI", 11, "bold"),
            foreground="#16A34A",
        )
        self.model_tree.tag_configure(
            "class_item",
            font=("Segoe UI", 10),
            foreground="#0F172A",
        )
        self.model_tree.tag_configure(
            "object_item",
            font=("Segoe UI", 10),
            foreground="#0F172A",
        )
        self.model_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.model_tree.bind(
            "<<TreeviewSelect>>",
            self._show_selected_details,
        )

        self.model_tree_scrollbar = ctk.CTkScrollbar(
            tree_container,
            orientation="vertical",
            command=self.model_tree.yview,
            width=14,
            button_color="#AFCBFF",
            button_hover_color=self.colors["primary"],
        )
        self.model_tree_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(4, 0),
        )
        self.model_tree.configure(
            yscrollcommand=self.model_tree_scrollbar.set,
        )

        # -------------------------------------------------------------
        # Details panel in the same visual language as Step 1.
        # -------------------------------------------------------------
        detail_card = self._card(body)
        self.detail_card = detail_card
        detail_card.grid(
            row=1,
            column=1,
            sticky="nsew",
        )
        detail_card.grid_columnconfigure(0, weight=1)
        detail_card.grid_rowconfigure(2, weight=1)

        self.detail_title = self._card_title(
            detail_card,
            "Details",
        )
        self.detail_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(14, 4),
        )

        self.detail_subtitle = ctk.CTkLabel(
            detail_card,
            text="Select a class or object to inspect its attributes and values.",
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
        )
        self.detail_subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            padx=16,
            pady=(0, 10),
        )

        self.detail_table_wrapper = ctk.CTkFrame(
            detail_card,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=0,
        )
        self.detail_table_wrapper.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16),
        )
        self.detail_table_wrapper.grid_columnconfigure(0, weight=1)
        self.detail_table_wrapper.grid_rowconfigure(0, weight=1)

        self.detail_canvas = tk.Canvas(
            self.detail_table_wrapper,
            background="#FFFFFF",
            highlightthickness=0,
            bd=0,
        )
        self.detail_canvas.grid(row=0, column=0, sticky="nsew")

        self.detail_scrollbar = ctk.CTkScrollbar(
            self.detail_table_wrapper,
            orientation="vertical",
            command=self._detail_canvas_yview,
            width=14,
            button_color="#AFCBFF",
            button_hover_color=self.colors["primary"],
        )
        self.detail_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(4, 0),
        )

        self.detail_x_scrollbar = ctk.CTkScrollbar(
            self.detail_table_wrapper,
            orientation="horizontal",
            command=self._detail_canvas_xview,
            height=14,
            button_color="#AFCBFF",
            button_hover_color=self.colors["primary"],
        )
        self.detail_x_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(4, 0),
        )

        self.detail_canvas.configure(
            xscrollcommand=self.detail_x_scrollbar.set,
            yscrollcommand=self.detail_scrollbar.set,
        )
        self.detail_canvas.bind("<Enter>", self._bind_detail_scroll_events)
        self.detail_canvas.bind("<Leave>", self._unbind_detail_scroll_events)

        self.detail_table = tk.Frame(
            self.detail_canvas,
            background="#FFFFFF",
            bd=0,
            highlightthickness=0,
        )
        self.detail_canvas_window = self.detail_canvas.create_window(
            (0, 0),
            window=self.detail_table,
            anchor="nw",
        )
        self.detail_table.bind(
            "<Configure>",
            lambda _event: self.detail_canvas.configure(
                scrollregion=self.detail_canvas.bbox("all")
            ),
        )
        self.detail_canvas.bind(
            "<Configure>",
            self._resize_detail_canvas_window,
        )

        # -------------------------------------------------------------
        # Navigation
        # -------------------------------------------------------------
        actions = ctk.CTkFrame(
            self.content,
            fg_color="transparent",
        )
        actions.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        actions.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            actions,
            text="←  Back to Import",
            width=150,
            height=42,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#EEF2FF",
            border_width=1,
            border_color="#C7D2E3",
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._show_import_page,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkButton(
            actions,
            text="Continue to Next Step  →",
            width=230,
            height=42,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: self._open_placeholder_step(3),
        ).grid(
            row=0,
            column=2,
            sticky="e",
        )

        self._populate_model_tree(model)
        self._render_empty_detail_state()

    def _bind_detail_scroll_events(self, _event=None):
        self.bind_all("<MouseWheel>", self._on_detail_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_detail_shift_mousewheel)

    def _unbind_detail_scroll_events(self, _event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def _on_detail_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.detail_canvas.yview_scroll(delta, "units")
            self._sync_model_overview_sticky_items()

    def _on_detail_shift_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.detail_canvas.xview_scroll(delta, "units")
            self._sync_model_overview_sticky_items()

    def _detail_canvas_yview(self, *args):
        self.detail_canvas.yview(*args)
        self._sync_model_overview_sticky_items()

    def _detail_canvas_xview(self, *args):
        self.detail_canvas.xview(*args)
        self._sync_model_overview_sticky_items()

    def _resize_detail_canvas_window(self, event):
        window_id = getattr(self, "detail_canvas_window", None)
        if window_id is None:
            return
        try:
            self.detail_canvas.itemconfigure(window_id, width=event.width)
        except tk.TclError:
            pass

    def _reset_detail_canvas_table(self):
        self.detail_canvas.delete("all")
        self.detail_table = tk.Frame(
            self.detail_canvas,
            background="#FFFFFF",
            bd=0,
            highlightthickness=0,
        )
        self.detail_canvas_window = self.detail_canvas.create_window(
            (0, 0),
            window=self.detail_table,
            anchor="nw",
        )
        self.detail_table.bind(
            "<Configure>",
            lambda _event: self.detail_canvas.configure(
                scrollregion=self.detail_canvas.bbox("all")
            ),
        )
        self.detail_canvas.configure(scrollregion=(0, 0, 0, 0))

    def _natural_sort_key(self, text: str):
        return [
            int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", text)
        ]

    def _model_overview_display_name(self, model: FmmlxModel) -> str:
        class_objects = [
            obj
            for obj in model.mlm_objects
            if obj.level > 0 and obj.attr_list
        ]
        if class_objects:
            return class_objects[0].name
        if model.path_name:
            return model.path_name.split("::")[-1]
        return "Model"


    def _open_placeholder_step(self, step: int):
        self.step_unlocked[step] = True
        self.current_step = step
        self._refresh_steps()
        messagebox.showinfo(
            "Step not implemented yet",
            f"{self.STEP_TITLES[step]} will be implemented next.",
        )

    def _metric_card_no_icon(
            self,
            parent,
            label: str,
            value: int,
            value_color: str,
    ) -> ctk.CTkFrame:
        card = self._card(parent)
        card.configure(height=104)
        card.grid_propagate(False)

        is_zero = value == 0
        muted_color = "#A8B2C1"
        label_color = muted_color if is_zero else self.colors["text"]
        number_color = muted_color if is_zero else value_color

        value_text = str(value)
        if len(value_text) >= 7:
            value_size = 17
        elif len(value_text) >= 6:
            value_size = 18
        elif len(value_text) >= 5:
            value_size = 20
        else:
            value_size = 22

        ctk.CTkLabel(
            card,
            text=label,
            text_color=label_color,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            y=29,
            anchor="center",
        )

        ctk.CTkLabel(
            card,
            text=value_text,
            text_color=number_color,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=value_size,
                weight="bold",
            ),
        ).place(
            relx=0.5,
            y=69,
            anchor="center",
        )

        return card

    def _show_models_overview_page(self):
        self._hide_workflow_sidebar()
        self._set_top_tab("models")
        self._clear_content()

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Models Overview",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="View and manage all imported or generated models.",
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        total_models_card = ctk.CTkFrame(
            header,
            width=184,
            height=68,
            fg_color=self.colors["primary"],
            corner_radius=10,
            border_width=0,
        )
        total_models_card.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e",
        )
        total_models_card.grid_propagate(False)
        total_models_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            total_models_card,
            text="Total Models",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).grid(row=0, column=0, pady=(10, 0))

        self.total_models_value_label = ctk.CTkLabel(
            total_models_card,
            text=str(len(self.loaded_models)),
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=23, weight="bold"),
        )
        self.total_models_value_label.grid(row=1, column=0, pady=(0, 9))

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=3)
        body.grid_rowconfigure(1, weight=2)

        # -------------------------------------------------------------
        # Models table
        # -------------------------------------------------------------
        list_card = self._card(body)
        list_card.grid(row=0, column=0, sticky="nsew", pady=(0, 14))
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(2, weight=1)

        self._card_title(list_card, "Your Models").grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(14, 10),
        )

        filters = ctk.CTkFrame(
            list_card,
            fg_color="#F8FAFC",
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
        )
        filters.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Search deliberately receives less space, while the remaining filters
        # have enough room to remain readable.
        filters.grid_columnconfigure(1, weight=3, minsize=330)
        filters.grid_columnconfigure(3, weight=0, minsize=150)
        filters.grid_columnconfigure(5, weight=0, minsize=120)
        filters.grid_columnconfigure(7, weight=0, minsize=120)

        self.models_search_var = tk.StringVar()
        self.models_search_var.trace_add(
            "write",
            lambda *_args: self._populate_models_table(),
        )

        ctk.CTkLabel(
            filters,
            text="Search",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=10)

        search_box = ctk.CTkFrame(
            filters,
            fg_color="#FFFFFF",
            corner_radius=7,
            border_width=1,
            border_color="#BBD0F4",
            height=36,
        )
        search_box.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=10)
        search_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_box,
            text="⌕",
            width=30,
            text_color="#64748B",
            font=ctk.CTkFont(family="Segoe UI Symbol", size=16),
        ).grid(row=0, column=0, padx=(6, 0))

        ctk.CTkEntry(
            search_box,
            textvariable=self.models_search_var,
            placeholder_text="Search models...",
            height=32,
            corner_radius=0,
            border_width=0,
            fg_color="transparent",
            placeholder_text_color="#94A3B8",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.models_type_filter_var = tk.StringVar(value="All")

        ctk.CTkLabel(
            filters,
            text="Type",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        ).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=10)

        ctk.CTkOptionMenu(
            filters,
            variable=self.models_type_filter_var,
            values=["All", "CSV", "XML"],
            width=150,
            height=36,
            corner_radius=7,
            fg_color="#FFFFFF",
            button_color="#EEF4FF",
            button_hover_color="#DBEAFE",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#EEF4FF",
            dropdown_text_color=self.colors["text"],
            text_color=self.colors["text"],
            border_width=1,
            border_color="#AFCBFF",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            command=lambda _value: self._populate_models_table(),
        ).grid(row=0, column=3, sticky="w", padx=(0, 18), pady=10)

        self.models_min_objects_var = tk.StringVar()
        self.models_min_attributes_var = tk.StringVar()
        for var in (self.models_min_objects_var, self.models_min_attributes_var):
            var.trace_add("write", lambda *_args: self._populate_models_table())

        ctk.CTkLabel(
            filters,
            text="Min objects",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        ).grid(row=0, column=4, sticky="w", padx=(0, 8), pady=10)

        ctk.CTkEntry(
            filters,
            textvariable=self.models_min_objects_var,
            placeholder_text="e.g. 100",
            width=110,
            height=36,
            border_color="#BBD0F4",
            fg_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).grid(row=0, column=5, sticky="w", padx=(0, 18), pady=10)

        ctk.CTkLabel(
            filters,
            text="Min attributes",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        ).grid(row=0, column=6, sticky="w", padx=(0, 8), pady=10)

        ctk.CTkEntry(
            filters,
            textvariable=self.models_min_attributes_var,
            placeholder_text="e.g. 10",
            width=110,
            height=36,
            border_color="#BBD0F4",
            fg_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).grid(row=0, column=7, sticky="w", padx=(0, 12), pady=10)

        self.models_table_wrapper = ctk.CTkFrame(
            list_card,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=0,
        )
        self.models_table_wrapper.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16),
        )
        self.models_table_wrapper.grid_columnconfigure(0, weight=1)
        self.models_table_wrapper.grid_rowconfigure(0, weight=1)

        self.models_canvas = tk.Canvas(
            self.models_table_wrapper,
            background="#FFFFFF",
            highlightthickness=0,
            bd=0,
        )
        self.models_canvas.grid(row=0, column=0, sticky="nsew")

        self.models_scrollbar = ctk.CTkScrollbar(
            self.models_table_wrapper,
            orientation="vertical",
            command=self.models_canvas.yview,
            width=14,
            button_color="#AFCBFF",
            button_hover_color=self.colors["primary"],
        )
        self.models_scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 0))

        self.models_canvas.configure(
            yscrollcommand=self.models_scrollbar.set,
        )
        self.models_canvas.bind("<Enter>", self._bind_models_scroll_events)
        self.models_canvas.bind("<Leave>", self._unbind_models_scroll_events)
        self.models_canvas.bind(
            "<Configure>",
            lambda _event: self._populate_models_table(),
        )

        # -------------------------------------------------------------
        # Selected model
        # -------------------------------------------------------------
        details_card = self._card(body)
        details_card.grid(row=1, column=0, sticky="nsew")
        details_card.grid_columnconfigure(0, weight=1)

        self._card_title(details_card, "Selected Model").grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(14, 8),
        )

        self.overview_details = ctk.CTkFrame(
            details_card,
            fg_color="#FFFFFF",
            corner_radius=0,
        )
        self.overview_details.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16),
        )
        self.overview_details.grid_columnconfigure(0, weight=0, minsize=380)
        self.overview_details.grid_columnconfigure(1, weight=1)

        self._populate_models_table()
        if hasattr(self, "total_models_value_label"):
            self.total_models_value_label.configure(
                text=str(len(self.loaded_models))
            )
        self._render_overview_details(None)

    def _page_header(self, title: str, subtitle: str):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(1, weight=1)

        step_number = None
        display_title = title
        match = re.match(r"Step\s+(\d+)\s+of\s+\d+:\s*(.*)", title)
        if match:
            step_number = match.group(1)
            display_title = f"Step {step_number} of 5: {match.group(2)}"

        if step_number:
            ctk.CTkLabel(
                header,
                text=step_number,
                width=46,
                height=self.TABLE_HEADER_HEIGHT,
                corner_radius=23,
                fg_color=self.colors["primary_soft"],
                text_color=self.colors["primary"],
                font=ctk.CTkFont(size=19, weight="bold"),
            ).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 16))

        ctk.CTkLabel(
            header,
            text=display_title,
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=1, sticky="w", pady=(3, 0))

    def _card(self, parent) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"],
        )

    def _card_title(self, parent, text: str) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text=text,
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )

    def _metric_card(self, parent, label: str, value: int) -> ctk.CTkFrame:
        card = self._card(parent)
        ctk.CTkLabel(
            card,
            text=label,
            text_color=self.colors["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(pady=(10, 0))
        ctk.CTkLabel(
            card,
            text=str(value),
            text_color=self.colors["text"],
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(pady=(2, 10))
        return card

    def _tree(self, parent, **kwargs) -> ttk.Treeview:
        tree = ttk.Treeview(parent, **kwargs)
        tree.tag_configure("even", background="#ffffff")
        tree.tag_configure("odd", background="#f8fafc")
        return tree

    def _select_example_file(self):
        """Open the project's examples folder, if one exists."""
        candidate_folders = [
            os.path.join(os.getcwd(), "examples"),
            os.path.join(os.path.dirname(__file__), "examples"),
            os.path.join(os.path.dirname(__file__), "data", "examples"),
        ]
        examples_dir = next(
            (folder for folder in candidate_folders if os.path.isdir(folder)),
            None,
        )

        if examples_dir is None:
            messagebox.showinfo(
                "No examples found",
                "Create an 'examples' folder in the project and place CSV or XML example files inside it.",
            )
            return

        file_path = filedialog.askopenfilename(
            initialdir=examples_dir,
            title="Select Example",
            filetypes=[
                ("Supported files", "*.csv *.xml"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self._validate_current_file()

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

        if not file_path:
            self.validation_status_badge.configure(
                text="Not validated",
                fg_color=self.colors["disabled_bg"],
                text_color=self.colors["muted"],
            )
            self._set_validation_rows([("File", "No file selected")])
            self._render_empty_preview("Select a CSV or XML file to start.")
            self._set_create_button_enabled(False)
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
            self._set_validation_rows([
                ("File type", extension or "unknown"),
                ("Errors", "Unsupported file type"),
            ])
            self._render_empty_preview("Only CSV and XML files are supported.")
            can_create = False

        self._set_create_button_enabled(can_create and self._can_create_current_file())


    def _set_create_button_enabled(self, enabled: bool):
        self.create_button.configure(
            state="normal" if enabled else "disabled",
            fg_color=self.colors["primary"] if enabled else "#cbd5e1",
            hover_color=self.colors["primary_hover"] if enabled else "#cbd5e1",
            text_color="#ffffff" if enabled else "#f8fafc",
        )

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
                errors.append(f"Row {row_number} has {len(row)} values, but the header has {column_count} values.")
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
        is_ready = not preview.errors and preview.header_detected
        delimiter_name = {";": "Semicolon (;)", ",": "Comma (,)", "\t": "Tab", "|": "Pipe (|)"}.get(
            preview.delimiter, preview.delimiter
        )
        self._set_validation_rows(
            [
                ("File type", "CSV"),
                ("Status", "Ready" if is_ready else "Blocked"),
                ("Delimiter", delimiter_name),
                ("Rows", str(preview.row_count)),
                ("Columns", str(preview.column_count)),
                ("Errors", "; ".join(preview.errors) if preview.errors else "None"),
            ]
        )

    def _render_xml_validation(self, preview: XmlImportPreview):
        is_ready = not preview.errors
        model = preview.model
        rows = [
            ("File type", "XML"),
            ("Status", "Ready" if is_ready else "Blocked"),
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

    def _bind_column_scroll_events(self, _event=None):
        self.bind_all("<MouseWheel>", self._on_column_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_column_shift_mousewheel)

    def _unbind_column_scroll_events(self, _event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def _on_column_mousewheel(self, event):
        # Windows/macOS touchpads usually send MouseWheel events.
        if not hasattr(self, "column_canvas"):
            return
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.column_canvas.yview_scroll(delta, "units")

    def _on_column_shift_mousewheel(self, event):
        # Kept for future horizontal scrolling if the table ever grows wider.
        if not hasattr(self, "column_canvas"):
            return
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.column_canvas.xview_scroll(delta, "units")


    def _set_validation_rows(self, rows: List[tuple]):
        for child in self.validation_rows_frame.winfo_children():
            child.destroy()

        icons = {
            "File type": "▣",
            "Status": "✓",
            "Delimiter": "⋯",
            "Rows": "≡",
            "Columns": "▥",
            "Errors": "!",
            "Path": "⌂",
            "Classes": "▦",
            "Objects": "●",
            "Associations": "↔",
            "Links": "⛓",
            "Enums": "◇",
            "File": "▣",
        }

        icon_width = 38
        label_width = 165
        divider_x = icon_width + label_width

        for row_index, (key, value) in enumerate(rows):
            row_bg = "#FFFFFF" if row_index % 2 == 0 else "#F5F8FC"

            # pack(fill="x") makes every row span the full Validation card.
            row_frame = tk.Frame(
                self.validation_rows_frame,
                height=self.VALIDATION_ROW_HEIGHT,
                background=row_bg,
                bd=0,
                highlightthickness=0,
            )
            row_frame.pack(
                fill="x",
                expand=False,
            )
            row_frame.pack_propagate(False)

            icon_cell = tk.Frame(
                row_frame,
                width=icon_width,
                height=self.VALIDATION_ROW_HEIGHT,
                background=row_bg,
                bd=0,
                highlightthickness=0,
            )
            icon_cell.place(
                x=0,
                y=0,
                width=icon_width,
                height=self.VALIDATION_ROW_HEIGHT,
            )

            status_is_ready = key == "Status" and str(value) == "Ready"
            status_is_blocked = key == "Status" and str(value) == "Blocked"

            ctk.CTkLabel(
                icon_cell,
                text=icons.get(str(key), "•"),
                text_color=(
                    self.colors["success"]
                    if status_is_ready
                    else self.colors["danger"]
                    if status_is_blocked
                    else self.colors["primary"]
                ),
                font=ctk.CTkFont(
                    family="Segoe UI Symbol",
                    size=13,
                    weight="bold",
                ),
            ).place(relx=0.5, rely=0.5, anchor="center")

            label_cell = tk.Frame(
                row_frame,
                width=label_width,
                height=self.VALIDATION_ROW_HEIGHT,
                background=row_bg,
                bd=0,
                highlightthickness=0,
            )
            label_cell.place(
                x=icon_width,
                y=0,
                width=label_width,
                height=self.VALIDATION_ROW_HEIGHT,
            )

            ctk.CTkLabel(
                label_cell,
                text=str(key),
                anchor="w",
                justify="left",
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold",
                ),
            ).place(x=8, rely=0.5, anchor="w")

            # One light divider between label and value.
            tk.Frame(
                row_frame,
                width=1,
                height=self.VALIDATION_ROW_HEIGHT,
                background="#DCE6F2",
                bd=0,
                highlightthickness=0,
            ).place(
                x=divider_x,
                y=0,
                width=1,
                height=self.VALIDATION_ROW_HEIGHT,
            )

            # Value area stretches from the divider to the right edge.
            value_cell = tk.Frame(
                row_frame,
                height=self.VALIDATION_ROW_HEIGHT,
                background=row_bg,
                bd=0,
                highlightthickness=0,
            )
            value_cell.place(
                x=divider_x + 1,
                y=0,
                relwidth=1.0,
                width=-(divider_x + 1),
                height=self.VALIDATION_ROW_HEIGHT,
            )

            is_error = key == "Errors" and str(value) != "None"
            ctk.CTkLabel(
                value_cell,
                text=str(value),
                anchor="w",
                justify="left",
                text_color=(
                    self.colors["danger"]
                    if is_error or status_is_blocked
                    else self.colors["success"]
                    if status_is_ready
                    else self.colors["text"]
                ),
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold" if key == "Status" else "normal",
                ),
            ).place(
                x=12,
                rely=0.5,
                anchor="w",
            )

    def _column_table_total_width(self) -> int:
        if hasattr(self, "column_canvas"):
            current_width = self.column_canvas.winfo_width()
            if current_width > 1:
                return current_width
        return (
                self.COLUMN_WIDTH_INCLUDE
                + self.COLUMN_WIDTH_NAME
                + self.COLUMN_WIDTH_TYPE
                + self.COLUMN_WIDTH_EXAMPLES
        )

    def _reset_column_table(self, total_height: int):
        """Create a fresh full-width table without an outer border."""
        if self.column_table is not None:
            self.column_table.destroy()

        self.column_canvas.update_idletasks()
        total_width = max(
            self.column_canvas.winfo_width(),
            self.COLUMN_WIDTH_INCLUDE
            + self.COLUMN_WIDTH_NAME
            + self.COLUMN_WIDTH_TYPE
            + 360,
            )

        self.column_table = tk.Frame(
            self.column_canvas,
            background="#FFFFFF",
            height=total_height,
            bd=0,
            highlightthickness=0,
        )

        # Stable first columns; Example Values receives the remaining width.
        self.column_table.grid_columnconfigure(
            0,
            weight=0,
            minsize=self.COLUMN_WIDTH_INCLUDE,
        )
        self.column_table.grid_columnconfigure(
            1,
            weight=0,
            minsize=self.COLUMN_WIDTH_NAME,
        )
        self.column_table.grid_columnconfigure(
            2,
            weight=0,
            minsize=self.COLUMN_WIDTH_TYPE,
        )
        self.column_table.grid_columnconfigure(
            3,
            weight=1,
            minsize=360,
        )

        self.column_canvas.delete("all")
        self.column_canvas_window = self.column_canvas.create_window(
            (0, 0),
            window=self.column_table,
            anchor="nw",
            width=total_width,
            height=total_height,
        )

        self.column_canvas.configure(
            scrollregion=(0, 0, total_width, total_height)
        )
        self.column_canvas.yview_moveto(0)

        def _fit_table_to_canvas(event):
            fitted_width = max(
                event.width,
                self.COLUMN_WIDTH_INCLUDE
                + self.COLUMN_WIDTH_NAME
                + self.COLUMN_WIDTH_TYPE
                + 360,
                )
            self.column_canvas.itemconfigure(
                self.column_canvas_window,
                width=fitted_width,
            )
            self.column_canvas.configure(
                scrollregion=(0, 0, fitted_width, total_height)
            )

        self.column_canvas.bind("<Configure>", _fit_table_to_canvas)

    def _make_table_cell(
            self,
            row: int,
            column: int,
            height: int,
            background: str,
            border_left: bool = False,
    ):
        cell = tk.Frame(
            self.column_table,
            height=height,
            background=background,
            highlightthickness=0,
            bd=0,
        )
        cell.grid(row=row, column=column, sticky="nsew")
        cell.grid_propagate(False)

        if border_left:
            separator = tk.Frame(
                cell,
                width=1,
                background="#DCE6F2",
                bd=0,
                highlightthickness=0,
            )
            separator.place(x=0, y=0, width=1, height=height)

        return cell

    def _build_column_table_header(self):
        header_bg = "#DCEAFF"
        specs = (
            (0, "include", "All"),
            (1, "label", "Column Name"),
            (2, "label", "Detected Data Type"),
            (3, "label", "Example Values"),
        )

        self.column_table.grid_rowconfigure(
            0,
            weight=0,
            minsize=self.TABLE_HEADER_HEIGHT,
        )

        for column, cell_type, text in specs:
            cell = self._make_table_cell(
                row=0,
                column=column,
                height=self.TABLE_HEADER_HEIGHT,
                background=header_bg,
                border_left=column > 0,
            )

            if cell_type == "include":
                # A separate checkbox and label are placed in one centered
                # group. This avoids CTkCheckBox centering only its text.
                all_group = tk.Frame(
                    cell,
                    background=header_bg,
                    bd=0,
                    highlightthickness=0,
                )
                all_group.place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center",
                )

                self.select_all_columns_checkbox = ctk.CTkCheckBox(
                    all_group,
                    text="",
                    variable=self.all_columns_selected_var,
                    width=21,
                    height=21,
                    checkbox_width=21,
                    checkbox_height=21,
                    corner_radius=4,
                    border_width=2,
                    border_color="#315D9B",
                    fg_color=self.colors["primary"],
                    hover_color=self.colors["primary_hover"],
                    command=self._toggle_all_columns,
                )
                self.select_all_columns_checkbox.pack(
                    side="left",
                    padx=(0, 6),
                )

                all_label = ctk.CTkLabel(
                    all_group,
                    text="All",
                    text_color="#17365D",
                    font=ctk.CTkFont(
                        family="Segoe UI",
                        size=12,
                        weight="bold",
                    ),
                )
                all_label.pack(side="left")
                all_label.bind(
                    "<Button-1>",
                    lambda _event: self._toggle_all_columns_from_label(),
                )
            else:
                ctk.CTkLabel(
                    cell,
                    text=text,
                    anchor="center",
                    justify="center",
                    text_color="#17365D",
                    font=ctk.CTkFont(
                        family="Segoe UI",
                        size=12,
                        weight="bold",
                    ),
                ).place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center",
                )

    def _render_csv_mapping(self, preview: CsvImportPreview):
        self.selected_csv_columns.clear()
        self.all_columns_selected_var.set(True)

        row_count = len(preview.header)
        total_height = (
                self.TABLE_HEADER_HEIGHT
                + row_count * self.TABLE_ROW_HEIGHT
        )

        self._reset_column_table(total_height)
        self._build_column_table_header()

        helper_model = FmmlxModel()

        for column_index, column_name in enumerate(preview.header):
            values = [
                row[column_index]
                for row in preview.data_rows
                if column_index < len(row)
            ]
            data_type = helper_model._get_csv_attribute_type(values).split("::")[-1]
            selected = tk.BooleanVar(value=True)
            self.selected_csv_columns[column_name] = selected

            row_number = column_index + 1
            row_color = "#FFFFFF" if column_index % 2 == 0 else "#F3F7FD"

            self.column_table.grid_rowconfigure(
                row_number,
                weight=0,
                minsize=self.TABLE_ROW_HEIGHT,
            )

            include_cell = self._make_table_cell(
                row=row_number,
                column=0,
                height=self.TABLE_ROW_HEIGHT,
                background=row_color,
            )
            checkbox = ctk.CTkCheckBox(
                include_cell,
                text="",
                variable=selected,
                width=22,
                height=22,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=4,
                border_width=2,
                border_color="#4F78B8",
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                command=self._on_column_checkbox_changed,
            )
            checkbox.place(relx=0.5, rely=0.5, anchor="center")

            name_cell = self._make_table_cell(
                row=row_number,
                column=1,
                height=self.TABLE_ROW_HEIGHT,
                background=row_color,
                border_left=True,
            )
            ctk.CTkLabel(
                name_cell,
                text=column_name,
                anchor="center",
                justify="center",
                text_color=self.colors["text"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).place(relx=0.5, rely=0.5, anchor="center")

            type_cell = self._make_table_cell(
                row=row_number,
                column=2,
                height=self.TABLE_ROW_HEIGHT,
                background=row_color,
                border_left=True,
            )
            ctk.CTkLabel(
                type_cell,
                text=data_type,
                height=26,
                corner_radius=13,
                fg_color="#E7F0FF",
                text_color="#2457A6",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=11,
                    weight="bold",
                ),
            ).place(relx=0.5, rely=0.5, anchor="center")

            examples_cell = self._make_table_cell(
                row=row_number,
                column=3,
                height=self.TABLE_ROW_HEIGHT,
                background=row_color,
                border_left=True,
            )
            ctk.CTkLabel(
                examples_cell,
                text=self._format_example_values(values),
                anchor="center",
                justify="center",
                text_color="#334155",
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).place(
                relx=0.5,
                rely=0.5,
                anchor="center",
                relwidth=0.94,
            )

        self.column_canvas.update_idletasks()
        fitted_width = max(
            self.column_canvas.winfo_width(),
            self.COLUMN_WIDTH_INCLUDE
            + self.COLUMN_WIDTH_NAME
            + self.COLUMN_WIDTH_TYPE
            + 360,
            )
        self.column_canvas.itemconfigure(
            self.column_canvas_window,
            width=fitted_width,
            height=total_height,
        )
        self.column_canvas.configure(
            scrollregion=(0, 0, fitted_width, total_height)
        )
        self.column_canvas.yview_moveto(0)

    def _format_example_values(
            self,
            values: List[str],
            max_chars: int = 58,
    ) -> str:
        cleaned_values = [
            str(value).strip()
            for value in values
            if str(value).strip()
        ]

        if not cleaned_values:
            return "—"

        selected_values: List[str] = []
        current_length = 0

        for value in cleaned_values:
            separator_length = 2 if selected_values else 0
            remaining = max_chars - current_length - separator_length

            if remaining <= 0:
                break

            # A single long value is shortened so that every populated
            # column still shows at least one example.
            if not selected_values and len(value) > remaining:
                shortened = value[: max(1, remaining - 1)].rstrip()
                selected_values.append(shortened + "…")
                current_length = max_chars
                break

            if len(value) > remaining:
                break

            selected_values.append(value)
            current_length += separator_length + len(value)

        if not selected_values:
            first_value = cleaned_values[0]
            return (
                first_value
                if len(first_value) <= max_chars
                else first_value[: max_chars - 1].rstrip() + "…"
            )

        result = ", ".join(selected_values)
        if len(selected_values) < len(cleaned_values) and not result.endswith("…"):
            if len(result) + 3 <= max_chars:
                result += ", …"
            else:
                result = result[: max_chars - 1].rstrip(" ,") + "…"

        return result

    def _toggle_all_columns_from_label(self):
        self.all_columns_selected_var.set(
            not self.all_columns_selected_var.get()
        )
        self._toggle_all_columns()

    def _toggle_all_columns(self):
        selected = self.all_columns_selected_var.get()
        for variable in self.selected_csv_columns.values():
            variable.set(selected)
        self._set_create_button_enabled(self._has_selected_columns())

    def _toggle_column_selection_size(self):
        self.column_selection_expanded = not self.column_selection_expanded

        if self.column_selection_expanded:
            self.file_card.grid_remove()
            self.validation_card.grid_remove()
            self.expand_columns_button.configure(text="Collapse  ↓")
            self.column_canvas.configure(height=560)
        else:
            self.file_card.grid()
            self.validation_card.grid()
            self.expand_columns_button.configure(text="Expand  ↑")
            self.column_canvas.configure(height=290)


    def _on_column_checkbox_changed(self):
        values = [var.get() for var in self.selected_csv_columns.values()]
        self.all_columns_selected_var.set(bool(values) and all(values))
        self._set_create_button_enabled(self._has_selected_columns())


    def _can_create_current_file(self) -> bool:
        extension = os.path.splitext(self.current_file_path or "")[1].lower()
        if extension == ".csv":
            return self._has_selected_columns()
        if extension == ".xml":
            return self.xml_preview is not None and not self.xml_preview.errors
        return False

    def _has_selected_columns(self) -> bool:
        if self.csv_preview is None or self.csv_preview.errors or not self.csv_preview.header_detected:
            return False
        return any(var.get() for var in self.selected_csv_columns.values())


    def _render_csv_preview(self, preview: CsvImportPreview):
        # The compact preview is shown directly in the Example Values column.
        return

    def _render_xml_preview(self, preview: XmlImportPreview):
        for child in self.column_table.winfo_children():
            child.destroy()

        self._build_column_table_header()

        model = preview.model
        if model is None:
            return

        xml_rows = [
            ("Model path", model.path_name),
            ("Classes", len(model.get_all_flat_classes())),
            ("Objects", len(model.get_all_pure_objects())),
            ("Attributes", self._count_attributes(model)),
            ("Slots", self._count_slots(model)),
            ("Associations", len(model.associations)),
            ("Links", len(model.links)),
            ("Enums", len(model.enums)),
        ]

        for index, (label, value) in enumerate(xml_rows, start=1):
            row_color = "#FFFFFF" if index % 2 else "#F3F7FD"

            label_cell = ctk.CTkFrame(
                self.column_table,
                fg_color=row_color,
                corner_radius=0,
                height=48,
            )
            label_cell.grid(row=index, column=0, columnspan=3, sticky="nsew")
            label_cell.grid_propagate(False)
            label_cell.grid_rowconfigure(0, weight=1)
            label_cell.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                label_cell,
                text=str(label),
                anchor="center",
                justify="center",
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold",
                ),
            ).grid(row=0, column=0, sticky="nsew", padx=14)

            self._add_column_separator(index, 3)

            value_cell = ctk.CTkFrame(
                self.column_table,
                fg_color=row_color,
                corner_radius=0,
                height=48,
            )
            value_cell.grid(row=index, column=4, columnspan=3, sticky="nsew")
            value_cell.grid_propagate(False)
            value_cell.grid_rowconfigure(0, weight=1)
            value_cell.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                value_cell,
                text=str(value),
                anchor="center",
                justify="center",
                text_color="#334155",
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).grid(row=0, column=0, sticky="nsew", padx=14)

    def _render_empty_preview(self, text: str):
        if not hasattr(self, "column_canvas"):
            return

        total_height = self.TABLE_HEADER_HEIGHT + 76
        self._reset_column_table(total_height)
        self._build_column_table_header()

        self.column_table.grid_rowconfigure(
            1,
            weight=0,
            minsize=76,
        )

        empty_cell = tk.Frame(
            self.column_table,
            height=76,
            background="#FFFFFF",
            bd=0,
            highlightthickness=0,
        )
        empty_cell.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="nsew",
        )
        empty_cell.grid_propagate(False)

        ctk.CTkLabel(
            empty_cell,
            text=text,
            anchor="center",
            justify="center",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _clear_preview_container(self):
        if not hasattr(self, "column_table"):
            return
        for child in self.column_table.winfo_children():
            child.destroy()

    def _attach_scrollbars(self, parent, table: ttk.Treeview, row: int = 0, padx: int = 0, bottom: int = 0):
        y_scroll = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        x_scroll = ttk.Scrollbar(parent, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=row, column=1, sticky="ns", pady=(0, bottom))
        x_scroll.grid(row=row + 1, column=0, sticky="ew", padx=padx)

    def _create_model(self):
        if not self.current_file_path:
            messagebox.showerror("Import blocked", "Select a file first.")
            return

        try:
            extension = os.path.splitext(self.current_file_path)[1].lower()
            if extension == ".csv":
                selected_columns = [
                    column
                    for column, selected in self.selected_csv_columns.items()
                    if selected.get()
                ]

                if not selected_columns:
                    messagebox.showerror(
                        "Import blocked",
                        "Select at least one CSV column.",
                    )
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

        self.step_completed[1] = True
        self.step_unlocked[2] = True
        self._store_loaded_model(extension)
        self._show_model_page()

    def _store_loaded_model(self, extension: str):
        if self.current_model is None or self.current_file_path is None:
            return
        source_file = os.path.basename(self.current_file_path)
        name = self.current_model.path_name.split("::")[-1] if self.current_model.path_name else os.path.splitext(source_file)[0]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.loaded_models.append(
            LoadedModel(
                name=name,
                source_file=source_file,
                file_type=extension.lstrip(".").upper(),
                model=self.current_model,
                uploaded=timestamp,
                last_worked_on=timestamp,
            )
        )

    def _touch_loaded_model(self, loaded: LoadedModel):
        loaded.last_worked_on = datetime.now().strftime("%Y-%m-%d %H:%M")


    def _format_file_modified_time(self, file_path: str) -> str:
        try:
            return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(
                "%Y-%m-%d %H:%M"
            )
        except OSError:
            return "Unknown"

    def _populate_model_tree(
            self,
            model: FmmlxModel,
            query: str = "",
    ):
        self.tree_item_payload.clear()
        self._clear_tree(self.model_tree)

        normalized_query = query.strip().lower()

        root_text = model.path_name or os.path.basename(
            self.current_file_path or "Model"
        )
        root_id = self.model_tree.insert(
            "",
            "end",
            text=f"Model: {root_text}",
            open=True,
            tags=("model_root",),
        )
        self.tree_item_payload[root_id] = model

        level_1_objects = [
            obj
            for obj in model.mlm_objects
            if obj.level == 1
               and (
                       not normalized_query
                       or normalized_query in obj.name.lower()
               )
        ]
        level_0_objects = [
            obj
            for obj in model.mlm_objects
            if obj.level == 0
               and (
                       not normalized_query
                       or normalized_query in obj.name.lower()
               )
        ]

        level_1_id = self.model_tree.insert(
            root_id,
            "end",
            text=f"Level 1 ({len(level_1_objects)})",
            open=True,
            tags=("level_class",),
        )
        self.tree_item_payload[level_1_id] = None

        for obj in sorted(
                level_1_objects,
                key=lambda item: self._natural_sort_key(item.name),
        ):
            obj_id = self.model_tree.insert(
                level_1_id,
                "end",
                text=obj.name,
                open=False,
                tags=("class_item",),
            )
            self.tree_item_payload[obj_id] = obj

        level_0_id = self.model_tree.insert(
            root_id,
            "end",
            text=f"Level 0 ({len(level_0_objects)})",
            open=True,
            tags=("level_object",),
        )
        self.tree_item_payload[level_0_id] = None

        for obj in sorted(
                level_0_objects,
                key=lambda item: self._natural_sort_key(item.name),
        ):
            obj_id = self.model_tree.insert(
                level_0_id,
                "end",
                text=obj.name,
                open=False,
                tags=("object_item",),
            )
            self.tree_item_payload[obj_id] = obj

        self.model_tree.selection_remove(
            self.model_tree.selection()
        )
        self.model_tree.yview_moveto(0)

    def _filter_model_tree(self, _event=None):
        if self.current_model is None:
            return

        query = self.model_search_var.get()
        self._cancel_detail_loading()
        self._populate_model_tree(
            self.current_model,
            query=query,
        )
        self._render_empty_detail_state()

    def _show_selected_details(self, _event):
        selected = self.model_tree.selection()
        if not selected:
            self._cancel_detail_loading()
            self._render_empty_detail_state()
            return

        payload = self.tree_item_payload.get(selected[0])
        self._cancel_detail_loading()

        if isinstance(payload, FmmlxModel):
            self._start_model_overview_loading(payload)
        elif isinstance(payload, FmmlxObject):
            if payload.level > 0:
                self._render_class_details(payload)
            else:
                self._render_object_details(payload)
        else:
            self._render_empty_detail_state()

    def _cancel_detail_loading(self):
        self._detail_load_token = getattr(self, "_detail_load_token", 0) + 1

        batch_id = getattr(self, "_detail_batch_after_id", None)
        if batch_id is not None:
            try:
                self.after_cancel(batch_id)
            except Exception:
                pass
            self._detail_batch_after_id = None

        staging_table = getattr(self, "_detail_staging_table", None)
        staging_was_current = (
            staging_table is not None
            and getattr(self, "detail_table", None) is staging_table
        )
        if staging_table is not None and staging_table.winfo_exists():
            staging_table.destroy()
        self._detail_staging_table = None
        staging_window = getattr(self, "_detail_staging_window", None)
        if staging_window is not None and hasattr(self, "detail_canvas"):
            try:
                self.detail_canvas.delete(staging_window)
            except Exception:
                pass
        self._detail_staging_window = None
        self._pending_overview_rows = []

        overlay = getattr(self, "_detail_loading_overlay", None)
        if overlay is not None and overlay.winfo_exists():
            try:
                if hasattr(self, "detail_loading_bar"):
                    self.detail_loading_bar.stop()
            except Exception:
                pass
            overlay.destroy()
        self._detail_loading_overlay = None
        toolbar = getattr(self, "_detail_overview_toolbar", None)
        if toolbar is not None and toolbar.winfo_exists():
            toolbar.destroy()
        self._detail_overview_toolbar = None
        self._detail_progress_determinate = False
        overview_canvas_was_current = getattr(
            self,
            "_detail_canvas_overview_loading",
            False,
        )
        self._detail_canvas_overview_loading = False
        if staging_was_current or overview_canvas_was_current or (
            hasattr(self, "detail_table")
            and not self.detail_table.winfo_exists()
        ):
            self._reset_detail_canvas_table()

    def _schedule_detail_batch(self, token: int, delay_ms: int, callback):
        if token != getattr(self, "_detail_load_token", None):
            return
        self._detail_batch_after_id = self.after(delay_ms, callback)

    def _start_model_overview_loading(self, model: FmmlxModel):
        self._show_model_overview_load_options(model)

    def _show_model_overview_load_options(self, model: FmmlxModel):
        self._detail_load_token = getattr(self, "_detail_load_token", 0) + 1

        self.detail_title.configure(
            text="Model Overview",
            text_color=self.colors["text"],
        )
        self.detail_subtitle.configure(
            text="Choose how many objects should be loaded into the overview."
        )

        class_objects = [
            obj
            for obj in model.mlm_objects
            if obj.level > 0 and obj.attr_list
        ]
        attributes = class_objects[0].attr_list if class_objects else []
        objects = [
            obj
            for obj in model.mlm_objects
            if obj.level == 0
        ]
        objects = sorted(
            objects,
            key=lambda item: self._natural_sort_key(item.name),
        )

        self._reset_detail_canvas_table()
        for child in self.detail_table.winfo_children():
            child.destroy()

        panel = ctk.CTkFrame(
            self.detail_table,
            fg_color=self.colors["surface_alt"],
            corner_radius=8,
            border_width=1,
            border_color="#D8E3F5",
        )
        panel.grid(row=0, column=0, sticky="new", padx=18, pady=18)
        panel.grid_columnconfigure(1, weight=1)

        total_objects = len(objects)
        total_cells = (total_objects + 1) * (len(attributes) + 1)

        ctk.CTkLabel(
            panel,
            text="Load model overview",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            panel,
            text=f"The model contains {total_objects} objects and {total_cells} cells if fully loaded.",
            text_color=self.colors["muted"],
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 16))

        ctk.CTkLabel(
            panel,
            text="Number of objects",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).grid(row=2, column=0, sticky="w", padx=(18, 14), pady=(0, 12))

        self.model_overview_count_var = tk.StringVar(
            value=str(min(total_objects, 200))
        )
        count_entry = ctk.CTkEntry(
            panel,
            textvariable=self.model_overview_count_var,
            width=120,
            height=34,
            corner_radius=7,
            border_color="#BBD0F4",
            fg_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        count_entry.grid(row=2, column=1, sticky="w", padx=(0, 18), pady=(0, 12))

        ctk.CTkLabel(
            panel,
            text="Selection",
            text_color=self.colors["text"],
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).grid(row=3, column=0, sticky="w", padx=(18, 14), pady=(0, 18))

        self.model_overview_selection_var = tk.StringVar(value="From start")
        selection_frame = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )
        selection_frame.grid(row=3, column=1, sticky="w", padx=(0, 18), pady=(0, 18))
        self._model_overview_mode_buttons = {}
        for index, label in enumerate(("From start", "From end", "Random")):
            button = ctk.CTkButton(
                selection_frame,
                text=label,
                width=92,
                height=32,
                corner_radius=7,
                border_width=1,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda value=label: self._set_model_overview_selection_mode(value),
            )
            button.grid(row=0, column=index, padx=(0 if index == 0 else 8, 0))
            self._model_overview_mode_buttons[label] = button
        self._set_model_overview_selection_mode("From start")

        ctk.CTkButton(
            panel,
            text="Load Overview",
            width=150,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: self._start_model_overview_loading_with_options(
                model=model,
                attributes=attributes,
                objects=objects,
            ),
        ).grid(row=4, column=1, sticky="w", padx=(0, 18), pady=(0, 18))

        self.detail_table.update_idletasks()
        self.detail_canvas.itemconfigure(
            self.detail_canvas_window,
            width=max(self.detail_canvas.winfo_width(), 700),
        )
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))
        self.detail_canvas.xview_moveto(0)
        self.detail_canvas.yview_moveto(0)

    def _set_model_overview_selection_mode(self, value: str):
        self.model_overview_selection_var.set(value)
        buttons = getattr(self, "_model_overview_mode_buttons", {})
        for label, button in buttons.items():
            if label == value:
                button.configure(
                    fg_color=self.colors["primary"],
                    hover_color=self.colors["primary_hover"],
                    border_color=self.colors["primary"],
                    text_color="#FFFFFF",
                )
            else:
                button.configure(
                    fg_color="#FFFFFF",
                    hover_color="#EEF4FF",
                    border_color="#BBD0F4",
                    text_color=self.colors["text"],
                )

    def _start_model_overview_loading_with_options(
            self,
            model: FmmlxModel,
            attributes: List[FmmlxAttribute],
            objects: List[FmmlxObject],
    ):
        try:
            requested_count = int(self.model_overview_count_var.get().strip())
        except ValueError:
            messagebox.showerror(
                "Invalid object count",
                "Enter a whole number of objects to load.",
            )
            return

        if requested_count <= 0:
            messagebox.showerror(
                "Invalid object count",
                "Enter at least 1 object to load.",
            )
            return

        selected_objects = self._select_model_overview_objects(
            objects=objects,
            count=min(requested_count, len(objects)),
            mode={
                "From start": "from_start",
                "From end": "from_end",
                "Random": "random",
            }.get(self.model_overview_selection_var.get(), "from_start"),
        )
        self._current_overview_model = model
        self._current_overview_attributes = attributes
        self._current_overview_objects = objects

        self._detail_load_token = getattr(self, "_detail_load_token", 0) + 1
        token = self._detail_load_token

        self.detail_title.configure(
            text="Model Overview",
            text_color=self.colors["text"],
        )
        self.detail_subtitle.configure(
            text="Preparing the complete model overview."
        )

        self._reset_detail_canvas_table()
        self._pending_overview_rows = []
        self._pending_overview_model_name = self._model_overview_display_name(model)
        self._pending_overview_attributes = attributes
        self._detail_progress_loaded = 0
        self._detail_progress_total = len(selected_objects)
        self._detail_progress_work_loaded = 0
        self._detail_progress_work_total = max(
            1,
            (len(selected_objects) + 1) * (len(attributes) + 1),
        )
        self._detail_progress_determinate = True

        self._show_model_loading_progress(
            token=token,
            total=self._detail_progress_work_total,
        )

        self._schedule_detail_batch(
            token,
            1,
            lambda: self._prepare_model_overview_batch(
                token=token,
                attributes=attributes,
                objects=selected_objects,
                start_index=0,
            ),
        )

    def _select_model_overview_objects(
            self,
            objects: List[FmmlxObject],
            count: int,
            mode: str,
    ) -> List[FmmlxObject]:
        if mode == "from_end":
            return objects[-count:]
        if mode == "random":
            return sorted(
                random.sample(objects, count),
                key=lambda item: self._natural_sort_key(item.name),
            )
        return objects[:count]

    def _show_model_loading_progress(self, token: int, total: int):
        if token != getattr(self, "_detail_load_token", None):
            return

        existing = getattr(self, "_detail_loading_overlay", None)
        if existing is not None and existing.winfo_exists():
            existing.destroy()

        overlay = ctk.CTkFrame(
            self.detail_table_wrapper,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=0,
        )
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.grid_columnconfigure(0, weight=1)
        overlay.grid_rowconfigure(0, weight=1)

        loading_panel = ctk.CTkFrame(
            overlay,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"],
            height=230,
        )
        loading_panel.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.68,
        )
        loading_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            loading_panel,
            text="Loading data…",
            text_color=self.colors["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=17,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=0,
            pady=(26, 6),
        )

        self.detail_loading_message_label = ctk.CTkLabel(
            loading_panel,
            text="Preparing the complete model overview. Please wait…",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.detail_loading_message_label.grid(
            row=1,
            column=0,
            pady=(0, 18),
        )

        progress_row = ctk.CTkFrame(
            loading_panel,
            fg_color="transparent",
        )
        progress_row.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=34,
        )
        progress_row.grid_columnconfigure(0, weight=1)

        self.detail_loading_bar = ctk.CTkProgressBar(
            progress_row,
            mode="determinate",
            height=13,
            corner_radius=7,
            progress_color=self.colors["primary"],
        )
        self.detail_loading_bar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 14),
        )
        self.detail_loading_bar.set(0)

        self.detail_loading_total_label = ctk.CTkLabel(
            progress_row,
            text=f"Total: {total} cells",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
        )
        self.detail_loading_total_label.grid(
            row=0,
            column=1,
            sticky="e",
        )

        self.detail_loading_count_label = ctk.CTkLabel(
            loading_panel,
            text=f"0 of {total} cells loaded",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
            ),
        )
        self.detail_loading_count_label.grid(
            row=3,
            column=0,
            pady=(12, 0),
        )

        ctk.CTkButton(
            loading_panel,
            text="Cancel Loading",
            width=146,
            height=36,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#FEF2F2",
            border_width=1,
            border_color="#FCA5A5",
            text_color="#DC2626",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
            command=self._cancel_model_overview_loading,
        ).grid(
            row=4,
            column=0,
            pady=(18, 20),
        )

        self._detail_loading_overlay = overlay
        overlay.lift()

        # Force Tk to paint the loading layer before the first data batch starts.
        self.update_idletasks()

    def _refresh_determinate_progress_display(self, token: int):
        if token != getattr(self, "_detail_load_token", None):
            return
        if not getattr(self, "_detail_progress_determinate", False):
            return

        overlay = getattr(self, "_detail_loading_overlay", None)
        if overlay is None or not overlay.winfo_exists():
            return

        loaded = getattr(self, "_detail_progress_loaded", 0)
        total = getattr(self, "_detail_progress_total", 0)
        work_loaded = getattr(self, "_detail_progress_work_loaded", loaded)
        work_total = getattr(self, "_detail_progress_work_total", total)
        fraction = 1.0 if work_total == 0 else min(1.0, work_loaded / work_total)
        self.detail_loading_bar.set(fraction)
        self.detail_loading_message_label.configure(
            text="Preparing the complete model overview. Please wait…"
        )
        self.detail_loading_count_label.configure(
            text=f"{work_loaded} of {work_total} cells loaded"
        )

    def _cancel_model_overview_loading(self):
        self._cancel_detail_loading()
        self.detail_title.configure(
            text="Loading cancelled",
            text_color=self.colors["text"],
        )
        self.detail_subtitle.configure(
            text="Select the model again to restart loading."
        )

        for child in self.detail_table.winfo_children():
            child.destroy()

        ctk.CTkLabel(
            self.detail_table,
            text="Model overview loading was cancelled.",
            text_color=self.colors["muted"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=40,
        )

    def _update_model_loading_progress(
            self,
            token: int,
            loaded: int,
            total: int,
            phase: str = "loading",
            work_loaded: Optional[int] = None,
            work_total: Optional[int] = None,
    ):
        if token != getattr(self, "_detail_load_token", None):
            return

        self._detail_progress_total = total
        if work_loaded is None:
            work_loaded = loaded
        if work_total is None:
            work_total = max(1, total)
        self._detail_progress_work_loaded = min(work_loaded, work_total)
        self._detail_progress_work_total = max(1, work_total)
        self._detail_progress_loaded = loaded
        self._refresh_determinate_progress_display(token)

    def _prepare_model_overview_batch(
            self,
            token: int,
            attributes: List[FmmlxAttribute],
            objects: List[FmmlxObject],
            start_index: int,
    ):
        self._detail_batch_after_id = None
        if token != getattr(self, "_detail_load_token", None):
            return

        batch_size = 40
        end_index = min(start_index + batch_size, len(objects))

        for object_index in range(start_index, end_index):
            obj = objects[object_index]
            slot_by_name = {
                slot.name: slot.value
                for slot in obj.slot_list
            }
            row_values = [
                slot_by_name.get(attr.name, "")
                for attr in attributes
            ]
            self._pending_overview_rows.append(
                (obj.name, row_values)
            )

        self._update_model_loading_progress(
            token=token,
            loaded=end_index,
            total=len(objects),
            phase="preparing",
            work_loaded=0,
            work_total=getattr(self, "_detail_progress_work_total", len(objects)),
        )

        if end_index < len(objects):
            self._schedule_detail_batch(
                token,
                1,
                lambda: self._prepare_model_overview_batch(
                    token=token,
                    attributes=attributes,
                    objects=objects,
                    start_index=end_index,
                ),
            )
        else:
            self._finish_preparing_model_overview(token)

    def _finish_preparing_model_overview(self, token: int):
        if token != getattr(self, "_detail_load_token", None):
            return

        self._begin_prepared_model_overview_render(
            token=token,
            model_name=self._pending_overview_model_name,
            attributes=self._pending_overview_attributes,
            prepared_rows=self._pending_overview_rows,
        )

    def _render_model_overview(self, model: FmmlxModel):
        self._start_model_overview_loading(model)

    def _render_prepared_model_overview_table(
            self,
            model_name: str,
            attributes: List[FmmlxAttribute],
            prepared_rows: list,
    ):
        # Compatibility entry point.
        token = getattr(self, "_detail_load_token", 0)
        self._begin_prepared_model_overview_render(
            token=token,
            model_name=model_name,
            attributes=attributes,
            prepared_rows=prepared_rows,
        )

    def _begin_prepared_model_overview_render(
            self,
            token: int,
            model_name: str,
            attributes: List[FmmlxAttribute],
            prepared_rows: list,
    ):
        if token != getattr(self, "_detail_load_token", None):
            return

        name_width = 220
        attribute_width = 180
        header_height = 42
        row_height = 46
        total_width = max(
            name_width + len(attributes) * attribute_width,
            self.detail_canvas.winfo_width(),
            )
        total_cells = (len(prepared_rows) + 1) * (len(attributes) + 1)
        total_work = max(1, total_cells)

        try:
            self.detail_table.destroy()
        except Exception:
            pass
        self.detail_canvas.delete("all")
        self.detail_canvas.configure(scrollregion=(0, 0, 0, 0))
        self.detail_table = tk.Frame(
            self.detail_canvas,
            background="#FFFFFF",
            bd=0,
            highlightthickness=0,
        )
        self.detail_canvas_window = None
        self._detail_staging_table = None
        self._detail_staging_window = None
        self._detail_canvas_overview_loading = True
        overlay = getattr(self, "_detail_loading_overlay", None)
        if overlay is not None and overlay.winfo_exists():
            overlay.lift()

        headers = [model_name] + [attr.name for attr in attributes]
        x = 0
        for column, text in enumerate(headers):
            column_width = name_width if column == 0 else attribute_width
            self._draw_model_overview_cell(
                x=x,
                y=0,
                width=column_width,
                height=header_height,
                text=text,
                background="#DCEAFF",
                foreground="#17365D",
                font=("Segoe UI", 12, "bold"),
                tags=("overview_corner",) if column == 0 else ("overview_header",),
            )
            x += column_width

        state = {
            "name_width": name_width,
            "attribute_width": attribute_width,
            "header_height": header_height,
            "row_height": row_height,
            "total_width": total_width,
            "column_count": len(attributes) + 1,
            "total_cells": total_cells,
            "total_work": total_work,
        }

        row_heights = []
        row_offsets = []
        current_y = header_height
        for object_name, row_values in prepared_rows:
            row_offsets.append(current_y)
            dynamic_height = self._model_overview_row_height(
                object_name=object_name,
                row_values=row_values,
                state=state,
            )
            row_heights.append(dynamic_height)
            current_y += dynamic_height
        state["row_heights"] = row_heights
        state["row_offsets"] = row_offsets
        state["total_height"] = current_y

        self._detail_progress_loaded = 0
        self._detail_progress_total = len(prepared_rows)
        self._detail_progress_work_loaded = len(headers)
        self._detail_progress_work_total = total_work
        self._overview_sticky_x = 0
        self._overview_sticky_y = 0
        self._refresh_determinate_progress_display(token)

        self._schedule_detail_batch(
            token,
            1,
            lambda: self._render_prepared_overview_batch(
                token=token,
                prepared_rows=prepared_rows,
                state=state,
                start_index=0,
            ),
        )

    def _draw_model_overview_cell(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            text: object,
            background: str,
            foreground: str,
            font,
            tags=(),
    ):
        self.detail_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=background,
            outline="#E4EBF4",
            width=1,
            tags=tags,
        )
        self.detail_canvas.create_text(
            x + (width / 2),
            y + (height / 2),
            text="" if text is None else str(text),
            fill=foreground,
            font=font,
            anchor="center",
            justify="center",
            width=max(20, width - 18),
            tags=tags,
        )

    def _wrapped_line_count(self, text: object, width: int, font) -> int:
        value = "" if text is None else str(text)
        if not value:
            return 1

        measure_font = tkfont.Font(self.detail_canvas, font=font)
        available_width = max(20, width - 18)
        lines = 0

        for paragraph in value.splitlines() or [""]:
            words = paragraph.split()
            if not words:
                lines += 1
                continue

            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if measure_font.measure(candidate) <= available_width:
                    current = candidate
                    continue

                if current:
                    lines += 1
                    current = word
                while measure_font.measure(current) > available_width and len(current) > 1:
                    split_at = max(1, len(current) - 1)
                    while (
                            split_at > 1
                            and measure_font.measure(current[:split_at]) > available_width
                    ):
                        split_at -= 1
                    lines += 1
                    current = current[split_at:]

            if current:
                lines += 1

        return max(1, lines)

    def _model_overview_row_height(
            self,
            object_name: str,
            row_values: List[object],
            state: dict,
    ) -> int:
        line_counts = [
            self._wrapped_line_count(
                object_name,
                state["name_width"],
                ("Segoe UI", 12, "bold"),
            )
        ]
        for value in row_values:
            line_counts.append(
                self._wrapped_line_count(
                    value,
                    state["attribute_width"],
                    ("Segoe UI", 12),
                )
            )
        return max(state["row_height"], (max(line_counts) * 18) + 18)

    def _render_prepared_overview_batch(
            self,
            token: int,
            prepared_rows: list,
            state: dict,
            start_index: int,
    ):
        self._detail_batch_after_id = None
        if token != getattr(self, "_detail_load_token", None):
            return

        # Canvas items are much lighter than per-cell Tk widgets, so larger
        # batches remain responsive and avoid widget resource exhaustion.
        batch_size = 40
        end_index = min(start_index + batch_size, len(prepared_rows))

        for object_index in range(start_index, end_index):
            object_name, row_values = prepared_rows[object_index]
            row_index = object_index + 1
            row_bg = "#FFFFFF" if row_index % 2 else "#F3F7FD"
            y = state["row_offsets"][object_index]
            row_height = state["row_heights"][object_index]

            self._draw_model_overview_cell(
                x=0,
                y=y,
                width=state["name_width"],
                height=row_height,
                text=object_name,
                background=row_bg,
                foreground="#16A34A",
                font=("Segoe UI", 12, "bold"),
                tags=("overview_column",),
            )

            x = state["name_width"]
            for column, value in enumerate(row_values, start=1):
                self._draw_model_overview_cell(
                    x=x,
                    y=y,
                    width=state["attribute_width"],
                    height=row_height,
                    text="" if value is None else str(value),
                    background=row_bg,
                    foreground=self.colors["text"],
                    font=("Segoe UI", 12),
                )
                x += state["attribute_width"]

        loaded = end_index
        rendered_cells = state["column_count"] + (loaded * state["column_count"])
        work_loaded = rendered_cells
        self._update_model_loading_progress(
            token=token,
            loaded=loaded,
            total=len(prepared_rows),
            phase="loading",
            work_loaded=work_loaded,
            work_total=state["total_work"],
        )

        if end_index < len(prepared_rows):
            self._schedule_detail_batch(
                token,
                1,
                lambda: self._render_prepared_overview_batch(
                    token=token,
                    prepared_rows=prepared_rows,
                    state=state,
                    start_index=end_index,
                ),
            )
        else:
            self._finish_model_overview_render(
                token=token,
                state=state,
            )

    def _finish_model_overview_render(
            self,
            token: int,
            state: dict,
    ):
        if token != getattr(self, "_detail_load_token", None):
            return

        self.detail_canvas.configure(
            scrollregion=(
                0,
                0,
                state["total_width"],
                max(state["total_height"], 122),
            )
        )
        self.detail_canvas.xview_moveto(0)
        self.detail_canvas.yview_moveto(0)
        self._overview_sticky_x = 0
        self._overview_sticky_y = 0
        self._sync_model_overview_sticky_items()

        overlay = getattr(self, "_detail_loading_overlay", None)
        if overlay is not None and overlay.winfo_exists():
            overlay.destroy()
        self._detail_loading_overlay = None
        self._detail_canvas_overview_loading = False
        self.detail_subtitle.configure(
            text="Complete model overview loaded."
        )
        self._show_model_overview_loaded_toolbar()

    def _sync_model_overview_sticky_items(self):
        if not getattr(self, "_detail_canvas_overview_loading", False) and getattr(self, "_detail_overview_toolbar", None) is None:
            return
        if not hasattr(self, "detail_canvas"):
            return
        current_x = self.detail_canvas.canvasx(0)
        current_y = self.detail_canvas.canvasy(0)
        previous_x = getattr(self, "_overview_sticky_x", 0)
        previous_y = getattr(self, "_overview_sticky_y", 0)
        dx = current_x - previous_x
        dy = current_y - previous_y
        if dx:
            self.detail_canvas.move("overview_column", dx, 0)
            self.detail_canvas.move("overview_corner", dx, 0)
        if dy:
            self.detail_canvas.move("overview_header", 0, dy)
            self.detail_canvas.move("overview_corner", 0, dy)
        self._overview_sticky_x = current_x
        self._overview_sticky_y = current_y
        self.detail_canvas.tag_raise("overview_header")
        self.detail_canvas.tag_raise("overview_column")
        self.detail_canvas.tag_raise("overview_corner")

    def _show_model_overview_loaded_toolbar(self):
        existing = getattr(self, "_detail_overview_toolbar", None)
        if existing is not None and existing.winfo_exists():
            existing.destroy()

        toolbar = ctk.CTkFrame(
            self.detail_card,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D8E3F5",
        )
        toolbar.place(relx=1.0, y=12, anchor="ne", x=-16)

        ctk.CTkButton(
            toolbar,
            text="Change selection",
            width=142,
            height=32,
            corner_radius=7,
            fg_color="#FFFFFF",
            hover_color="#EEF4FF",
            border_width=1,
            border_color="#BBD0F4",
            text_color=self.colors["primary"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._return_to_model_overview_options,
        ).grid(row=0, column=0, padx=8, pady=8)

        self._detail_overview_toolbar = toolbar
        toolbar.lift()

    def _return_to_model_overview_options(self):
        model = getattr(self, "_current_overview_model", None)
        if model is None:
            return
        toolbar = getattr(self, "_detail_overview_toolbar", None)
        if toolbar is not None and toolbar.winfo_exists():
            toolbar.destroy()
        self._detail_overview_toolbar = None
        self._show_model_overview_load_options(model)


    def _render_empty_detail_state(self):
        self.detail_title.configure(
            text="Details",
            text_color=self.colors["text"],
        )
        self.detail_subtitle.configure(
            text="Select the model, a class, or an object to load its details."
        )
        self._render_detail_rows([])

    def _render_class_details(self, obj: FmmlxObject):
        self.detail_title.configure(
            text=f"Class: {obj.name}",
            text_color="#2563EB",
        )
        self.detail_subtitle.configure(
            text="Attributes defined for the selected class."
        )

        rows = []
        for attr in obj.attr_list:
            rows.append(
                (
                    attr.name,
                    attr.attr_type_short,
                    "",
                )
            )

        self._render_detail_rows(rows)

    def _render_object_details(self, obj: FmmlxObject):
        self.detail_title.configure(
            text=f"Object: {obj.name}",
            text_color="#16A34A",
        )
        self.detail_subtitle.configure(
            text="Attribute values for the selected object."
        )

        rows = []
        for slot in obj.slot_list:
            rows.append(
                (
                    slot.name,
                    self._slot_type(slot),
                    slot.value,
                )
            )

        self._render_detail_rows(rows)

    def _render_detail_rows(self, rows):
        self._reset_detail_canvas_table()
        for child in self.detail_table.winfo_children():
            child.destroy()

        # Shared columns for all rows.
        self.detail_table.grid_columnconfigure(0, weight=2, minsize=240)
        self.detail_table.grid_columnconfigure(1, weight=1, minsize=180)
        self.detail_table.grid_columnconfigure(2, weight=2, minsize=280)

        header_bg = "#DCEAFF"
        headers = ("Attribute", "Type", "Value")

        for column, text in enumerate(headers):
            cell = tk.Frame(
                self.detail_table,
                height=42,
                background=header_bg,
                bd=0,
                highlightthickness=0,
            )
            cell.grid(
                row=0,
                column=column,
                sticky="nsew",
            )
            cell.grid_propagate(False)

            if column > 0:
                tk.Frame(
                    cell,
                    width=1,
                    background="#DCE6F2",
                    bd=0,
                    highlightthickness=0,
                ).place(x=0, y=0, width=1, height=42)

            ctk.CTkLabel(
                cell,
                text=text,
                anchor="center",
                justify="center",
                text_color="#17365D",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold",
                ),
            ).place(relx=0.5, rely=0.5, anchor="center")

        if not rows:
            empty = tk.Frame(
                self.detail_table,
                height=80,
                background="#FFFFFF",
                bd=0,
                highlightthickness=0,
            )
            empty.grid(
                row=1,
                column=0,
                columnspan=3,
                sticky="nsew",
            )
            empty.grid_propagate(False)

            ctk.CTkLabel(
                empty,
                text="Nothing selected.",
                text_color=self.colors["muted"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            for row_index, (attribute, attr_type, value) in enumerate(
                    rows,
                    start=1,
            ):
                row_bg = "#FFFFFF" if row_index % 2 else "#F3F7FD"

                for column, cell_value in enumerate(
                        (attribute, attr_type, value)
                ):
                    cell = tk.Frame(
                        self.detail_table,
                        height=46,
                        background=row_bg,
                        bd=0,
                        highlightthickness=0,
                    )
                    cell.grid(
                        row=row_index,
                        column=column,
                        sticky="nsew",
                    )
                    cell.grid_propagate(False)

                    if column > 0:
                        tk.Frame(
                            cell,
                            width=1,
                            background="#E4EBF4",
                            bd=0,
                            highlightthickness=0,
                        ).place(
                            x=0,
                            y=0,
                            width=1,
                            height=46,
                        )

                    if column == 1 and cell_value:
                        ctk.CTkLabel(
                            cell,
                            text=str(cell_value),
                            height=24,
                            corner_radius=12,
                            fg_color="#E7F0FF",
                            text_color="#2457A6",
                            font=ctk.CTkFont(
                                family="Segoe UI",
                                size=11,
                                weight="bold",
                            ),
                        ).place(
                            relx=0.5,
                            rely=0.5,
                            anchor="center",
                        )
                    else:
                        ctk.CTkLabel(
                            cell,
                            text="" if cell_value is None else str(cell_value),
                            anchor="center",
                            justify="center",
                            text_color=self.colors["text"],
                            font=ctk.CTkFont(
                                family="Segoe UI",
                                size=12,
                            ),
                        ).place(
                            relx=0.5,
                            rely=0.5,
                            anchor="center",
                            relwidth=0.92,
                        )

        self.detail_table.update_idletasks()
        self.detail_canvas.itemconfigure(
            self.detail_canvas_window,
            width=max(self.detail_canvas.winfo_width(), 700),
        )
        self.detail_canvas.configure(
            scrollregion=self.detail_canvas.bbox("all")
        )
        self.detail_canvas.xview_moveto(0)
        self.detail_canvas.yview_moveto(0)

    def _render_attribute_details(self, attr: FmmlxAttribute):
        # Attribute nodes are no longer selectable in Step 2.
        self._render_empty_detail_state()

    def _render_slot_details(self, slot: FmmlxSlot):
        # Slot nodes are no longer selectable in Step 2.
        self._render_empty_detail_state()

    def _set_detail_rows(self, rows):
        # Compatibility helper for older code paths.
        self._render_detail_rows(rows)

    def _populate_models_table(self):
        if not hasattr(self, "models_canvas"):
            return

        self.models_canvas.delete("all")
        self._models_canvas_rows = {}

        canvas_width = max(1, self.models_canvas.winfo_width())

        # Relative widths always sum to the current canvas width.
        column_specs = [
            ("name", "Model Name", 0.13),
            ("source", "Source File", 0.17),
            ("type", "Type", 0.08),
            ("classes", "Classes", 0.09),
            ("attributes", "Attributes", 0.10),
            ("objects", "Objects", 0.10),
            ("status", "Completed Step", 0.16),
            ("worked", "Last worked on", 0.17),
        ]

        columns = []
        used_width = 0
        for index, (key, label, fraction) in enumerate(column_specs):
            if index == len(column_specs) - 1:
                width = canvas_width - used_width
            else:
                width = max(80, int(canvas_width * fraction))
                used_width += width
            columns.append((key, label, width))

        row_height = 44
        header_height = 44

        x = 0
        for _key, label, width in columns:
            self._draw_models_table_cell(
                x=x,
                y=0,
                width=width,
                height=header_height,
                text=label,
                background="#DCEAFF",
                foreground="#17365D",
                font=("Segoe UI", 12, "bold"),
            )
            x += width

        filtered = []
        for index, loaded in enumerate(self.loaded_models):
            if self._model_matches_overview_filters(loaded):
                filtered.append((index, loaded))

        for row_index, (model_index, loaded) in enumerate(filtered, start=1):
            model = loaded.model
            y = header_height + ((row_index - 1) * row_height)
            row_bg = "#FFFFFF" if row_index % 2 else "#F3F7FD"

            values = [
                loaded.name,
                loaded.source_file,
                loaded.file_type,
                len(model.get_all_flat_classes()),
                self._count_attributes(model),
                len(model.get_all_pure_objects()),
                self._model_completed_step_label(),
                loaded.last_worked_on or "Unknown",
            ]

            x = 0
            row_items = []
            for column_index, ((_key, _label, width), value) in enumerate(
                zip(columns, values)
            ):
                if column_index == 6:
                    items = self._draw_models_status_cell(
                        x=x,
                        y=y,
                        width=width,
                        height=row_height,
                        status=str(value),
                        background=row_bg,
                    )
                else:
                    items = self._draw_models_table_cell(
                        x=x,
                        y=y,
                        width=width,
                        height=row_height,
                        text=value,
                        background=row_bg,
                        foreground=self.colors["text"],
                        font=("Segoe UI", 12),
                    )
                row_items.extend(items)
                x += width

            for item in row_items:
                self.models_canvas.tag_bind(
                    item,
                    "<Button-1>",
                    lambda _event, idx=model_index: self._select_model_from_overview_index(idx),
                )

            self._models_canvas_rows[model_index] = row_items

        total_height = header_height + max(1, len(filtered)) * row_height
        self.models_canvas.configure(
            scrollregion=(0, 0, canvas_width, total_height)
        )
        self.models_canvas.xview_moveto(0)

    def _draw_models_table_cell(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            text: object,
            background: str,
            foreground: str,
            font,
    ) -> List[int]:
        rect = self.models_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=background,
            outline="#E4EBF4",
            width=1,
        )
        label = self.models_canvas.create_text(
            x + (width / 2),
            y + (height / 2),
            text="" if text is None else str(text),
            fill=foreground,
            font=font,
            anchor="center",
            justify="center",
            width=max(20, width - 18),
        )
        return [rect, label]

    def _draw_models_status_cell(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            status: str,
            background: str,
    ) -> List[int]:
        rect = self.models_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=background,
            outline="#E4EBF4",
            width=1,
        )
        failed = "fail" in status.lower()
        text = self.models_canvas.create_text(
            x + (width / 2),
            y + (height / 2),
            text=status,
            fill=self.colors["danger"] if failed else self.colors["success"],
            font=("Segoe UI", 11, "bold"),
            anchor="center",
            justify="center",
            width=max(20, width - 16),
        )
        return [rect, text]

    def _model_matches_overview_filters(self, loaded: LoadedModel) -> bool:
        query_var = getattr(self, "models_search_var", None)
        query = query_var.get().strip().lower() if query_var is not None else ""
        if query and query not in loaded.name.lower() and query not in loaded.source_file.lower():
            return False

        type_var = getattr(self, "models_type_filter_var", None)
        type_filter = type_var.get() if type_var is not None else "All"
        if type_filter != "All" and loaded.file_type != type_filter:
            return False

        model = loaded.model
        min_objects_var = getattr(self, "models_min_objects_var", None)
        min_objects = self._optional_int_filter(
            min_objects_var.get() if min_objects_var is not None else ""
        )
        if min_objects is not None and len(model.get_all_pure_objects()) < min_objects:
            return False

        min_attributes_var = getattr(self, "models_min_attributes_var", None)
        min_attributes = self._optional_int_filter(
            min_attributes_var.get() if min_attributes_var is not None else ""
        )
        if min_attributes is not None and self._count_attributes(model) < min_attributes:
            return False

        return True

    def _optional_int_filter(self, value: str) -> Optional[int]:
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _model_completed_step_label(self) -> str:
        completed = [
            step
            for step, done in self.step_completed.items()
            if done
        ]
        if not completed:
            return "Imported"
        return f"Step {max(completed)} completed"

    def _select_model_from_overview(self, _event):
        return

    def _select_model_from_overview_index(self, index: int):
        for row_items in getattr(self, "_models_canvas_rows", {}).values():
            for item in row_items:
                try:
                    self.models_canvas.itemconfigure(item, width=1)
                except tk.TclError:
                    pass
        for item in getattr(self, "_models_canvas_rows", {}).get(index, []):
            try:
                if self.models_canvas.type(item) == "rectangle":
                    self.models_canvas.itemconfigure(item, outline="#AFCBFF", width=2)
            except tk.TclError:
                pass
        loaded = self.loaded_models[index]
        self.current_model = loaded.model
        self._render_overview_details(loaded)

    def _bind_models_scroll_events(self, _event=None):
        self.bind_all("<MouseWheel>", self._on_models_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_models_shift_mousewheel)

    def _unbind_models_scroll_events(self, _event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def _on_models_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.models_canvas.yview_scroll(delta, "units")

    def _on_models_shift_mousewheel(self, event):
        # The overview table always fits the available width.
        return

    def _render_overview_details(self, loaded: Optional[LoadedModel] = None):
        for child in self.overview_details.winfo_children():
            child.destroy()

        self.overview_details.grid_columnconfigure(0, weight=0, minsize=380)
        self.overview_details.grid_columnconfigure(1, weight=1)

        if loaded is None:
            message = (
                "No model selected."
                if self.loaded_models
                else "No models created yet."
            )
            ctk.CTkLabel(
                self.overview_details,
                text=message,
                text_color=self.colors["muted"],
                anchor="center",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13,
                    weight="bold",
                ),
            ).grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="nsew",
                padx=18,
                pady=32,
            )
            return

        self.current_model = loaded.model
        model = loaded.model

        meta = ctk.CTkFrame(
            self.overview_details,
            fg_color="#F8FAFC",
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
        )
        meta.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=(0, 14),
        )
        meta.grid_columnconfigure(1, weight=1)

        rows = [
            ("Model Name", loaded.name),
            ("Source File", loaded.source_file),
            ("Type", loaded.file_type),
            ("Imported", loaded.uploaded or "Unknown"),
            ("Last worked on", loaded.last_worked_on or "Unknown"),
        ]

        for row, (label, value) in enumerate(rows):
            top_pad = 12 if row == 0 else 5
            bottom_pad = 12 if row == len(rows) - 1 else 5

            ctk.CTkLabel(
                meta,
                text=label,
                text_color=self.colors["muted"],
                anchor="w",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold",
                ),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(14, 18),
                pady=(top_pad, bottom_pad),
            )

            ctk.CTkLabel(
                meta,
                text=str(value),
                anchor="w",
                text_color=self.colors["text"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold" if row == 0 else "normal",
                ),
            ).grid(
                row=row,
                column=1,
                sticky="ew",
                padx=(0, 14),
                pady=(top_pad, bottom_pad),
            )

        metrics = ctk.CTkFrame(
            self.overview_details,
            fg_color="transparent",
        )
        metrics.grid(
            row=0,
            column=1,
            sticky="nsew",
            pady=(0, 10),
        )

        metric_colors = {
            "Classes": "#2563EB",
            "Attributes": "#7C3AED",
            "Enumerations": "#F59E0B",
            "Associations": "#64748B",
            "Objects": "#16A34A",
            "Slots": "#EA580C",
            "Links": "#0891B2",
        }

        for index, (label, value) in enumerate(self._model_metrics(model)):
            metrics.grid_columnconfigure(index, weight=1)
            metric = self._metric_card_no_icon(
                metrics,
                label,
                value,
                metric_colors.get(label, self.colors["primary"]),
            )
            metric.configure(height=88)
            metric.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 4, 0 if index == 6 else 4),
            )

        actions = ctk.CTkFrame(
            self.overview_details,
            fg_color="transparent",
        )
        actions.grid(
            row=1,
            column=1,
            sticky="ew",
        )
        actions.grid_columnconfigure(0, weight=1)

        button_group = ctk.CTkFrame(
            actions,
            fg_color="transparent",
        )
        button_group.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            button_group,
            text="Open Model",
            width=180,
            height=42,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold",
            ),
            command=lambda target=loaded: self._open_loaded_model(target),
        ).grid(
            row=0,
            column=0,
            padx=(0, 10),
        )

        ctk.CTkButton(
            button_group,
            text="Delete Model",
            width=180,
            height=42,
            corner_radius=8,
            fg_color=self.colors["danger"],
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold",
            ),
            command=lambda target=loaded: self._delete_loaded_model(target),
        ).grid(
            row=0,
            column=1,
        )

    def _open_loaded_model(self, loaded: LoadedModel):
        self._touch_loaded_model(loaded)
        self.current_model = loaded.model
        self._show_model_page()

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

    def _delete_loaded_model(self, loaded: LoadedModel):
        if not messagebox.askyesno(
                "Delete model",
                f"Remove '{loaded.name}' from the models overview?",
        ):
            return
        if loaded in self.loaded_models:
            self.loaded_models.remove(loaded)
        if self.current_model is loaded.model:
            self.current_model = self.loaded_models[-1].model if self.loaded_models else None
        self._populate_models_table()
        self._render_overview_details(None)

    def _model_metrics(self, model: FmmlxModel):
        return [
            ("Classes", len(model.get_all_flat_classes())),
            ("Attributes", self._count_attributes(model)),
            ("Enumerations", len(model.enums)),
            ("Associations", len(model.associations)),
            ("Objects", len(model.get_all_pure_objects())),
            ("Slots", self._count_slots(model)),
            ("Links", len(model.links)),
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
