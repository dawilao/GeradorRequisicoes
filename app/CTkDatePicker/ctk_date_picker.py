import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import calendar

class CTkDatePicker(ctk.CTkFrame):
    def __init__(self, master=None, tabview=None, **kwargs):
        """
        Initialize the CTkDatePicker instance.
        
        Parameters:
        - master: The parent widget.
        - **kwargs: Additional keyword arguments passed to the CTkFrame constructor.
        
        Initializes the date entry, calendar button, popup, and other related components.
        """
        super().__init__(master)
        self.tabview = tabview

        self.frame_externo = ctk.CTkFrame(self)
        self.frame_externo.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        self._set_appearance_mode("system")

        # Configuração para expansão horizontal do frame
        self.grid_columnconfigure(0, weight=1)
        self.frame_externo.grid_columnconfigure(0, weight=1)  # Faz a entrada expandir

        self.date_entry = ctk.CTkEntry(self.frame_externo, border_width=1, corner_radius=1)
        self.date_entry.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        self.calendar_button = ctk.CTkButton(self.frame_externo, text="📅", width=28, fg_color="#565b5e", 
                                            corner_radius=1, hover_color="#7a848d", command=self.open_calendar)
        self.calendar_button.grid(row=0, column=1, sticky="w", padx=0, pady=0)

        self.popup = None
        self.selected_date = None
        self.date_format = "%d/%m/%Y"
        self.allow_manual_input = True  
        
    def set_date_format(self, date_format):
        """
        Set the date format to be used in the date entry.

        Parameters:
        - date_format (str): The desired date format string, e.g., "%m/%d/%Y".
        
        Sets the format in which the selected date will be displayed.
        """
        self.date_format = date_format
                
    def open_calendar(self):
        """
        Open the calendar popup for date selection.
        
        Creates and displays a calendar widget allowing the user to select a date.
        The calendar appears just below the date entry field.
        """
        
        if self.popup is not None:
            self.popup.destroy()

        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Selecione a data")
        self.popup.geometry("+%d+%d" % (self.winfo_rootx(), self.winfo_rooty() + self.winfo_height()))
        self._set_appearance_mode("system")
        self.popup.resizable(False, False)

        self.popup.after(500, lambda: self.popup.focus())
        
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.build_calendar()
        
    def build_calendar(self):
        """
        Build and display the calendar in the popup.

        Constructs the calendar UI for the currently selected month and year.
        Includes navigation buttons for previous and next months.
        """
        
        if hasattr(self, 'calendar_frame'):
            self.calendar_frame.destroy()

        self.calendar_frame = ctk.CTkFrame(self.popup)
        self.calendar_frame.grid(row=0, column=0)
        self._set_appearance_mode("system")

        today = datetime.today().date()

        meses_pt = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        # Month and Year Selector
        month_label = ctk.CTkLabel(self.calendar_frame, text=f"{meses_pt[self.current_month]}, {self.current_year}")
        month_label.grid(row=0, column=1, columnspan=5)

        prev_month_button = ctk.CTkButton(self.calendar_frame, text="<", width=5, command=self.prev_month)
        prev_month_button.grid(row=0, column=0)

        next_month_button = ctk.CTkButton(self.calendar_frame, text=">", width=5, command=self.next_month)
        next_month_button.grid(row=0, column=6)

        # Days of the week header
        days = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, day in enumerate(days):
            lbl = ctk.CTkLabel(self.calendar_frame, text=day)
            lbl.grid(row=1, column=i)

        # Days in month
        month_days = calendar.monthrange(self.current_year, self.current_month)[1]
        start_day = (calendar.monthrange(self.current_year, self.current_month)[0] + 1) % 7
        day = 1

        for week in range(2, 8):
            for day_col in range(7):
                if week == 2 and day_col < start_day:
                    lbl = ctk.CTkLabel(self.calendar_frame, text="", text_color=("black", "white"))
                    lbl.grid(row=week, column=day_col)
                elif day > month_days:
                    lbl = ctk.CTkLabel(self.calendar_frame, text="", text_color=("black", "white"))
                    lbl.grid(row=week, column=day_col)
                else:
                    current_day = day
                    current_date = datetime(self.current_year, self.current_month, current_day).date()

                    if self.tabview == "AQUISIÇÃO" and current_date < today:
                        btn = ctk.CTkButton(self.calendar_frame, text=str(current_day), width=3,
                                            state="disabled", fg_color="transparent", text_color="#A0A0A0")
                    elif current_date == today:
                        btn = ctk.CTkButton(self.calendar_frame, text=str(current_day), width=3,
                                            command=lambda day=current_day: self.select_date(day),
                                            fg_color="#3a7bd5", text_color="white")
                    else:
                        btn = ctk.CTkButton(self.calendar_frame, text=str(current_day), width=3,
                                            command=lambda day=current_day: self.select_date(day),
                                            fg_color="transparent", text_color=("black", "white"))

                    btn.grid(row=week, column=day_col)
                    day += 1

    def prev_month(self):
        """
        Navigate to the previous month in the calendar.

        Updates the calendar display to show the previous month's days.
        Adjusts the year if necessary.
        """
        
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.build_calendar()

    def next_month(self):
        """
        Navigate to the next month in the calendar.

        Updates the calendar display to show the next month's days.
        Adjusts the year if necessary.
        """
        
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.build_calendar()

    def select_date(self, day):
        """
        Select a date from the calendar.

        Parameters:
        - day (int): The day of the month selected by the user.
        
        Sets the selected date in the date entry field and closes the calendar popup.
        """
        
        self.selected_date = datetime(self.current_year, self.current_month, day)
        # Temporarily enable the entry to set the date
        self.date_entry.configure(state='normal')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, self.selected_date.strftime(self.date_format))
        # Restore the disabled state if necessary
        if not self.allow_manual_input:
            self.date_entry.configure(state='disabled')
        self.popup.destroy()
        self.popup = None

        
    def get_date(self):
        """
        Get the currently selected date as a string.

        Returns:
        - str: The date string in the format specified by self.date_format.
        """
    
        return self.date_entry.get()
    
    def set_allow_manual_input(self, value):
        """
        Enable or disable manual date input.

        Parameters:
        - value (bool): If True, manual input in the date entry is allowed; otherwise, it is disabled.
        
        Allows the user to manually enter a date if set to True; otherwise, restricts input to selection via the calendar.
        """
        
        self.allow_manual_input = value
        if not value:
            self.date_entry.configure(state='disabled')
        else:
            self.date_entry.configure(state='normal')

    def set(self, value: str):
        """
        Define programaticamente o valor/data no campo de entrada do date picker.
        
        Esta função permite definir uma data específica no campo de entrada, 
        independentemente da configuração de entrada manual do componente.
        É especialmente útil para restaurar valores salvos, definir datas padrão
        ou sincronizar com outros componentes da interface.
        
        Parameters:
        - value (str): A data em formato string que será inserida no campo.
                    Deve estar no formato especificado por self.date_format
                    (padrão: "%d/%m/%Y", ex: "25/12/2023").
        
        Behavior:
        - Se allow_manual_input for False (entrada manual desabilitada):
        * Habilita temporariamente o campo
        * Limpa o conteúdo atual
        * Insere o novo valor
        * Restaura o estado desabilitado
        - Se allow_manual_input for True (entrada manual habilitada):
        * Limpa o conteúdo atual
        * Insere o novo valor diretamente
        
        Example:
            date_picker.set("31/12/2023")  # Define 31 de dezembro de 2023
            date_picker.set("01/01/2024")  # Define 1º de janeiro de 2024
        
        Note:
            Esta função não valida o formato da data fornecida. É responsabilidade
            do chamador garantir que o valor esteja no formato correto.
        """
        if not self.allow_manual_input:
            self.date_entry.configure(state="normal")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, value)
            self.date_entry.configure(state="disabled")
        else:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, value)