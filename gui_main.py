# customtkinter doc link: https://customtkinter.tomschimansky.com/documentation/
# customtkinter GitHub: https://github.com/TomSchimansky/CustomTkinter
import customtkinter as ctk
from customtkinter import filedialog
import os
from datetime import date

from promotion_process import *


# Background color theme of widgets
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green


class GuiMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x500")
        self.title("MLM Case Navigator Tool")
        self.create_widgets()
        # more attributes in other gui

    def create_widgets(self):

        # fonts and paddings
        font_header:str = "Roboto"
        font_body:str = "Roboto"

        padx_s = "10"
        padx_l = "20"

        #pady

        # Titel, der oben im Programm steht
        title_label = ctk.CTkLabel(self, text="MLM Automatic Construction", font=(font_header, 40, "bold"))
        title_label.pack(pady=10, padx=10, anchor="w")

        # 1) Case Navigator
        case_label = ctk.CTkLabel(self, text="Case Navigator", font=(font_header, 28))
        case_label.pack(anchor="w", padx=20)

        pad_label = ctk.CTkLabel(self, text="", font=(font_header, 5))
        pad_label.pack(anchor="w", pady=10)

        # Drop-Down-Menü für Cases MUSS MIT RICHTIGEN CASES GEFÜLLT WERDEN
        # Zunächst Methode, die nach Auswahl im Dropdown-Menü aufgerufen wird und Infolabel (s.u.) über Case aktualisiert
        def combobox_callback(choice):
            if choice == "Generalization":
                update_info_label(choice + ": This case covers the investigation of generalization potentials, which"
                                           " might not involve the introduction of new levels")
            if choice == "Classification":
                update_info_label(choice + ": This case covers classification examples, where a new level must be introduced")

        self.case_dropdown = ctk.StringVar(self)
        self.combobox_case_dropdown = ctk.CTkComboBox(self, values=["Generalization", "Classification"], command=combobox_callback,
                                                      button_color="gray")
        self.combobox_case_dropdown.set("Select case...")
        self.combobox_case_dropdown.pack(anchor="w", padx="20")

        # Informationstext über ausgewählten Case
        self.case_info_label = ctk.CTkLabel(self, text="Here you can view information about the selected case." ,
                                            font=(font_body, 16, "normal"))
        self.case_info_label.pack(anchor="w", padx="40")

        # Methode wird aufgerufen, nachdem ein Case im Dropdown_Menü ausgewählt wird
        def update_info_label(choice):
            self.case_info_label.configure(text=choice)

        # Nur damit mehr Platz zwischen einzelnen Zeilen ist
        placeholder_label = ctk.CTkLabel(self, text="", font=("Calibri", 16, "normal"))
        placeholder_label.pack(anchor="w", pady="30", padx="10")

        # Dropdown Menü über Automatisierungstechnik
        self.automation_technology_dropdown = ctk.StringVar(self)
        self.combobox_automation_technology_dropdown = ctk.CTkComboBox(self, values=["Formal Concept Analaysis",
                                                                                     "Clustering"],
                                                                       button_color="gray", width=250)
        self.combobox_automation_technology_dropdown.set("Select automation technology...")
        self.combobox_automation_technology_dropdown.pack(anchor="w", padx="20")

        # 2) Upload Input Model
        upload_label = ctk.CTkLabel(self, text="Upload Input Model", font=("Calibri", 28, "bold"))
        upload_label.pack(anchor="w")  # bestimmt, dass das Label mittig platziert wird

        # Dateiauswahl-Button für Model Upload
        self.file_path = ctk.StringVar(self)
        browse_xml_file_button = ctk.CTkButton(self, text="Select file", font=("Calibri", 18, "bold"), command=self.browse_xml_file)
        browse_xml_file_button.pack()

        # Ausgewählte Datei anzeigen
        selected_file_label = ctk.CTkLabel(self, textvariable=self.file_path)
        selected_file_label.pack()

        # Execute-Button, der Methode "execute_case" ausführt, die weiter unten definiert ist
        execute_button = ctk.CTkButton(self, text="Execute", font=("Calibri", 18, "bold"), command=self.execution)
        execute_button.pack(side="bottom", padx=10, pady=10)

        # Erstellung eines Result-Label
        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack()

    # Methode wird aufgerufen, nachdem browse_xml_file_button gedrückt wird
    def browse_xml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        self.file_path.set(file_path)

    # Methode zur Ausführung des ausgewählten Case, Automatisierungstechnik und XML-Datei
    def execution(self):
        if self.file_path.get():
            perform_promotion_process(self.file_path.get())
            # print(mlm)
        else:
            print("NO FILE PROVIDED")

    def execute_case(self):
        # XML-Inhalt, den du speichern möchtest (hier verwende ich ein Beispiel)
        xml_content = "<root><data>Some data</data></root>"
        # Überprüfe, welcher Case ausgewählt wurde
        # Falls kein Case ausgewählt, wird folgender Text angezeigt
        selected_case = self.combobox_case_dropdown.get()
        if selected_case == "Select case...":
            self.result_label.configure(text="Please choose a case.")
            return

        # Überprüfe, welche Automatisierungstechnik ausgewählt wurde
        # Falls keine Technik ausgewählt, wird folgender Text angezeigt
        selected_automation_technology = self.combobox_automation_technology_dropdown.get()
        if selected_automation_technology == "Select automation technology...":
            self.result_label.configure(text="Please choose an automation technology.")
            return

        # Überprüfe, ob eine Datei ausgewählt wurde
        if self.file_path.get():
            selected_file_path = self.file_path.get()

            # Extrahiere den Verzeichnispfad und den Dateinamen
            file_dir, file_name = os.path.split(selected_file_path)

            # Füge das aktuelle Datum als Präfix zum Dateinamen hinzu
            dateToday = date.today()
            new_file_name = str(dateToday) + "_" + file_name

            # Erstelle den vollständigen Pfad für die neue Datei
            new_file_path = os.path.join(file_dir, new_file_name)

            # Speichere den XML-Inhalt in die neue Datei
            # with open(new_file_path, "w") as file:
            #    file.write(xml_content)

            self.result_label.configure(text=f"XML file saved under:\n{new_file_path}")
        else:
            self.result_label.configure(text="Please choose a XML file.")


if __name__ == "__main__":
    gui = GuiMain()
    gui.mainloop()
