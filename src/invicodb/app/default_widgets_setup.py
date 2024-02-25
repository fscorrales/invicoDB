import customtkinter as ctk
from dataclasses import dataclass

class DefaultFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # kwargs['height'] = 100
        super().__init__(master, **kwargs)

class DefaultScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        kwargs['width'] = 300
        # kwargs['height'] = 100
        super().__init__(master, **kwargs)

class DefaultCheckBox(ctk.CTkCheckBox):
    def __init__(self, master, **kwargs):
        # kwargs['label_text'] = 'Prueba'
        super().__init__(master, **kwargs)

class DefaultButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        # kwargs['label_text'] = 'Prueba'
        super().__init__(master, **kwargs)

class DefaultSwitch(ctk.CTkSwitch):
    def __init__(self, master, **kwargs):
        # kwargs['label_text'] = 'Prueba'
        super().__init__(master, **kwargs)

class DefaultOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, master, **kwargs):
        kwargs['dynamic_resizing'] = False
        super().__init__(master, **kwargs)

class MyCheckboxFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = ctk.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get_text(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes

class MyScrollableCheckboxFrame(DefaultScrollableFrame):
    def __init__(
            self, master, title:str, values_and_vars:dict, 
            padx_checkbox:int = 5, pady_checkbox:int = 5
    ):
        super().__init__(master, label_text=title)
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            # self.rowconfigure(index=index, weight=1)
        self.values = list(values_and_vars.keys())
        self.vars_names = list(values_and_vars.values())
        self.checkboxes = []
        
        self.var_switch_all = ctk.BooleanVar()
        self.switch = DefaultSwitch(
            self, text="Seleccionar Todo", variable=self.var_switch_all,
            command=self.switch_all
        )
        self.switch.grid(
            row=0, column=1, padx=10, pady=(0, 0), sticky="nsew"
        )

        for i, value in enumerate(self.values):
            checkbox_var = ctk.BooleanVar()
            setattr(self, self.vars_names[i], checkbox_var)  # Asignar la variable al objeto
            checkbox = DefaultCheckBox(self, text=value, variable=checkbox_var)
            checkbox.grid(
                row=i+1, column=0, sticky="w", columnspan=3,
                padx=padx_checkbox, pady=pady_checkbox
            )
            self.checkboxes.append(checkbox)

    def get_text(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
    
    def switch_all(self):
        if self.var_switch_all.get() == 1:
            for checkbox in self.checkboxes:
                checkbox.select()
        else:
            for checkbox in self.checkboxes:
                checkbox.deselect()