"""
BarrenoApp V0.1

Digital form to collect field data in soil surveys
Soil testing using auger and trench sampling

Created by J. Rodriguez
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkinter import Tk, font
import csv
import os

class FormsApp(tk.Tk):
    """
    Main application class for the multi-page form.
    Manages page navigation and data saving.
    """
    def __init__(self):
        super().__init__()
        self.title('Planilla Estudio de Suelos')
        self.geometry('1280x760') # Tamaño estándar HD

        self.estacion_var = tk.StringVar()
        self.estacion_codigo_var = tk.StringVar()
        self.proyecto_var = tk.StringVar()
        self.IDpunto_var = tk.StringVar()
        
        self.defaultFont = font.nametofont('TkDefaultFont')  # Creating a Font object of 'TkDefaultFont'

        # Overriding default-font with custom settings, i.e changing font-family, size and weight
        self.defaultFont.configure(family='Helvetica', size=9)

        # Dictionary to store data collected from all pages
        self.form_data = {}

        # Create a container frame to hold all pages.
        # This allows pages to be stacked and switched using tkraise().
        container = tk.Frame(self)
        container.pack(side='top', fill='none', expand=False)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize and store all pages in a dictionary
        self.frames = {}
        
        for F in (PageOne, PageTwo):
            page_name = F.__name__
            # Pass the container as parent and self (FormsApp instance) as controller
            frame = F(parent = container, controller=self)
            self.frames[page_name] = frame
            # Place each frame in the same grid cell so they overlap
            frame.grid(row=0, column = 0, sticky='nsew')

        # Show the first page initially
        self.show_frame('PageOne')

    def show_frame(self, page_name):
        """
        Raises the specified frame to the top, making it visible.
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def update_form_data(self, page_name, data):
        """
        Updates the main form_data dictionary with data from a specific page.
        Prefixes keys with page name for clarity in the CSV.
        """
        if page_name not in self.form_data:
        # Inicializar el diccionario para la página si no existe
            self.form_data[page_name] = {}
            # Usar .update() asegura que se guarden todas las claves, incluyendo 'horaf'.
        self.form_data[page_name].update(data)

    def save_page_data_to_csv(self, page_name):
        data = self.form_data.get(page_name, {})
        file_name = f'soilsurvey_{page_name.lower()}.csv'
        rows_to_write = []
        
        if page_name == 'PageTwo':
            # Filtrar listas vacías o erróneas antes de guardar
            fixed_data = {k: v for k, v in data.items() if not isinstance(v, list)}
            horizon_data = {k: v for k, v in data.items() if isinstance(v, list)}
            
            # Verificar longitud máxima
            lengths = [len(v) for v in horizon_data.values() if isinstance(v, list)]
            num_horizons = max(lengths) if lengths else 0
            
            fieldnames = list(fixed_data.keys()) + list(horizon_data.keys())
            
            if num_horizons > 0:
                for i in range(num_horizons):
                    row = fixed_data.copy()
                    for key, values in horizon_data.items():
                        # Manejo seguro de índices
                        if i < len(values):
                            row[key] = values[i]
                        else:
                            row[key] = ''
                    rows_to_write.append(row)
        else:
            fieldnames = list(data.keys()) 
            if data:
                rows_to_write.append(data)
        
        if not rows_to_write:
            return True 

        try:
            file_exists = os.path.isfile(file_name)
            with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
                if not file_exists:
                    writer.writeheader()
                writer.writerows(rows_to_write) 
        except Exception as e:
            messagebox.showerror('Error', f'Error guardando {page_name}: {e}')
            return False

        return True
   
    def save_all_data_and_reset(self):
        """
        Saves data from all pages to their respective CSV files and clears forms.
        """
        success_page1 = self.save_page_data_to_csv('PageOne')
        success_page2 = self.save_page_data_to_csv('PageTwo')
        
        if success_page1 and success_page2:
            messagebox.showinfo('Guardado', '¡Guardado exitoso en archivos CSV separados!')
            self.clear_form_data()
            self.show_frame('PageOne')
        else:
             messagebox.showerror('Error', 'Fallo al guardar uno o más archivos CSV.')

    def clear_form_data(self):
        """
        Clears the internal form_data dictionary and resets the StringVars
        on both pages to their default or empty states.
        """
        self.form_data = {}
        self.frames['PageOne'].reset_variables()
        self.frames['PageTwo'].reset_variables()
        
# =============================================================
# Clase para la primera página del formulario
# =============================================================
class PageOne(tk.Frame):
    """
    Represents the first page of the form.
    Contains two Entry widgets and one Radiobutton group.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, padx=0, pady=0) # Add padding to the frame
        self.controller = controller

        # --- CONFIGURACIÓN DE ESTILOS ---
        self.style = ttk.Style()
        
        # Esto cambia la fuente de TODOS los TLabels y TEntries en la app
        self.style.configure('TLabel', font=('Arial', 9))
        self.style.configure('TEntry', font=('Arial', 9))
        self.style.configure('TCombobox', font=('Arial', 9))
        self.style.configure('TLabelframe.Label', font=('Arial', 9, 'italic')) # Títulos de módulos

        ### Validaciones ###
        # 1. Registrar la función de validación
        # La función de validación se ejecutará cuando se intente modificar el Entry.
        # '%P' pasa el valor *posterior* de la entrada al validador.
        self.date_vcmd = (self.register(self.validate_date), '%P')
        self.time_vcmd = (self.register(self.check_time_12hr), '%P')
        self.flotante_vcmd = (self.register(self.validar_flotante), '%P')
        self.vcmd_range = (self.register(self.validate_slope_range), '%P')

        # =============================================================
        # CONFIGURACIÓN DE REJILLA (GRID) DE LA PÁGINA
        # =============================================================
        # Definiremos 3 filas y 6 columnas para los 18 módulos
        for i in range(7): self.grid_columnconfigure(i, weight = 1, minsize = 140)
        for j in range(6): self.grid_rowconfigure(j, weight = 1, minsize = 120)

        # =============================================================
        # MÓDULO 1: IDENTIFICACIÓN Y UBICACIÓN
        # =============================================================
        mod_proyecto = ttk.LabelFrame(self, text="1. PROYECTO", padding=10)
        mod_proyecto.grid(row =0, column = 0, columnspan = 4, padx = 1, pady = 1, sticky = 'nsew')
        
        # Proyecto
        ttk.Label(mod_proyecto,text ='Proyecto:').grid(row=0, column = 0, sticky = 'w')
        ttk.Entry(mod_proyecto, width = 10, textvariable = self.controller.proyecto_var
                  ).grid(row=0, column = 1, padx = 1, pady = 1, sticky = 'nsew')
     
        # Fecha
        self.fecha_var = tk.StringVar()
        
        ttk.Label(mod_proyecto, text='Fecha(AAAA/MM/DD):').grid(row=0, column = 2, sticky='w')
        ttk.Entry(mod_proyecto, width = 10, textvariable = self.fecha_var,
                  validate='key', validatecommand=self.date_vcmd).grid(row=0, column = 3, sticky='w')
        
        # --- CONFIGURACIÓN DE HORAS (INICIO Y FIN) ---
        self.hora_vars = {
            'ini': {'time': tk.StringVar(), 'merid': tk.StringVar(value='AM')},
            'fin': {'time': tk.StringVar(), 'merid': tk.StringVar(value='AM')}
        }

        for i, (key, label_text) in enumerate([('ini', 'Inicio'), ('fin', 'Fin')]):
            ttk.Label(mod_proyecto, text=f'{label_text}(HH:MM):').grid(row=i, column=4, sticky='w')
            
            # Pasamos '%W' al validador para saber qué Entry es
            vcmd = (self.register(self.check_time_12hr), '%P', '%W')
            
            ent = ttk.Entry(mod_proyecto, width=10, 
                            textvariable=self.hora_vars[key]['time'],
                            validate='key', validatecommand=vcmd,
                            style='Valid.TEntry')
            ent.grid(row=i, column=5, sticky='w')
            
            cbox = ttk.Combobox(mod_proyecto, width=3, 
                                textvariable=self.hora_vars[key]['merid'],
                                values=['AM', 'PM'], state='readonly')
            cbox.grid(row=i, column=6, sticky='w')        

        # Agrólogo
        self.agrologo_var = tk.StringVar()
        
        ttk.Label(mod_proyecto, text='Agrólogo:').grid(row=1, column = 0, sticky='w')
        ttk.Entry(mod_proyecto,
                  width = 10,
                  textvariable = self.agrologo_var).grid(row=1, column = 1, sticky='w')

        # etiqueta rúbrica
        self.rubrica_var = tk.StringVar()
        
        ttk.Label(mod_proyecto,text = 'Rúbrica: ').grid(row = 1, column = 2, sticky = 'e')

        rubrica_choices =['Si', 'No']
        
        rubrica_combobox = ttk.Combobox(mod_proyecto, width = 7, textvariable = self.rubrica_var, values = rubrica_choices, state='readonly')
        rubrica_combobox.grid(row = 1, column = 3)
        rubrica_combobox.set('Si')

        # Sistema de referencia de coordenadas
        self.sistcoord_var = tk.StringVar()
        
        ttk.Label(mod_proyecto, text='SRC:').grid(row = 2, column = 0, sticky='e')
        ttk.Entry(mod_proyecto,
                  width = 10,
                  textvariable = self.sistcoord_var).grid(row = 2, column = 1, sticky='w')

        # este         
        self.este_var = tk.DoubleVar()
        
        ttk.Label(mod_proyecto, text = 'Este: ').grid(row = 2, column = 2, sticky = 'e')

        ttk.Entry(mod_proyecto,
                  width = 10,
                  textvariable = self.este_var,
                  validate ='key',
                  validatecommand = self.flotante_vcmd).grid(row = 2, column = 3)

        # norte
        self.norte_var = tk.DoubleVar()
        
        ttk.Label(mod_proyecto, text = 'Norte: ').grid(row = 2, column = 4, sticky = 'e')
        
        ttk.Entry(mod_proyecto,
                  width = 10,
                  textvariable = self.norte_var,
                  validate = 'key',
                  validatecommand = self.flotante_vcmd).grid(row = 2, column = 5)
        
        # =============================================================
        # MÓDULO 2: UBICACIÓN GEOGRÁFICA
        # =============================================================
        mod_ubi = ttk.LabelFrame(self, text="2. UBICACIÓN", padding=10)
        mod_ubi.grid(row = 0, column = 4, columnspan = 4, padx = 1, pady = 1, sticky = 'nsew')

        #ID punto      
        ttk.Label(mod_ubi, text='ID punto:').grid(row = 0, column = 0, sticky='w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.controller.IDpunto_var).grid(row = 0, column = 1, sticky='w')

        # Tipo descripción
        self.descripcion_var = tk.StringVar()
        
        ttk.Label(mod_ubi,text = 'Descripción: ').grid(row = 0, column = 2, sticky = 'e')

        descripcion_choices =['Barreno', 'Calicata']
        
        descripcion_combobox = ttk.Combobox(mod_ubi, width = 10, textvariable = self.descripcion_var, values = descripcion_choices, state='readonly')
        descripcion_combobox.grid(row = 0, column = 3)
        descripcion_combobox.set('Barreno')

        # localidad
        self.local_var = tk.StringVar()       

        ttk.Label(mod_ubi,text ='Localidad:').grid(row=0, column = 4, sticky = 'w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.local_var).grid(row=0, column = 5, sticky='w')
        
        # Estado
        self.estado_var = tk.StringVar()
        
        ttk.Label(mod_ubi, text='Estado:').grid(row = 1, column = 0, sticky='w')
        self.estado_option = {'Aragua': 1,
                              'Carabobo': 2,
                              'Guárico': 3,
                              'Miranda': 4,
                              'Portuguesa': 5}

 
        estado_choices = list(self.estado_option.keys())
        self.estado_combobox = ttk.Combobox(mod_ubi,
                                            width= 10,
                                            textvariable = self.estado_var,
                                            values=estado_choices,
                                            state='readonly')
        
        self.estado_combobox.grid(row=1, column = 1, sticky='w')
        self.estado_combobox.set(estado_choices[0])  # Set default value

        # Municipio
        self.munic_var = tk.StringVar()

        ttk.Label(mod_ubi, text='Municipio:').grid(row=1, column = 2, sticky='w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.munic_var).grid(row = 1, column = 3, sticky='w')

        # estacion experimental
        ttk.Label(mod_ubi, text='Estación:').grid(row = 1, column = 4, sticky='w')
        self.controller.estacion_option = {'Campo experimental': '1CE',
                                'Bajo Seco': '2BS',
                                'Dr. Jaime Henao, El Laurel': '3EL',
                                'Experta': '4EX',
                                'La Estancia': '5LE',
                                'Montalbán': '6MT',
                                'Nicolasito': '7NI',
                                'Biológica (Rancho Grande)':'8RG',
                                'Samán Mocho': '9SM',
                                'San Nicolás': '10SN',
                                'CENIAP': '11CE'}

        estacion_choices = list(self.controller.estacion_option.keys())
        self.controller.estacion_combobox = ttk.Combobox(mod_ubi,
                                              width = 20,
                                              textvariable = self.controller.estacion_var,
                                              values = estacion_choices,
                                              state = 'readonly')
        self.controller.estacion_combobox.grid(row=1, column = 5, sticky='w')
        self.controller.estacion_combobox.set('Campo experimental')  # Set default value

        # fotografía
        self.foto_var = tk.StringVar()

        ttk.Label(mod_ubi, text='Unid.Fotog.:').grid(row=2, column = 0, sticky='w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.foto_var).grid(row=2, column = 1, sticky='w')
        
        # altitud
        self.altitud_var = tk.DoubleVar()

        ttk.Label(mod_ubi, text = 'Altitud(msnm):').grid(row = 2, column = 2, sticky = 'w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.altitud_var,
                  validate = 'key',
                  validatecommand = self.flotante_vcmd).grid(row = 2, column = 3)

        # altitud máxima
        self.altmax_var = tk.DoubleVar()

        ttk.Label(mod_ubi,text = 'Alt.Máx.(msnm):').grid(row=2, column = 4, sticky = 'w')
        ttk.Entry(mod_ubi,
                  width = 10,
                  textvariable = self.altmax_var,
                  validate = 'key',
                  validatecommand = self.flotante_vcmd).grid(row = 2, column = 5, sticky = 'w')
        
        # =============================================================
        # MÓDULO 3: CONDICIÓN CLIMÁTICA
        # =============================================================
        mod_clima = ttk.LabelFrame(self, text= "3. COND. CLIMÁTICA ", padding=10)
        mod_clima.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'nsew')

        # Radiobutton Group (Condición climática)
        self.condclima_var = tk.StringVar(value='') # Default selected option       

        # Radiobuttons share the same variable (self.condclima_var)
        ttk.Radiobutton(mod_clima, text='Sol./Despej.', variable = self.condclima_var, value='1').grid(row = 0, column = 0,  sticky='w')
        ttk.Radiobutton(mod_clima, text='Parcial. nublado', variable = self.condclima_var, value='2').grid(row = 1, column = 0, sticky='w')
        ttk.Radiobutton(mod_clima, text='Nublado', variable = self.condclima_var, value='3').grid(row = 2, column = 0, sticky='w')
        ttk.Radiobutton(mod_clima, text='Lluvioso', variable = self.condclima_var, value='4').grid(row = 3, column = 0, sticky='w')

        # =============================================================
        # MÓDULO 4: TAXONOMÍA Y ZONAS DE VIDA
        # =============================================================
        mod_taxon = ttk.LabelFrame(self, text= "4. TAXONOMÍA", padding=10)
        mod_taxon.grid(row =1, column = 1, columnspan = 3, rowspan = 2, padx = 1, pady = 1, sticky = 'nsew')
        
        # nombre suelo
        self.nombresuelo_var = tk.StringVar()
        
        ttk.Label(mod_taxon, text='Nombre suelo:').grid(row=0, column = 0, sticky='w')
        ttk.Entry(mod_taxon,
                  width = 15,
                  textvariable = self.nombresuelo_var).grid(row=0, column = 1, sticky='w')

        # taxón
        self.taxon_var = tk.StringVar()
        
        ttk.Label(mod_taxon, text='Unid.Tax.:').grid(row=1, column = 0, sticky='w')
        ttk.Entry(mod_taxon,
                  width = 15,
                  textvariable = self.taxon_var).grid(row=1, column = 1, sticky='w')

        # serie de suelo
        self.seriesuelo_var = tk.StringVar()
        
        ttk.Label(mod_taxon, text='Serie:').grid(row=0, column = 2, sticky='w')
        ttk.Entry(mod_taxon,
                  width = 15,
                  textvariable = self.seriesuelo_var).grid(row=0, column = 3, sticky='w')

        # fase de suelo
        self.fasesuelo_var = tk.StringVar()
        
        ttk.Label(mod_taxon, text='Fase:').grid(row = 1, column = 2, sticky='w')
        ttk.Entry(mod_taxon,
                  width = 15,
                  textvariable = self.fasesuelo_var).grid(row = 1, column = 3, sticky='w')

        # capacidad uso
        self.capuso_var = tk.StringVar()
            
        ttk.Label(mod_taxon, text='Capacidad Uso:').grid(row = 3, column = 0, sticky='w')
        capuso_combobox = ttk.Combobox(mod_taxon,
                                       width = 10,
                                       textvariable = self.capuso_var,
                                       values=['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'],
                                       state='readonly')
        capuso_combobox.grid(row = 3, column = 1, sticky='w')
        capuso_combobox.set('III')  # Set default value

        # Zona de vida
        self.holdridge_var = tk.StringVar()
        
        ttk.Label(mod_taxon, text='Zona de Vida:').grid(row = 4, column = 0, sticky='w')
        self.holdridge_option = {
            'Maleza desértica tropical': 1,
            'Monte espinoso tropical': 2,
            'Bosque muy seco tropical': 3,
            'Bosque seco tropical': 4,
            'Bosque húmedo tropical': 5,
            'Bosque muy húmedo tropical': 6,
            'Bosque espinoso premontano': 7,
            'Bosque seco premontano': 8,
            'Bosque húmedo premontano': 9,
            'Bosque muy húmedo premontano': 10,
            'Bosque pluvial premontano': 11,
            'Bosque seco montano bajo': 12,
            'Bosque húmedo montano bajo': 13,
            'Bosque muy húmedo montano bajo': 14,
            'Bosque pluvial montano bajo': 15,
            'Bosque húmedo montano': 16,
            'Bosque muy húmedo montano': 17,
            'Bosque pluvial montano': 18,
            'Páramo subalpino': 19,
            'Páramo pluvial subalpino': 20,
            'Tundra pluvial alpina': 21,
            'Nival': 22}

        holdridge_choices =list(self.holdridge_option.keys())

        self.holdridge_combobox = ttk.Combobox(mod_taxon,
                                               width = 20,
                                               textvariable = self.holdridge_var,
                                               values= holdridge_choices,
                                               state='readonly')
        self.holdridge_combobox.grid(row = 4, column = 1, columnspan = 2, sticky='w')
        self.holdridge_combobox.set(holdridge_choices[3])  # Set default value

        # =============================================================
        # MÓDULO 5: REGIÓN FISIOGRÁFICA, PAISAJE
        # =============================================================
        mod_fisiog = ttk.LabelFrame(self, text= "5. REGIÓN FISIOGRÁFICA, PAISAJE ", padding=10)
        mod_fisiog.grid(row = 1, column = 4, columnspan = 3, padx = 1, pady = 1, sticky = 'nsew')

        # región fisiográfica
        self.fisio_var = tk.StringVar()
        
        ttk.Label(mod_fisiog, text='Región fisiográfica:').grid(row = 0, column = 0, sticky='w')
        fisio_choices = ['Sistema de la Costa/Tramo Central/Serranía del Litoral/Depresiones Intermontanas/Depresión del Lago de Valencia/Cuenca Río Güey', '']
        fisio_combobox = ttk.Combobox(mod_fisiog,
                                      width = 30,
                                      textvariable = self.fisio_var,
                                      values=fisio_choices, state='readonly')
        fisio_combobox.grid(row = 0, column = 1, sticky='w')
        fisio_combobox.set('')  # Set default value

        # Paisaje
        self.paisaje_var = tk.StringVar()

        ttk.Label(mod_fisiog, text='Paisaje:').grid(row=0, column = 2, sticky='w')
        ttk.Entry(mod_fisiog,
                  width = 15,
                  textvariable = self.paisaje_var).grid(row=0, column = 3, sticky='w')
        
        # forma terreno
        self.formaterreno_var = tk.StringVar()
        
        ttk.Label(mod_fisiog, text='Forma terreno:').grid(row = 1, column = 0, sticky='w')
        ttk.Entry(mod_fisiog,
                  width = 15,
                  textvariable = self.formaterreno_var).grid(row = 1, column = 1, sticky='w')

        # microrasgo
        self.microrasgo_var = tk.StringVar()
        
        ttk.Label(mod_fisiog, text='Microrasgo:').grid(row = 1, column = 2, sticky='w')
        ttk.Entry(mod_fisiog,
                  width = 15,
                  textvariable = self.microrasgo_var).grid(row = 1, column = 3, sticky='w')
    
        # =============================================================
        # MÓDULO 6: COMPONENTE GEOMÓRFICO
        # =============================================================
        mod_geomorf = ttk.LabelFrame(self, text= "6. COMPONENTE GEOMÓRFICO ", padding=10)
        mod_geomorf.grid(row = 2, column = 0, columnspan = 4, rowspan = 2, padx = 1, pady = 1, sticky = 'nsew')
        
        # Radiobutton Group (componente geomorfico)
        self.compgeom_var = tk.StringVar(value='')

        # montaña
        compmont_label = ttk.Label(mod_geomorf,
                                   text = 'Montaña',
                                   background='snow3',
                                   border=3,
                                   width = 15).grid(row=0, column = 0)

        boton = ttk.Radiobutton(mod_geomorf, text= 'Tope (MT)', value = 1,
                                variable = self.compgeom_var).grid(row=1, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Ladera (MF)', value = 2,
                                variable = self.compgeom_var).grid(row=2, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio alto (UT)', value = 3,
                                variable = self.compgeom_var).grid(row=3, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio medio (CT)', value = 4,
                                variable = self.compgeom_var).grid(row=4, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio bajo (LT)', value = 5,
                                variable = self.compgeom_var).grid(row=5, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Aflor. roca (FF)', value = 6,
                        variable = self.compgeom_var).grid(row=6, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Base (MB)', value = 7,
                                variable = self.compgeom_var).grid(row=7, column = 0, sticky = 'w')
        
        # cerro
        compcerro_label = ttk.Label(mod_geomorf,
                                    text = 'Cerro',
                                    background='snow3',
                                    border=3,
                                    width = 15).grid(row=0, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Parteagua (IF)', value = 8,
                        variable = self.compgeom_var).grid(row=1, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Cresta (CT)', value = 9,
                        variable = self.compgeom_var).grid(row=2, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Pendiente (HS)', value = 10,
                        variable = self.compgeom_var).grid(row=3, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Naríz (NS)', value = 11,
                        variable = self.compgeom_var).grid(row=4, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Drenes (SS)', value = 12,
                        variable = self.compgeom_var).grid(row=5, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Aflor. roca (FF)', value = 13,
                        variable = self.compgeom_var).grid(row=6, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_geomorf, text= 'Base (BS)', value = 14,
                        variable = self.compgeom_var).grid(row=7, column = 1, sticky = 'w')

        # terraza
        compterraza_label = ttk.Label(mod_geomorf,
                                      text = 'Terraza',
                                      background='snow3',
                                      border=3,
                                      width = 15,
                                      anchor = 'center').grid(row=0, column = 2)
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Pared (RI)', value = 15,
                                variable = self.compgeom_var)
        boton.grid(row=1, column = 2, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Huella (TR)', value = 16,
                                variable = self.compgeom_var)
        boton.grid(row=2, column = 2, sticky = 'w')
        
        # plano
        compplano_label = ttk.Label(mod_geomorf, text = 'Plano',
                                    background='snow3', border=3, width = 15,  anchor = 'center')
        compplano_label.grid(row=3, column = 2)
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Elevado (RI)', value = 17,
                                variable = self.compgeom_var)
        boton.grid(row=4, column = 2, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Llano (TF)', value = 18,
                                variable = self.compgeom_var)
        boton.grid(row=5, column = 2, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Bajo (DP)', value = 19,
                                variable = self.compgeom_var)
        boton.grid(row=6, column = 2, sticky = 'w')

        #aluvial
        compaluvial_label = ttk.Label(mod_geomorf, text = 'Aluvial',
                                      background='snow3', border = 3, width = 15, anchor = 'center')
        compaluvial_label.grid(row=0, column = 3)
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Banco (BN)', value = 20,
                        variable = self.compgeom_var)
        boton.grid(row=1, column = 3, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Bajío (BJ)', value = 21,
                                variable = self.compgeom_var)
        boton.grid(row=2, column = 3, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Estero (BS)', value = 22,
                                variable = self.compgeom_var)
        boton.grid(row=3, column = 3, sticky = 'w')

        # segmento ladera
        self.compsegm_var = tk.StringVar(value='')
        
        compsegm_label = ttk.Label(mod_geomorf,
                                   text = 'Segmento ladera',
                                   background='snow3',
                                   border=3,
                                   width = 15,
                                   anchor = 'center').grid(row = 0, column = 4)

        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio alto (TA)', value = 1,
                                variable = self.compsegm_var).grid(row=1, column = 4, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio medio (TM)', value = 2,
                        variable = self.compsegm_var).grid(row=2, column = 4, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Tercio bajo (TB)', value = 3,
                                variable = self.compsegm_var).grid(row=3, column = 4, sticky = 'w')

        # posicion ladera punto
        self.comppunto_var = tk.StringVar(value='')
        
        comppunto_label = ttk.Label(mod_geomorf,
                                    text = 'Posición ladera',
                                    background='snow3',
                                    border=3,
                                    width = 15,
                                    anchor = 'center').grid(row = 4, column = 3, columnspan = 2)

        boton = ttk.Radiobutton(mod_geomorf, text= 'Cumbre (SU)', value = 1,
                                variable = self.comppunto_var).grid(row = 5, column = 3, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Hombro (SH)', value = 2,
                                variable = self.comppunto_var).grid(row = 6, column = 3, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Ladera (BS)', value = 3,
                                variable = self.comppunto_var).grid(row = 7, column = 3, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Pie ladera (FS)', value = 4,
                                variable = self.comppunto_var).grid(row = 5, column = 4, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_geomorf, text= 'Planicie (TS)', value = 5,
                                variable = self.comppunto_var).grid(row = 6, column = 4, sticky = 'w')

        # =============================================================
        # MÓDULO 7: MICRORELIEVE
        # =============================================================
        mod_micro = ttk.LabelFrame(self, text= "7. MICRORELIEVE", padding=10)
        mod_micro.grid(row = 2, column = 4, padx = 1, pady = 1, sticky = 'nsew')
        
        # microrelieve
        self.microrel_var = tk.StringVar()
        
        boton = ttk.Radiobutton(mod_micro,text='Micro alto', value = 1,
                                variable = self.microrel_var).grid(row = 0, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_micro,text='Micro pendiente', value = 2,
                                variable = self.microrel_var).grid(row = 1, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_micro,text='Micro bajo', value = 3,
                                variable = self.microrel_var).grid(row = 2, column = 0, sticky = 'w')

        # =============================================================
        # MÓDULO 8: PENDIENTE
        # =============================================================
        mod_pend = ttk.LabelFrame(self, text= "8. PENDIENTE ", padding=10)
        mod_pend.grid(row = 2, column = 5, rowspan = 2, padx = 1, pady = 1, sticky = 'nsew')
        
        # aspecto pendiente
        self.asppend_var = tk.StringVar()

        asppend_label = ttk.Label(mod_pend,text = 'Aspecto pend. (grados):')
        asppend_label.grid(row=9, column = 6, sticky = 'w')

        self.asppend_entrybox = ttk.Entry(mod_pend, width = 15,
                                          textvariable = self.asppend_var,
                                          validate = 'key',
                                          validatecommand = self.vcmd_range
                                          ).grid(row=9, column = 7)

        # complejidad pendiente
        self.comppend_var = tk.StringVar()

        comppend_label = ttk.Label(mod_pend,
                                   text = 'Complejidad pend.',
                                   background='snow3',
                                   border=3,
                                   width = 15,
                                   anchor='center').grid(row=10, column = 6)
        
        boton = ttk.Radiobutton(mod_pend,text='Simple', value = 1,
                                variable = self.comppend_var).grid(row=11,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Compleja', value = 2,
                                variable = self.comppend_var).grid(row=12,column = 6, sticky = 'w')

        # clase pendiente
        self.clasepend_var = tk.StringVar()
        
        clasepend_label = ttk.Label(mod_pend,
                                    text = 'Clase pendiente',
                                    background='snow3',
                                    border=3,
                                    width = 15,
                                    anchor='center').grid(row=13, column = 6)
        
        boton = ttk.Radiobutton(mod_pend,text='Plano (0-2%)', value = 1,
                                variable = self.clasepend_var).grid(row=14,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Median.incl (2-6%)', value = 2,
                                variable = self.clasepend_var).grid(row=15,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Inclinado (6-13%)', value = 3,
                                variable = self.clasepend_var).grid(row=16,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Median.Escarp(13-25%)', value = 4,
                                variable = self.clasepend_var).grid(row=17,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Escarpado (25-55%)', value = 5,
                                variable = self.clasepend_var).grid(row=18,column = 6, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Muy Escarp.(>55%)', value = 6,
                                variable = self.clasepend_var).grid(row=19,column = 6, sticky = 'w')

        # forma pendiente
        self.foroptionend_var = tk.StringVar()
        
        foroptionend_label = ttk.Label(mod_pend,
                                       text = 'Forma pendiente',
                                       background='snow3',
                                       border=3,
                                       width = 15,
                                       anchor='center').grid(row=10, column = 7)
         
        boton = ttk.Radiobutton(mod_pend,text='Lineal-lineal (LL)', value = 1,
                                variable = self.foroptionend_var).grid(row=11,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Lineal-cóncava (LV)', value = 2,
                                variable = self.foroptionend_var).grid(row=12,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Lineal-convexa (LC)', value = 3,
                                variable = self.foroptionend_var).grid(row=13,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Convexa-lineal (VL)', value = 4,
                                variable = self.foroptionend_var).grid(row=14,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Convexa-convexa (VV)', value = 5,
                                variable = self.foroptionend_var).grid(row=15,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Convexa-cóncava (VC)', value = 6,
                                variable = self.foroptionend_var).grid(row=16,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Cóncava-lineal (CL)', value = 7,
                               variable = self.foroptionend_var).grid(row=17,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Cóncava-convexa (CV)', value = 8,
                                variable = self.foroptionend_var).grid(row=18,column = 7, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_pend,text='Cóncava-cóncava (CC)', value = 9,
                                variable = self.foroptionend_var).grid(row=19,column = 7, sticky = 'w')

        # =============================================================
        # MÓDULO 9: MATERIAL PARENTAL
        # =============================================================
        mod_mp = ttk.LabelFrame(self, text= "9. MATERIAL PARENTAL", padding=10)
        mod_mp.grid(row = 3, column = 4, padx = 1, pady = 1, sticky = 'nsew')

        #etiqueta material parental
        self.parental_var = tk.StringVar()

        boton = ttk.Radiobutton(mod_mp,text='In situ', value = 'S',
                                variable = self.parental_var).grid(row = 0, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_mp,text='Misceláneos', value = 'I',
                               variable = self.parental_var).grid(row = 1, column = 0, sticky = 'w')
                
        boton = ttk.Radiobutton(mod_mp,text='Masa', value = 'M',
                                variable = self.parental_var).grid(row = 2, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_mp,text='Hídrico', value = 'H',
                                variable = self.parental_var).grid(row = 3, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_mp,text='Glacial', value = 'G',
                                variable = self.parental_var).grid(row = 0, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_mp,text='Eólico', value = 'E',
                                variable = self.parental_var).grid(row = 1, column = 1, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_mp,text='Orgánico', value = 'O',
                                variable = self.parental_var).grid(row = 2, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_mp,text='Antrópico', value = 'A',
                                variable = self.parental_var).grid(row = 3, column = 1, sticky = 'w')

        # Código 3 letras Material parental
        self.codigomp_var = tk.StringVar()      
        ttk.Label(mod_mp,text = 'Código MP:').grid(row = 4, column = 0, sticky = 'w')
        
        self.codigomp_option = {
            'Aluvial': 'ALL',
            'Aluviones laderas de valles': 'VSA',
            'Aluviones taludes': 'SAL',
            'Arena de playa': 'BES',
            'Arena eólica': 'EOS',
            'Areniscas verdes': 'GRS',
            'Basal': 'BTI',
            'Bauxita': 'BAU',
            'Bloques desprendidos o deslizados': 'SLB',
            'Bomba volcánica': 'BOM',
            'Ceniza volcánica ácida': 'ASA',
            'Ceniza volcánica andesita': 'ASN',
            'Ceniza volcánica basáltica': 'ASB',
            'Ceniza volcánica': 'ASH',
            'Cenizas': 'CIN',
            'Coluvión': 'COL',
            'Cryoturbado': 'CRY',
            'Depósito arrugamiento del suelo': 'CRP',
            'Depósito avalancha de escombros': 'DAD',
            'Depósito avalancha de rocas': 'RAD',
            'Depósito caída de rocas': 'RDF',
            'Depósito caída de tierra o suelo suelto': 'SFD',
            'Depósito caídas de escombros': 'DLD',
            'Depósito de caída': 'FAD',
            'Depósito de flujo': 'FLD',
            'Depósito soliflucción (FOD)': 'FOD',
            'Depósito soliflucción (SOD)': 'SOD',
            'Depósito de vuelco o derrumbe': 'TOD',
            'Depósito desliza. bloques': 'BGD',
            'Depósito desliza. escombros (DSD)': 'DSD',
            'Depósito desliza. escombros (OSD)': 'OSD',
            'Depósito desliza. o depósito lateral': 'SD',
            'Depósito desliza. rotacional escombros': 'RDD',
            'Depósito desliz. rotacional de rocas': 'RRD',
            'Depósito desliza. rotacional de tierra': 'RED',
            'Depósito desliza. rotacional': 'RLD',
            'Depósito desliza. translacional escombros': 'TDD',
            'Depósito desliza. translacional rocas': 'TRD',
            'Depósito desliza. translacional tierra': 'TED',
            'Depósito desliza. translacional': 'TSD',
            'Depósito dispersión de escombros': 'DPD',
            'Depósito dispersión de rocas': 'RSD',
            'Depósito dispersión de tierra': 'EPD',
            'Depósito en masa': 'MMD',
            'Depósito eólico': 'EOD',
            'Depósito estuarino': 'ESD',
            'Depósito flujo de arena': 'SAD',
            'Depósito flujo de escombros': 'DFD',
            'Depósito flujo de lodo': 'MFD',
            'Depósito fluviomarino': 'FMD',
            'Depósito glaciofluvial': 'GFD',
            'Depósito glaciolacustrino': 'GLD',
            'Depósito glaciomarino': 'GMD',
            'Depósito tierra fluída': 'EFD',
            'Depósito vuelco de escombros': 'DTD',
            'Depósito vuelco de tierra': 'RTD',
            'Depósitos de ciénagas': 'LGD',
            'Depósitos de lahares': 'LAV',
            'Depósitos de pantanos': 'BSD',
            'Depósitos desliza. tierras complejos': 'CLD',
            'Depósitos lacustrinos': 'LAD',
            'Depósitos marinos': 'MAD',
            'Depósitos sobre riberas': 'OBD',
            'Deriva': 'GRD',
            'Derretimiento': 'MTI',
            'Diamigton': 'DIM',
            'Dispersión lateral': 'LSD',
            'Escoria': 'SCO',
            'Flujo de escombros supraglacial': 'SGF',
            'Flujo piroclástico': 'PYF',
            'Flujo': 'FTI',
            'Fragmento roca en ladera': 'SCR',
            'Fragmentos granito granular': 'GRU',
            'Gypsita': 'GYP',
            'Lahar (flujo lodo volcánico, agua, roca y escombros)': 'LAH',
            'Lapilli': 'ALP',
            'Limonita': 'LIM',
            'Loess calcáreos': 'CLO',
            'Loess no calcáreo': 'NLO',
            'Loess': 'LOE',
            'Marga lacustrina (FVM)': 'FVM',
            'Marga lacustrina (FWM)': 'FWM',
            'Marga marina': 'CMA',
            'Marga': 'MAR',
            'Materia orgánica': 'ORM',
            'Material coprogénico (COM)': 'COM',
            'Materiales coprogénicos (COH)': 'COH',
            'Materiales transportados por personas': 'HTM',
            'MO grasosa': 'OGM',
            'MO herbácea': 'OHM',
            'MO leñosa': 'OWM',
            'MO musgo': 'OMM',
            'Oleada piroclástica': 'PFS',
            'Parna': 'PAR',
            'Piedra pómez': 'PUM',
            'Piroclástica': 'ASF',
            'Resíduo': 'RES',
            'Residuos dragado': 'DGD',
            'Residuos extracción carbón': 'CES',
            'Residuos extracción minerales metálicos': 'MSE',
            'Residuos minería, relleno terroso': 'MES',
            'Saprolita': 'SAP',
            'Sedimento ablación': 'ATI',
            'Sedimento escorrentía': 'OTW',
            'Sedimento presión': 'LTI',
            'Sedimento glaciar': 'TIL',
            'Sedimento subglaciar': 'GTI',
            'Sedimento supraglaciar derretido': 'PTI',
            'Sedimento supraglaciar': 'UTI',
            'Sedimentos pedológicos': 'PED',
            'Taludes': 'TAL',
            'Tierras diatomeas (hídricas)': 'DIH',
            'Tierras diatomeas': 'DIE',
            'Vuelco roca': 'ETD'}

        codigomp_choices = list(self.codigomp_option.keys())

        self.codigomp_combobox = ttk.Combobox(mod_mp,
                                              width = 20,
                                              textvariable = self.codigomp_var,
                                              values = codigomp_choices,
                                              state = 'readonly')
        self.codigomp_combobox.grid(row=4, column = 1)
        self.codigomp_combobox.set('Aluvial')

        # =============================================================
        # MÓDULO 10: DRENAJE
        # =============================================================
        mod_drenaje = ttk.LabelFrame(self, text= "10. DRENAJE", padding=10)
        mod_drenaje.grid(row =4, column = 0, columnspan = 4, padx = 1, pady = 1, sticky = 'nsew')
        
        # patron drenaje
        self.drenpatron_var = tk.StringVar()
        
        drenpatron_label = ttk.Label(mod_drenaje,
                                     text = 'Patrón',
                                     background='snow3',
                                     border=2,
                                     width = 15,
                                     anchor='center').grid(row = 0, column = 0, sticky = 'ew')

        boton = ttk.Radiobutton(mod_drenaje,text='Anular (AN)', value = 1,
                                variable = self.drenpatron_var).grid(row = 1, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Artificial (AR)', value = 2,
                                variable = self.drenpatron_var).grid(row = 2, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Centrípeto (CE)', value = 3,
                                variable = self.drenpatron_var).grid(row = 3, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Dendrítico (DN)', value = 4,
                                variable = self.drenpatron_var).grid(row = 4, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Trastornado (DR)', value = 5,
                                variable = self.drenpatron_var).grid(row=5,column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Sumidero (karts)', value = 6,
                                variable = self.drenpatron_var).grid(row = 0, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Paralelo (PA)', value = 7,
                                variable = self.drenpatron_var).grid(row = 1, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Pinnado (PI)', value = 8,
                                variable = self.drenpatron_var).grid(row = 2, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Radial (RA)', value = 9,
                               variable = self.drenpatron_var).grid(row = 3, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Rectangular (RE)', value = 10,
                                variable = self.drenpatron_var).grid(row = 4, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Dendrítico recto (TR)', value = 11,
                                variable = self.drenpatron_var).grid(row = 5, column = 1, sticky = 'w')

        # clase drenaje
        self.drenclase_var = tk.StringVar()
        
        drenclase_label = ttk.Label(mod_drenaje,
                                    text = 'Clase drenaje',
                                    background='snow3',
                                    border=3,
                                    width=20,
                                    anchor = 'center').grid(row=0, column = 2, columnspan = 2, sticky = 'ew')

        boton = ttk.Radiobutton(mod_drenaje,text='Subacuoso (SA)', value = 0,
                               variable = self.drenclase_var).grid(row=1,column = 2, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Muy pobre (VP)', value = 1,
                                variable = self.drenclase_var).grid(row=2, column = 2, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Pobre drenado (PD)', value = 2,
                                variable = self.drenclase_var).grid(row=3, column = 2, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Algo pobre (SP)', value = 3,
                                variable = self.drenclase_var).grid(row=4, column = 2, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Mod. bien drenado (MW)', value = 4,
                                variable = self.drenclase_var).grid(row=1, column = 3, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text='Bien drenado (WD)', value = 5,
                                variable = self.drenclase_var).grid(row=2, column = 3, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text= 'Algo excesiva (SE)', value = 6,
                                variable = self.drenclase_var).grid(row=3, column = 3, sticky = 'w')

        boton = ttk.Radiobutton(mod_drenaje,text= 'Exces. drenado (ED)', value = 7,
                                variable = self.drenclase_var).grid(row=4, column = 3, sticky = 'w')

        # =============================================================
        # MÓDULO 11:INUNDACION 
        # =============================================================
        mod_inun = ttk.LabelFrame(self, text="11. INUNDACION", padding=10)
        mod_inun.grid(row = 5, column = 0, columnspan = 2, padx = 1, pady = 1, sticky = 'nsew')

        # frecuencia
        self.frecinund_var = tk.StringVar()
        
        frecinund_label = ttk.Label(mod_inun,
                                    text = 'Frecuencia',
                                    background='snow3',
                                    border=3,
                                    width = 15,
                                    anchor='center').grid(row=0, column=0)

        boton = ttk.Radiobutton(mod_inun, text= 'Cada 500 años', value = 0,
                                variable = self.frecinund_var).grid(row = 0, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= 'Cada 100 años', value = 1,
                                variable = self.frecinund_var).grid(row = 1, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= '5 veces c/100 años', value = 2,
                                variable = self.frecinund_var).grid(row = 2, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= '>50veces c/100años', value = 3,
                                variable = self.frecinund_var).grid(row = 3, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= '6 meses/año', value = 4,
                                variable = self.frecinund_var).grid(row = 4, column = 0, sticky = 'w')

        # duración
        self.durinund_var = tk.StringVar()
        
        durinund_label = ttk.Label(mod_inun,
                                   text = 'Duración',
                                   background='snow3',
                                   border=3,
                                   width = 15,
                                   anchor='center').grid(row=0, column=1)

        boton = ttk.Radiobutton(mod_inun, text= 'Cortísima (<4h)', value = 1,
                                variable = self.durinund_var).grid(row=1, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= 'Muy corta (<48h)', value = 2,
                                variable = self.durinund_var).grid(row=2, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= 'Corta (<7 d)', value = 3,
                                variable = self.durinund_var).grid(row=3, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= 'Larga (<30 d)', value = 4,
                                variable = self.durinund_var).grid(row=4, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_inun, text= 'Muy larga (>30d)', value = 5,
                                variable = self.durinund_var).grid(row=5, column=1, sticky = 'w')

        #Meses inundados
        self.mesesinund_var = tk.StringVar(value='')
        
        mesesinund_label = ttk.Label(mod_inun,
                                     text = 'Meses inundación:',
                                     width = 15,
                                     anchor='e').grid(row=6, column=0)

        mesesinund_entrybox = ttk.Entry(mod_inun, width = 15,
                                        textvariable = self.mesesinund_var).grid(row=6, column=1)

        # =============================================================
        # MÓDULO 12:ENCHARCADO 
        # =============================================================
        mod_enchar = ttk.LabelFrame(self, text="12. ENCHARCADO 100 años", padding=10)
        mod_enchar.grid(row = 5, column = 2, columnspan =2, padx = 1, pady = 1, sticky = 'nsew')

        # frecuencia
        self.frecenchar_var = tk.StringVar()
        
        frecenchar_label = ttk.Label(mod_enchar,
                                     text = 'Frecuencia',
                                     background='snow3',
                                     border=3,
                                     width = 15,
                                     anchor='center').grid(row=0, column=0)

        boton = ttk.Radiobutton(mod_enchar, text= 'Nunca', value = 0,
                                variable = self.frecenchar_var).grid(row=1, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Raro (1-5)', value = 2,
                                variable = self.frecenchar_var).grid(row=1, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Ocasional (5-50)', value = 3,
                                variable = self.frecenchar_var).grid(row=2, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Frecuente (>50)', value = 4,
                                variable = self.frecenchar_var).grid(row=3, column=0, sticky = 'w')

        # duración
        self.durenchar_var = tk.StringVar(value = '')
        
        durenchar_label = ttk.Label(mod_enchar,
                                    text = 'Duración',
                                    background='snow3',
                                    border=3,
                                    width = 15,
                                    anchor='center').grid(row=0, column=1)

        boton = ttk.Radiobutton(mod_enchar, text= 'Cortísima (<2d)', value = 1,
                                variable = self.durenchar_var).grid(row=1, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Muy corta (<7d)', value = 2,
                                variable = self.durenchar_var).grid(row=2, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Larga (<30d)', value = 3,
                                variable = self.durenchar_var).grid(row=3, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_enchar, text= 'Muy larga (>30d)', value = 4,
                                variable = self.durenchar_var).grid(row=4, column=1, sticky = 'w')

        # Meses encharcados
        self.mesesenchar_var = tk.StringVar(value='')
        mesesenchar_label = ttk.Label(mod_enchar, text = 'Meses encharcado:',
                                      width = 15,  anchor='e').grid(row=5, column=0)

        mesesenchar_entrybox = ttk.Entry(mod_enchar,
                                         width = 15,
                                         textvariable = self.mesesenchar_var).grid(row=5, column=1)
        # Encharcado profundidad
        self.encharprof_var = tk.DoubleVar()

        ttk.Label(mod_enchar,text = 'Prof.Enchar(cm):').grid(row=6, column = 0, sticky = 'w')
        ttk.Entry(mod_enchar,
                  width = 10,
                  textvariable = self.encharprof_var,
                  validate = 'key',
                  validatecommand = self.flotante_vcmd).grid(row = 6, column = 1, sticky = 'w')
        
        # =============================================================
        # MÓDULO 13: FRAGMENTOS EN SUPERFICIE Y COBERTURA
        # =============================================================
        mod_fragsup = ttk.LabelFrame(self, text= "13. FRAG. EN SUPERFICIE Y TIPO COBERTURA", padding=10)
        mod_fragsup.grid(row = 4, column = 4, rowspan = 2, padx = 1, pady = 1, sticky = 'nsew')

        # Codigo tipo fragmentos superficie
        self.fragsup_var = tk.StringVar()
        
        self.fragsup_option = {'Ausentes': 'AUS',
                               'Bombas volcánicas': 'VB',
                               'Calcreta': 'CA',
                               'Carbón vegetal': 'CH',
                               'Cenizas': 'CI',
                               'Concre. carbonatadas': 'CAC',
                               'Concre. gibbsita': 'GBC',
                               'Concre. hierro-manganeso': 'FMC',
                               'Concre. sílice': 'SIC',
                               'Cuarcita': 'QZT',
                               'Cuarzo': 'QUA',
                               'Durinodes': 'DNN',
                               'Escoria': 'SCO',
                               'Frag. de conchas': 'SHF',
                               'Frag. de duripan': 'DUF',
                               'Frag. de ortstein': 'ORF',
                               'Frag. petrocálcicos': 'PEF',
                               'Frag. petroférricos': 'TCF',
                               'Frag. petrogípsicos': 'PGF',
                               'Lapilli volcánico': 'LA',
                               'Madera': 'WO',
                               'Nódulos carbonatados': 'CAN',
                               'Nódulos gibbsita': 'GBN',
                               'Nódulos hierro-manganeso': 'FMN',
                               'Nódulos hierro': 'FSN',
                               'Nódulos plintita': 'PLN',
                               'Rocas carbonatadas': 'CAR',
                               'Rocas ígneas': 'IGR',
                               'Rocas metam. foliadas': 'FMR',
                               'Rocas metamórficas': 'MMR',
                               'Rocas mixtas': 'MXR',
                               'Rocas sedimentarias': 'SED',
                               'Rocas volcánicas': 'VOL'}
        
        ttk.Label(mod_fragsup,
                  text = 'Tipo(código):',
                  background='snow3',
                  border=3,
                  width = 12,
                  anchor='center').grid(row=0, column=0)
               
        self.fragsup_combobox = ttk.Combobox(mod_fragsup,
                                             width = 18,
                                             textvariable = self.fragsup_var,
                                             values = list(self.fragsup_option.keys()),
                                             state = 'readonly')
        self.fragsup_combobox.grid(row = 0, column = 1, sticky = 'w')
        self.fragsup_combobox.set('Ausentes')

        # Clase de fragmentos
        self.clasefragm_var = tk.StringVar()
        
        self.clasefragm_label = ttk.Label(mod_fragsup,
                                          text = 'Clase',
                                          width = 15,
                                          anchor='center').grid(row = 1, column = 0)

        #caja entrada clase de fragmento
        boton = ttk.Radiobutton(mod_fragsup, text= 'Sin piedras', value = 0,
                                variable = self.clasefragm_var).grid(row = 2, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Pedregoso (0,01-0,1%)', value = 1,
                                variable = self.clasefragm_var).grid(row = 3, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Muy pedreg. (0,1-3%)', value = 2,
                        variable = self.clasefragm_var).grid(row = 4, column = 0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_fragsup, text= 'Ext. pedreg. (3-15%)', value = 3,
                        variable = self.clasefragm_var).grid(row = 5, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Escombroso (15-50%)', value = 4,
                                variable = self.clasefragm_var).grid(row = 6, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Muy escombroso(50-80%)', value = 5,
                                variable = self.clasefragm_var).grid(row = 7, column = 0, sticky = 'w')

        # afloramiento rocoso
        self.afloroca_var = tk.StringVar()
        
        afloroca_label = ttk.Label(mod_fragsup,
                                   text = 'Afloram. rocoso',
                                   background='snow3',
                                   border=3,
                                   width = 16,
                                   anchor='center').grid(row=1, column=1)

        boton = ttk.Radiobutton(mod_fragsup, text= 'Ninguno', value = 0,
                                variable = self.afloroca_var).grid(row = 2, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= '>50 metros', value = 1,
                                variable = self.afloroca_var).grid(row = 3, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= '20-50 metros', value = 2,
                                variable = self.afloroca_var).grid(row = 4, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= '5-20 metros', value = 3,
                                variable = self.afloroca_var).grid(row = 5, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= '2-5 metros', value = 4,
                                variable = self.afloroca_var).grid(row = 6, column = 1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= '<2 metros', value = 5,
                                variable = self.afloroca_var).grid(row = 7, column = 1, sticky = 'w')

        # cobertura
        self.cobertura_var = tk.StringVar()
        
        cobertura_label = ttk.Label(mod_fragsup,
                                    text = 'Tipo de Cobertura',
                                    background='snow3',
                                    border = 2,
                                    width = 15,
                                    anchor='center').grid(row = 8, column=0, columnspan = 2, sticky = 'ew')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Artificial', value = 0,
                                variable = self.cobertura_var).grid(row=9, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Estéril', value = 1,
                                variable = self.cobertura_var).grid(row=10, column=0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_fragsup, text= 'Cultivo', value = 2,
                                variable = self.cobertura_var).grid(row=11, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Pasto', value = 3,
                                variable = self.cobertura_var).grid(row=12, column=0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_fragsup, text= 'Arbusto cult.', value = 4,
                                variable = self.cobertura_var).grid(row=9, column=1, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_fragsup, text= 'Árboles', value = 5,
                                variable = self.cobertura_var).grid(row=10, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_fragsup, text= 'Agua', value = 6,
                                variable = self.cobertura_var).grid(row=11, column=1, sticky = 'w')

        
        # =============================================================
        # MÓDULO 14: EROSION
        # =============================================================
        mod_erosion = ttk.LabelFrame(self, text= "14. EROSION", padding=10)
        mod_erosion.grid(row =4, column = 5, padx = 1, pady = 1, sticky = 'nsew')

        #tipo
        self.erotipo_var = tk.StringVar(value='')

        erotipo_label = ttk.Label(mod_erosion,
                                  text = 'Tipo erosión',
                                  background='snow3',
                                  border=3,
                                  width = 15,
                                  anchor='center').grid(row = 0, column=0)

        boton = ttk.Radiobutton(mod_erosion, text= 'Eólica', value = 'E',
                        variable = self.erotipo_var).grid(row = 1, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= 'Hídrica laminar', value = 'L',
                                variable = self.erotipo_var).grid(row = 2, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= 'Hídrica surcos', value = 'S',
                                variable = self.erotipo_var).grid(row = 3, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= 'Hídrica cárcavas', value = 'C',
                                variable = self.erotipo_var).grid(row = 4, column = 0, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= 'Hídrica túnel', value = 'T',
                                variable = self.erotipo_var).grid(row = 5, column = 0, sticky = 'w')

        # clase
        self.eroclase_var = tk.StringVar()
        
        eroclase_label = ttk.Label(mod_erosion,
                                   text = 'Clase (Hor. A+E)',
                                   background='snow3',
                                   border=3,
                                   width=20,
                                   anchor='center').grid(row=0, column=1)

        boton = ttk.Radiobutton(mod_erosion, text= 'Ninguno (0%)', value = '0',
                                variable = self.eroclase_var).grid(row=1, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= '(0-25%)', value = '1',
                                variable = self.eroclase_var).grid(row=2, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= '(25-75%)', value = '2',
                                variable = self.eroclase_var).grid(row=3, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= '(75-100%)', value = '3',
                                variable = self.eroclase_var).grid(row=4, column=1, sticky = 'w')

        boton = ttk.Radiobutton(mod_erosion, text= '(>100%)', value = '4',
                                variable = self.eroclase_var).grid(row=5, column=1, sticky = 'w')

        # =============================================================
        # MÓDULO 15: USO ACTUAL, COBERTURA (%)
        # =============================================================
        mod_cob = ttk.LabelFrame(self, text= "15. USO ACTUAL, COBERTURA", padding=10)
        mod_cob.grid(row = 5, column = 5, padx = 1, pady = 1, sticky = 'nsew')
        
        # uso actual
        self.usoactual_var = tk.StringVar()

        boton = ttk.Radiobutton(mod_cob, text= 'Cultivo', value = 1,
                                variable = self.usoactual_var).grid(row=0, column=0, sticky = 'w')
        
        boton = ttk.Radiobutton(mod_cob, text= 'Banco germoplasma', value = 2,
                                variable = self.usoactual_var).grid(row=1, column=0, sticky = 'w')

        boton = ttk.Radiobutton(mod_cob, text= 'Reservorio', value = 3,
                                variable = self.usoactual_var).grid(row=0, column=1, sticky = 'w')

        # vegetación y porcentaje
        # Nombre vulgar
        self.vegetanv_var = tk.StringVar()
        
        vegetanv_label = ttk.Label(mod_cob, text = 'Vegetación (NV, %):',
                                     width=20,  anchor='center').grid(row=2, column=0)

        vegetacion_entrybox = ttk.Entry(mod_cob,
                                        width = 20,
                                        textvariable = self.vegetanv_var).grid(row=2, column=1)

        # Nombre científico
        self.vegetanc_var = tk.StringVar()
        
        vegetanc_label = ttk.Label(mod_cob,
                                   text = 'Vegetación (NC, %):',
                                   width=20,
                                   anchor='center').grid(row=3, column=0)

        vegetanc_entrybox = ttk.Entry(mod_cob,
                                      width = 20,
                                      textvariable = self.vegetanc_var).grid(row=3, column=1)

        # Nota
        self.nota_var = tk.StringVar()
        
        nota_label = ttk.Label(mod_cob,
                                   text = 'Notas:',
                                   width=20,
                                   anchor='center').grid(row=4, column=0)

        nota_entrybox = ttk.Entry(mod_cob,
                                      width = 20,
                                      textvariable = self.nota_var).grid(row=4, column=1)        

        # =============================================================
        # MÓDULO 16: BOTONES DE DESPLAZAMIENTO
        # =============================================================  
        #Next Button to navigate to Page 2
        button_container = ttk.Frame(self)
        button_container.grid(row = 0, column = 6, padx = 1, pady = 1, sticky = 'nsew')
        
        next_button = ttk.Button(button_container, text='Página 2', command=self.go_to_next_page)
        next_button.grid(row=0, column = 0) # pady for spacing

        # Configure grid column weights for responsiveness
        self.grid_columnconfigure(7, weight=1)
        
        # Configure a row weight to push the button towards the bottom if window resizes
        self.grid_rowconfigure(1, weight=1)

        # --- FUNCIONES ---

    def validate_date(self, new_text):
        """
        Función que valida si el texto introducido es una fecha válida en formato DD/MM/AAAA.
        Retorna True si es válida, False en caso contrario.
        """
        # Si el campo está vacío, es válido (para permitir borrar el contenido)
        if not new_text:
            self.fecha_entry.config(foreground='black') # Restaurar color si está vacío
            return True

        # Intenta analizar la fecha con el formato esperado
        try:
            # Intentar parsear la fecha con el formato 'AAAA/MM/DD'
            # La directiva '%Y/%m/%d' requiere año de 4 dígitos, mes 2 dígitos y día 2 dígitos
            datetime.strptime(new_text, '%Y/%m/%d')
            
            # Si tiene éxito, la fecha es válida
            self.fecha_entry.config(foreground='black') # Color normal
            return True
        except ValueError:
            # Si hay un ValueError, la fecha no coincide con el formato o no es real (ej. 30/02/2023)
            # Solo cambiar el color de texto a rojo si el texto tiene el largo de una fecha completa
            if len(new_text) == 10:
                self.fecha_entry.config(foreground='red') # Indica error
            else:
                self.fecha_entry.config(foreground='black') # Color normal mientras se escribe

            # Permite continuar escribiendo hasta que se alcance el formato completo para la validación final.
            # Puedes ajustar esta lógica dependiendo de si quieres restringir la entrada de caracteres.
            return True 
            
        except Exception:
            # Para cualquier otro error (poco probable aquí)
            self.fecha_entry.config(foreground='red')
            return False

    def _update_entry_style(self, entry_widget, is_valid, current_text):
        """Función auxiliar para aplicar estilos."""
        VALID_FG = 'black'
        VALID_STYLE = 'Valid.TEntry'
        INVALID_FG = 'red'
        INVALID_STYLE = 'Invalid.TEntry'
        
        # Longitud esperada (10 para fecha, 8 para hora 00:00 AM)
        expected_len = 10 if entry_widget is self.fecha_entry else 8
        
        if is_valid or not current_text:
            entry_widget.config(foreground=VALID_FG, style=VALID_STYLE)
        elif len(current_text) >= expected_len:
            entry_widget.config(foreground=INVALID_FG, style=INVALID_STYLE)
        else:
            entry_widget.config(foreground=VALID_FG, style=VALID_STYLE)
            
    def check_time_12hr(self, proposed_value, widget_name):
        if not proposed_value: return True
        
        try:
            # Solo dígitos y ':'
            if not all(char.isdigit() or char == ':' for char in proposed_value):
                return False
            
            if len(proposed_value) > 5: return False
            
            # Lógica de auto-insertar ':'
            if ':' not in proposed_value and len(proposed_value) == 2:
                hora = int(proposed_value)
                if 1 <= hora <= 12:
                    # Obtenemos el widget actual para actualizar SU variable
                    widget = self.nametowidget(widget_name)
                    var_name = widget.cget('textvariable')
                    self.setvar(var_name, proposed_value + ':')
                    widget.after(1, lambda: widget.icursor('end'))
                    return False
                return False # Si no es 1-12 no es hora válida
            
            # Validación de minutos si hay ':'
            if ':' in proposed_value:
                parts = proposed_value.split(':')
                h, m = parts[0], parts[1]
                if not h or not (1 <= int(h) <= 12): return False
                if len(m) > 2: return False
                if len(m) == 2 and not (0 <= int(m) <= 59): return False

            return True
        except:
            return False
        
    def validar_flotante(self, texto_nuevo):
        # La función de validación comprueba si el texto nuevo
        # es una cadena vacía o se puede convertir a float.
        if texto_nuevo == '':
            return True
        try:
            # Intentar convertir a float. Si falla, no es un número válido.
            float(texto_nuevo)
            return True
        except ValueError:
            # Si se produce un ValueError, la entrada no es un número válido.
            return False

    def validate_slope_range(self, P):
        """
        Valida que el texto ingresado sea un número entero entre 0 y 360.
        P: El valor que el campo Entry tendrá si se acepta la modificación.
        """
        if P == '':
            return True  # Permitir campo vacío
        
        # 1. Verificar que solo sean dígitos
        if not P.isdigit():
            self.bell() # Opcional: emite un sonido al intentar ingresar no-dígitos
            return False

        # 2. Convertir a entero y verificar el rango
        try:
            valor = int(P)
            if 0 <= valor <= 360:
                # El valor es válido
                return True
            else:
                # El valor está fuera del rango (ej. 361)
                self.bell()
                return False
        except ValueError:
            # En caso de error de conversión (poco probable después de isdigit)
            self.bell()
            return False

    def go_to_next_page(self):
        """
        Collects data from Page 1 widgets and passes it to the controller,
        then switches to Page 2.
        """
        estado_nombre = self.estado_var.get()
        estado_codigo = self.estado_option.get(estado_nombre, 'ERROR')

        estacion_nombre = self.controller.estacion_var.get()
        self.controller.estacion_codigo_var = self.controller.estacion_option.get(estacion_nombre, 'ERROR')

        holdridge_nombre = self.holdridge_var.get()
        holdridge_codigo = self.holdridge_option.get(holdridge_nombre, 'ERROR')

        codigomp_nombre = self.codigomp_var.get()
        codigomp_codigo = self.codigomp_option.get(codigomp_nombre, 'ERROR')

        fragsup_nombre = self.fragsup_var.get()
        fragsup_codigo = self.fragsup_option.get(fragsup_nombre, 'ERROR')

        '''
        for key in ['ini', 'fin']:
            time_part = self.hora_vars[key]['time'].get()
            merid_part = self.hora_vars[key]['merid'].get()

            # Validación de completitud
            if len(time_part) < 4 or ':' not in time_part or len(time_part.split(':')[1]) != 2:
                tk.messagebox.showerror("Error", f"Formato de hora {key} incompleto.")
                return

            # Formateo HH:MM (zfill)
            h, m = time_part.split(':')
            formatted_time = f"{h.zfill(2)}:{m} {merid_part}"
            
            # Guardamos en el diccionario de salida
            label = 'hora0' if key == 'ini' else 'horafin'
            data[label] = formatted_time

        self.controller.update_form_data('PageOne', data)
        self.controller.show_frame('PageTwo')
        '''

       # 1. Inicializar el diccionario donde guardaremos todo
        data = {}
        valores_comparativos = {}

        # 2. Extraer datos del nuevo diccionario self.hora_vars
        for key in ['ini', 'fin']:
            # Acceso correcto al nuevo formato de diccionario
            time_part = self.hora_vars[key]['time'].get()
            merid_part = self.hora_vars[key]['merid'].get()

            # Validación de que no esté vacío o incompleto
            if len(time_part) < 4 or ':' not in time_part:
                tk.messagebox.showerror("Error", f"La hora de {key} está incompleta.")
                return

            # Formateo HH:MM
            h, m = time_part.split(':')
            h_formateada = h.zfill(2)
            formatted_time = f"{h_formateada}:{m} {merid_part}"
            
            # Asignar al diccionario final con los nombres de tus columnas CSV
            label = 'hora0' if key == 'ini' else 'horafin'
            data[label] = formatted_time

            # Guardar valor numérico para comparar Inicio vs Fin
            h_int = int(h)
            if merid_part == 'PM' and h_int != 12: h_int += 12
            if merid_part == 'AM' and h_int == 12: h_int = 0
            valores_comparativos[key] = h_int * 100 + int(m)

        # 3. Validar que el fin sea después del inicio
        if valores_comparativos['fin'] <= valores_comparativos['ini']:
            tk.messagebox.showwarning("Reloj Inválido", 
                "La hora de fin debe ser posterior a la de inicio.")
            return

        # 4. Agregar el resto de campos (Asegúrate de que estas variables existan)
        # Sustituye estas líneas por las variables que realmente usas en tu app
        #data['idobserv'] = self.controller.IDpunto_var.get()
        # data['idestudio'] = self.controller.proyecto_var.get()
        # data['codestacion'] = self.estacion_var.get() # Ejemplo

        # 5. Enviar al controlador y saltar de página
        self.controller.update_form_data('PageOne', data)
        self.controller.show_frame('PageTwo')
        
        data = {
            'idobserv': self.controller.IDpunto_var.get(),
            'idestudio': self.controller.proyecto_var.get(),         
            'codestacion': self.controller.estacion_codigo_var,
            'codcondi_clima': self.condclima_var.get(),
            'codcomp_geomorfico': self.compgeom_var.get(), 
            'codpend_aspecto': self.asppend_var.get(),
            'codpend_forma': self.foroptionend_var.get(),
            'codpend_complejidad': self.comppend_var.get(),            
            'coddren_patron': self.drenpatron_var.get(),
            'coddren_clase': self.drenclase_var.get(),            
            'codladera_segmento': self.compsegm_var.get(),
            'codladera_posicion': self.comppunto_var.get(),
            'codmp_tipo': self.parental_var.get(),            
            'codmp_especifico': codigomp_codigo,
            'codmicrorelieve': self.microrel_var.get(),
            'coderos_tipo': self.erotipo_var.get(),
            'coderos_clase': self.eroclase_var.get(),
            'codfragsup_tipo': fragsup_codigo,
            'codfragsup_clase': self.clasefragm_var.get(),
            'codaflo_rocoso': self.afloroca_var.get(),
            'codinun_frecuencia': self.frecinund_var.get(),
            'codinun_duracion': self.durinund_var.get(),           
            'codenchar_frecuencia': self.frecenchar_var.get(),
            'codenchar_duracion': self.durenchar_var.get(),
            'codcobertura': self.cobertura_var.get(),
            'coduso_actual': self.usoactual_var.get(),
            'codpend_clase': self.clasepend_var.get(),
            'tipo_descripcion': self.descripcion_var.get(),          
            'este': self.este_var.get(),
            'norte': self.norte_var.get(),
            'altitud': self.altitud_var.get(),
            'altitud_max': self.altmax_var.get(),
            'suelo_nv': self.nombresuelo_var.get(),
            'taxon': self.taxon_var.get(),
            'capusoclas': self.capuso_var.get(),
            'agrologo': self.agrologo_var.get(),
            'fecha': self.fecha_var.get(),
            'hora0': self.hora_vars['ini']['time'].get(),
            'paisaje': self.paisaje_var.get(),
            'formaterreno': self.formaterreno_var.get(),
            'microrasgo': self.microrasgo_var.get(),
            'vegeta_nv': self.vegetanv_var.get(),
            'vegeta_nc': self.vegetanc_var.get(),
            'horafin': self.hora_vars['fin']['time'].get(),
            'rubrica': self.rubrica_var.get(),           
            'inunmeses': self.mesesinund_var.get(),
            'encharmeses': self.mesesenchar_var.get(),
            'enchar_profundidad': self.encharprof_var.get(),
            'serie_suelo': self.seriesuelo_var.get(),
            'fase_suelo': self.fasesuelo_var.get(),   
            'nota': self.nota_var.get(),
            'SRC': self.sistcoord_var.get(),
            
            'estado': estado_codigo,
            'municipio': self.munic_var.get(),
            'localidad': self.local_var.get(),
            'foto_aerea': self.foto_var.get(),           
            'codzona_vida': holdridge_codigo,
            'region_fisiografica': self.fisio_var.get(),
            }
        
        self.controller.update_form_data('PageOne', data)
        self.controller.show_frame('PageTwo')

    def reset_variables(self):
        """
        Resets the StringVars on this page to clear the form fields.
        """
        self.controller.IDpunto_var.set('')
        self.controller.proyecto_var.set('')
        self.local_var.set('')
        self.nota_var.set('')
        self.foto_var.set('')
        self.nombresuelo_var.set('')
        self.agrologo_var.set('')
        self.rubrica_var.set('')
        self.descripcion_var.set('')
        self.fecha_var.set('')

        for key in ['ini', 'fin']:
            self.hora_vars[key]['time'].set('')
            self.hora_vars[key]['merid'].set('AM')
                
        self.taxon_var.set('')
        self.sistcoord_var.set('')
        self.este_var.set(value = 0)
        self.norte_var.set(value = 0)
        self.altitud_var.set(value = 0)
        self.altmax_var.set(value = 0)
        self.encharprof_var.set(value = 0)
        
        estado_choices = list(self.estado_option.keys())
        self.estado_var.set(estado_choices[0] if estado_choices else '')
        self.controller.estacion_choices = list(self.controller.estacion_option.keys())
        self.controller.estacion_var.set(self.controller.estacion_choices[0] if self.controller.estacion_choices else '')
        
        self.munic_var.set('')
        self.controller.IDpunto_var.set('')
        self.capuso_var.set('III')
        self.agrologo_var.set('')

        holdridge_choices = list(self.holdridge_option.keys())
        self.holdridge_var.set(holdridge_choices[0] if holdridge_choices else '')

        self.condclima_var.set('')
        self.fisio_var.set('Sistema de la Costa/Tramo Central/Serranía del Litoral/Depresiones Intermontanas/Depresión del Lago de Valencia/Cuenca Río Güey')
        self.paisaje_var.set('')
        self.formaterreno_var.set('')
        self.microrasgo_var.set('')
        self.compgeom_var.set('')
        self.compsegm_var.set('')
        self.comppunto_var.set('')
        self.asppend_var.set('')
        self.comppend_var.set('')
        self.clasepend_var.set('')
        self.foroptionend_var.set('')
        self.microrel_var.set('')
        self.parental_var.set('')

        codigomp_choices = list(self.codigomp_option.keys())
        self.codigomp_var.set(codigomp_choices[0] if codigomp_choices else '')
 
        self.drenpatron_var.set('')
        self.drenclase_var.set('')
        self.frecinund_var.set('')
        self.durinund_var.set('')
        self.mesesinund_var.set('')
        self.frecenchar_var.set('')
        self.durenchar_var.set('')
        self.mesesenchar_var.set('')
        self.clasefragm_var.set('')

        fragsup_choices = list(self.fragsup_option.keys())
        self.fragsup_var.set(fragsup_choices[0] if fragsup_choices else '')
        
        self.afloroca_var.set('')
        self.erotipo_var.set('')
        self.eroclase_var.set('')
        self.cobertura_var.set('')
        self.usoactual_var.set('')
        self.vegetanv_var.set('')
        self.vegetanc_var.set('')

###################···········PAGE 2···········###################
class PageTwo(tk.Frame):
    """
    Represents the second page of the form.
    Contains one Entry widget and two Radiobutton widgets sharing one StringVar.
    """
    # 1. Definir los valores de Hue de Munsell Válidos para la validación  
    VALID_HUES = {'2.5R', '5R', '7.5R', '10R',
                  '2.5YR', '5YR', '7.5YR', '10YR',
                  '2.5Y', '5Y', '7.5Y', '10Y',
                  '2.5GY', '5GY', '7.5GY', '10GY',
                  '2.5G', '5G', '7.5G', '10G',
                  '5BG', '10BG', '5B', '10B',
                  '5PB', '5P', '5RP', 'N'}

    VALID_VALUES = {'2', '2.5', '3', '4', '5', '6',
                    '7', '8', '8.5', '9', '9.5'}
    
    VALID_CHROMA = {'1', '2', '3', '4', '6', '8'}
    
    def __init__(self, parent, controller):
        super().__init__(parent, padx=5, pady=5) # Add padding to the frame
        self.controller = controller

        ### Validaciones ###
        # 1. Registrar la función de validación
        # La función de validación se ejecutará cuando se intente modificar el Entry.
        # '%P' pasa el valor *posterior* de la entrada al validador.
        self.flotante_vcmd = (self.register(self.validar_flotante), '%P')

        # Número de horizontes
        self.num_filas = 15      

        # crear etiquetas e ingreso de datos ###############################
        # Estación experimental
        estacion_label = ttk.Label(self,text ='Est.:')
        estacion_label.grid(row=0, column = 0, sticky = 'w')
        proyecto_entrybox = ttk.Entry(self,
                                      width = 10,
                                      textvariable = self.controller.estacion_var,
                                      state = 'readonly')
        proyecto_entrybox.grid(row=0, column = 1, columnspan = 2, sticky='w')

        # Proyecto 
        proyecto_label = ttk.Label(self,text ='Proy.:')
        proyecto_label.grid(row=0, column = 3, sticky = 'w')
        proyecto_entrybox = ttk.Entry(self,
                                      width = 10,
                                      textvariable = self.controller.proyecto_var,
                                      state = 'readonly')
        proyecto_entrybox.grid(row=0, column = 4, sticky='w')
        
        # ID punto
        IDpunto_label = ttk.Label(self, text = 'ID punto: ')
        IDpunto_label.grid(row=0, column = 5, sticky = 'w')

        IDpunto_entrybox = ttk.Entry(self,
                                     width = 10,
                                     textvariable = self.controller.IDpunto_var,
                                     state = 'readonly')
        IDpunto_entrybox.grid(row=0, column = 6, sticky = 'w')

        # tipo de barreno
        self.barreno_option = {'Barreno abierto': 'BARA',
                               'Barreno cerrado': 'BARC',
                               'Calicata': 'CAL',
                               'Pala': 'PAL',
                               'Sonda hidráulica': 'HSON',
                               'Sonda manual': 'SON'}
        
        self.barreno_var = tk.StringVar()

        barreno_label = ttk.Label(self, text = 'Muestreador: ')
        barreno_label.grid(row = 0, column = 7, sticky = 'w')

        barreno_choices = list(self.barreno_option.keys())
        
        self.barreno_combobox = ttk.Combobox(self,
                                             width = 10,
                                             textvariable = self.barreno_var,
                                             values = barreno_choices,
                                             state = 'readonly')
        
        self.barreno_combobox.set(barreno_choices[0])
        self.barreno_combobox.grid(row=0, column=8)

        # Profundidad alcanzable (m)        
        self.prof_alc_m_var = tk.DoubleVar()
        
        ttk.Label(self, text = 'Prof.Alc.(m):').grid(row = 0, column = 9, sticky = 'e')

        ttk.Entry(self,
                  width = 10,
                  textvariable = self.prof_alc_m_var,
                  validate ='key',
                  validatecommand = self.flotante_vcmd).grid(row = 0, column = 10)

        # Identificación del estrato ======================================
        self.estrato_vars = []

        estrato_label = ttk.Label(self,
                                  text = 'Hor.',
                                  background='snow3',
                                  border = 1,
                                  width = 4,
                                  anchor='center'
                                  )
        estrato_label.grid(row = 2, column = 0, sticky = 'ew')

        for i in range(self.num_filas):
            estrato_num = i + 1

            self.estrato_vars.append(estrato_num)

            estrato_id_label = ttk.Label(self,
                                         text=str(estrato_num),
                                                  background='snow3',
                                                  width = 4,
                                                  anchor = 'center')
            estrato_id_label.grid(row = i + 4, column = 0)

         # Profundidad (cm)        
        self.prof_var = tk.IntVar()
        self.prof_vars = []
       
        prof_label = ttk.Label(self, text = 'Prof.',
                               background ='olive',
                               border = 1,
                               width = 5,
                               anchor='center'
                               )
        prof_label.grid(row=1, column=1, sticky = 'ew')
        prof1_label = ttk.Label(self,
                                text = '(cm)',
                                background ='olive',
                                border = 1,
                                width = 5,
                                anchor='center')
        prof1_label.grid(row=2, column=1, sticky = 'ew')

        # Registrar la función de validación
        vcmd = (self.register(self.validar_entero), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.prof_var = tk.StringVar(self)
            self.prof_vars.append(self.prof_var)

            # *** MODIFICACIÓN CLAVE 1: Enlazar el cambio de variable a la función de cálculo
            self.prof_var.trace_add('write',
                                    lambda name,
                                    index,
                                    mode,
                                    i=i: self.calcular_espesores(i))

            prof_entrybox = ttk.Entry(self,
                                      width = 5,
                                      textvariable = self.prof_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            prof_entrybox.grid(row=i + 4, column=1)

        # Espesor (cm) calculado a partir de las profundidades
        self.espesor_var = tk.IntVar()
        self.espesor_vars = []
              
        espesor_label = ttk.Label(self,
                                  text = 'Grosor',
                                  background='snow3',
                                  border = 1,
                                  width = 6,
                                  anchor='center'
                                  )
        espesor_label.grid(row=1, column=2, sticky = 'ew')
        
        espesor1_label = ttk.Label(self,
                                   text = '(cm)',
                                   background='snow3',
                                   border = 1,
                                   width = 6,
                                   anchor='center')
        espesor1_label.grid(row=2, column=2, sticky = 'ew')

        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.espesor_var = tk.IntVar(self)
            self.espesor_vars.append(self.espesor_var)

            espesor_entrybox = ttk.Entry(self,
                                         width = 6,
                                         textvariable = self.espesor_var,
                                         state = 'readonly'
                                         )
            espesor_entrybox.grid(row= i + 4, column=2)

        ## Color ########################################

        # Registramos los comandos de validación específicos
        self.vcmd_hue = (self.register(self._validate_hue), '%P')
        self.vcmd_value = (self.register(self._validate_value), '%P')
        self.vcmd_chroma = (self.register(self._validate_chroma), '%P')
        
        # ... (Variables y setup de labels se mantienen igual) ...

        # --- Variables para Color HÚMEDO ---
        self.matriz_colorhum_vars = []
        self.huehum_vars = []
        self.valorhum_vars = []
        self.chromahum_vars = []
        
        # --- Variables para Color SECO ---
        self.matriz_colorseco_vars = []
        self.hueseco_vars = []
        self.valorseco_vars = []
        self.chromaseco_vars = []
        
        # --- Variables para MOTEADOS (NUEVAS) ---
        self.colormota_vars = []
        self.huemota_vars = []
        self.valormota_vars = []
        self.chromamota_vars = []

        # --- Creación de Widgets ---
        self._setup_labels()
        self._setup_color_entries()

        ## DESIGNACION DE HORIZONTE #######################################
        self.horizonte_var = tk.StringVar()
        self.horizonte_vars = []

        horizonte_label = ttk.Label(self,
                                    text='Hor.',
                                    background='sandybrown',
                                    border = 1,
                                    width = 5,
                                    anchor='center'
                                    )
        horizonte_label.grid(row=1, column=11, sticky='ew')

        horizon_label = ttk.Label(self,
                                  text='Desig.',
                                  background='sandybrown',
                                  border = 1,
                                  width = 5,
                                  anchor='center'
                                  )
        horizon_label.grid(row=2, column=11, sticky='ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            self.horizonte_var = tk.StringVar(self)
            self.horizonte_vars.append(self.horizonte_var)

            self.horizonte_entrybox = ttk.Entry(self,
                                                width = 5,
                                                textvariable = self.horizonte_var
                                                )
            self.horizonte_entrybox.grid(row=i + 4, column=11)
  
        ## MOTEADOS #######################################
        # Etiqueta general moteados
        moteado_label = ttk.Label(self,
                                  text='Moteados',
                                  background='olive',
                                  border = 1,
                                  width = 6,
                                  anchor='center'
                                  )
        moteado_label.grid(row=1, column=12, columnspan = 5, sticky='ew')

        # Tipo moteado
        self.moteadotipo_var = tk.StringVar()
        self.moteadotipo_option = {'Ausente': '0',
                                   'Litológico': '1',
                                   'Redox': '2',
                                   'No redox': '3'}
        
        self.moteadotipo_vars = []
        self.moteadotipo_choices = list(self.moteadotipo_option.keys())

        moteadotipo_label = ttk.Label(self, text='Tipo', background = 'bisque')
        moteadotipo_label.grid(row=2, column=12, sticky = 'ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.moteadotipo_vars.append(var)

            seleccion_moteadotipo = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable=var,
                                                 values = self.moteadotipo_choices,
                                                 state='readonly'
                                                 )
            
            seleccion_moteadotipo.set(self.moteadotipo_choices[0])
            seleccion_moteadotipo.grid(row=i + 4, column=12)
        
        # Abundancia moteado
        self.moteadoabund_var = tk.StringVar()
        self.moteadoabund_option = {'Ausente': '0',
                                   'Poca (<2%)': '1',
                                   'Común (2-20)': '2',
                                   'Mucha (>20)': '3'}
        self.moteadoabund_vars = []
        self.moteadoabund_choices = list(self.moteadoabund_option.keys())
        
        moteadoabund_label = ttk.Label(self, text='Abund.', background = '#E6FFEE')
        moteadoabund_label.grid(row=2, column=13, sticky='ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.moteadoabund_vars.append(var)

            seleccion_moteadoabund = ttk.Combobox(self,
                                                  width = 6,
                                                  textvariable=var,
                                                  values = self.moteadoabund_choices,
                                                  state='readonly'
                                                  )
                                                       
            seleccion_moteadoabund.set(self.moteadoabund_choices[0])
            seleccion_moteadoabund.grid(row=i + 4, column=13)

        # Tamaño moteado
        self.moteadotama_var = tk.StringVar()
        self.moteadotama_option = {'Ausente': '0',
                                  '0,25 – 2 mm': '1',
                                  '2 – 5 mm': '2',
                                  '5 – 20 mm': '3'}
        self.moteadotama_vars = []
        self.moteadotama_choices = list(self.moteadotama_option.keys())

        # Etiqueta tamaño moteado
        moteadotama_label = ttk.Label(self, text='Tamaño', background = '#FFCCCC')
        moteadotama_label.grid(row=2, column=14, sticky='ew')
        
        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.moteadotama_vars.append(var)

            seleccion_moteadotama = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable=var,
                                                 values = self.moteadotama_choices,
                                                 state='readonly'
                                                 )
            
            seleccion_moteadotama.set(self.moteadotama_choices[0])
            seleccion_moteadotama.grid(row=i + 4, column=14)

        # Moteado contraste
        self.contraste_var = tk.StringVar()
        self.contraste_option = {'Ausente': '0',
                                 'Tenue': '1',
                                 'Distinguible': '2',
                                 'Conspicuo': '3'}

        self.contraste_vars = []
        self.contraste_choices = list(self.contraste_option.keys())
        
        contraste_label = ttk.Label(self,
                                    text='Contr.',
                                    background='white',
                                    width = 6,
                                    anchor='center'
                                    )
        contraste_label.grid(row=2, column=15, sticky='ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.contraste_vars.append(var)

            seleccion_contraste = ttk.Combobox(self,
                                               width=6,
                                               textvariable=var,
                                               values = self.contraste_choices,
                                               state='readonly')

            seleccion_contraste.set(self.contraste_choices[0])
            seleccion_contraste.grid(row=i + 4, column=15)
    
        # Moteado forma 
        self.formot_var = tk.StringVar()
        self.formot_option = {'Ausente': 'AU',
                              'Cúbico': 'CU',
                              'Cilíndrico': 'C',
                              'Dendrítico': 'D',
                              'Irregular': 'I',
                              'Lenticular': 'L',
                              'Pendular': 'PE',
                              'Plano': 'P',
                              'Reticular': 'R',
                              'Roseta':'RO',
                              'Esférico': 'S',
                              'Filamento': 'F'}

        self.formot_vars = []
        self.formot_choices = list(self.formot_option.keys())

        self.formot_label = ttk.Label(self, text='Forma',
                                      background='lavender',
                                      width = 8,
                                      anchor='center')
        self.formot_label.grid(row=2, column=16, sticky='ew')
       
        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.formot_vars.append(var)

            seleccion_formot = ttk.Combobox(self,
                                            width = 8,
                                            textvariable = var,
                                            values = self.formot_choices,
                                            state = 'readonly')
            
            seleccion_formot.set(self.formot_choices[0])
            seleccion_formot.grid(row=i + 4, column=16)

        ## PARTE INFERIOR      ############################################
        # Identificación del estrato ======================================
        self.estrato1_vars = []

        estrato1_label = ttk.Label(self,
                                  text = 'Hor.',
                                  background='snow3',
                                  border = 1,
                                  width = 4,
                                  anchor='center'
                                  )
        estrato1_label.grid(row = 21, column = 0, sticky = 'ew')

        for i in range(self.num_filas):
            estrato1_num = i + 1

            self.estrato1_vars.append(estrato1_num)

            estrato1_id_label = ttk.Label(self,
                                         text=str(estrato1_num),
                                                  background='snow3',
                                                  width = 4,
                                                  anchor = 'center')
            estrato1_id_label.grid(row = i + 24, column = 0)
 
        # Etiqueta efervescencia
        eferv_label = ttk.Label(self,
                                text='Eferv.',
                                background='wheat',
                                width = 7,
                                anchor='center')                    
        eferv_label.grid(row=20, column=1, sticky='ew')

        eferv_label1 = ttk.Label(self, text='Clase',
                                 background='wheat',
                                 width = 7,
                                 anchor='center')
        eferv_label1.grid(row=21, column=1, sticky='ew')

        self.eferv_var = tk.StringVar()                        
        self.eferv_option = {'Sin reacción': '0',
                             'Pocas burbujas': '1',
                             'Muchas burbujas': '2',
                             'Espuma ligera': '3',
                             'Espuma gruesa': '4'}
        
        self.eferv_vars = []        
        self.eferv_choices = list(self.eferv_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.eferv_vars.append(var)

            seleccion_eferv = ttk.Combobox(self,
                                           width = 7,
                                           textvariable=var,
                                           values = self.eferv_choices,
                                           state='readonly')

            seleccion_eferv.set(self.eferv_choices[0])
            seleccion_eferv.grid(row=i + 24, column=1)

        # Etiqueta Estado agua       
        estagua_label = ttk.Label(self, text='Estado',
                                 background='olive',
                                  width = 6,
                                  anchor='center')
        estagua_label.grid(row=20, column=2, sticky='ew')

        estagua1_label = ttk.Label(self,
                                   text='Agua',
                                   background='olive',
                                   width = 6,
                                   anchor='center')
        estagua1_label.grid(row=21, column=2, sticky='ew')
        
        self.estagua_var = tk.StringVar()
        self.estagua_option = {'Seco (> 1500 Kpa)': '0',
                              'Húmedo (< 1500 > 1 o > 0,5 Kpa)': '1',
                              'Mojado (≤ 1 o < 0,5 Kpa)': '2',
                              'No saciado (> 0 ≤ 1 o < 0,5 Kpa)': '3',
                              'Saciado (≤ 0 Kpa agua visible)': '4',
                              'Saturado (≥ 0 Kpa)': '5'}
        
        self.estagua_vars = []
        self.estagua_choices = list(self.estagua_option.keys())
        
        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.estagua_vars.append(var)

            seleccion_estagua = ttk.Combobox(self,
                                             width = 6,
                                             textvariable=var,
                                             values = self.estagua_choices,
                                             state='readonly')
            
            seleccion_estagua.set(self.estagua_choices[0])
            seleccion_estagua.grid(row=i + 24, column=2)
     
        # Textura al tacto
        self.textacto_var = tk.StringVar()
        self.textacto_valor = ('A', 'Aa', 'AL',
                               'F', 'FA', 'FL', 'Fa',
                               'FAa', 'FAL', 'aF',
                               'a', 'L')
        self.textacto_vars = []
        
        textacto_label = ttk.Label(self, text = 'Text.',
                                 background='bisque', width = 5,  anchor='center')
        textacto_label.grid(row=20, column=3, sticky = 'ew')

        textacto1_label = ttk.Label(self, text = 'tacto',
                                 background='bisque', width = 5,  anchor='center')
        textacto1_label.grid(row=21, column=3, sticky = 'ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            self.textacto_var = tk.StringVar(self)
            self.textacto_vars.append(self.textacto_var)

            self.seleccion_textacto = ttk.Combobox(self, width = 5,
                                        textvariable = self.textacto_var, state = 'readonly')
            self.seleccion_textacto['values'] = self.textacto_valor            
            self.seleccion_textacto.grid(row=i + 24, column=3)
            
        # Etiqueta plasticidad    
        self.plasticidad_label = ttk.Label(self,
                                           text='Plastic.',
                                           background='olive',
                                           width = 6,
                                           anchor='center')
        self.plasticidad_label.grid(row=20, column=4, sticky='ew')
        
        self.plasticidad_var = tk.StringVar()
        self.plasticidad_option = {'No plástico': '0',
                                   'Lig. plástico': '1',
                                   'Mod. plástico': '2',
                                   'Muy plástico': '3'}
        self.plasticidad_vars = []
        self.plasticidad_choices = list(self.plasticidad_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.plasticidad_vars.append(var)

            seleccion_plasticidad = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable=var,
                                                 values = self.plasticidad_choices,
                                                 state='readonly')
            
            seleccion_plasticidad.set(self.plasticidad_choices[0])
            seleccion_plasticidad.grid(row=i + 24, column=4)

        ## FRAGMENTOS ####################################################
        self.fragmentos_label = ttk.Label(self,
                                          text='Fragmentos',
                                          background='sandybrown',
                                          width = 6,
                                          anchor='center')
        self.fragmentos_label.grid(row=20, column=5, columnspan = 6, sticky='ew')

        # Tipo de fragmentos                
        self.fragtipo_label = ttk.Label(self,
                                        text='Tipo',
                                        background='olive',
                                        width = 6,
                                        anchor='center')
        self.fragtipo_label.grid(row=21, column=5, sticky='ew')

        self.fragtipo_option = {'Ausentes': 'AUS',
                               'Bombas volcánicas': 'VB',
                               'Calcreta': 'CA',
                               'Carbón vegetal': 'CH',
                               'Cenizas': 'CI',
                               'Concre. carbonatadas': 'CAC',
                               'Concre. gibbsita': 'GBC',
                               'Concre. hierro-manganeso': 'FMC',
                               'Concre. sílice': 'SIC',
                               'Cuarcita': 'QZT',
                               'Cuarzo': 'QUA',
                               'Durinodes': 'DNN',
                               'Escoria': 'SCO',
                               'Frag. de conchas': 'SHF',
                               'Frag. de duripan': 'DUF',
                               'Frag. de ortstein': 'ORF',
                               'Frag. petrocálcicos': 'PEF',
                               'Frag. petroférricos': 'TCF',
                               'Frag. petrogípsicos': 'PGF',
                               'Lapilli volcánico': 'LA',
                               'Madera': 'WO',
                               'Nódulos carbonatados': 'CAN',
                               'Nódulos gibbsita': 'GBN',
                               'Nódulos hierro-manganeso': 'FMN',
                               'Nódulos hierro': 'FSN',
                               'Nódulos plintita': 'PLN',
                               'Rocas carbonatadas': 'CAR',
                               'Rocas ígneas': 'IGR',
                               'Rocas metam. foliadas': 'FMR',
                               'Rocas metamórficas': 'MMR',
                               'Rocas mixtas': 'MXR',
                               'Rocas sedimentarias': 'SED',
                               'Rocas volcánicas': 'VOL'}
        
        self.fragtipo_vars =[]
        self.fragtipo_choices = list(self.fragtipo_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.fragtipo_vars.append(var)

            seleccion_fragtipo = ttk.Combobox(self,
                                              width = 6,
                                              textvariable=var,
                                              values = self.fragtipo_choices,
                                              state='readonly')
            
            seleccion_fragtipo.set(self.fragtipo_choices[0])
            seleccion_fragtipo.grid(row=i + 24, column=5)

        # Volumen de fragmentos                
        self.fragvolumen_label = ttk.Label(self,
                                        text='Volumen',
                                        background='bisque',
                                        width = 6,
                                        anchor='center')
        self.fragvolumen_label.grid(row=21, column=6, sticky='ew')

        self.fragvolumen_option = {'Sin fragmentos': 'SIN',
                                    'Gravoso': 'GR',
                                    'Finamente Gravoso': 'FGR',
                                    'Medianamente Gravoso': 'MGR',
                                    'Gruesamente Gravoso': 'CGR',
                                    'Muy Gravoso': 'VGR',
                                    'Ext. Gravoso': 'XGR',
                                    'Guijarros': 'CB',
                                    'Muchos Guijarros': 'VCB',
                                    'Ext. Pres. Guijarros': 'XCB',
                                    'Rocoso': 'ST',
                                    'Muy Rocoso':'VST',
                                    'Ext. Rocoso': 'XST',
                                    'Blocoso': 'BY',
                                    'Muy Blocoso': 'VBY',
                                    'Ext. Blocoso': 'XBY',
                                    'Guijarros Planos': 'CN',
                                    'Muchos Guijarros Planos': 'VCN',
                                    'Ext. Pres. Guijarros Planos': 'XCN',
                                    'Lajoso': 'FL',
                                    'Muy Lajoso': 'MFL',
                                    'Ext. Lajoso': 'XFL',
                                    'Paragravoso': 'PGR',
                                    'Muy Paragravoso': 'VPGR',
                                    'Ext. Paragravoso': 'XPGR'}
        
        self.fragvolumen_vars =[]
        self.fragvolumen_choices = list(self.fragvolumen_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.fragvolumen_vars.append(var)

            seleccion_fragvolumen = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable=var,
                                                 values = self.fragvolumen_choices,
                                                 state='readonly')
            
            seleccion_fragvolumen.set(self.fragvolumen_choices[0])
            seleccion_fragvolumen.grid(row=i + 24, column=6)

        # Tamaño fragmento
        self.fragtama_label = ttk.Label(self, text='Tamaño',
                                        background='snow3',
                                        width = 6,
                                        anchor='center')
        self.fragtama_label.grid(row=21, column=7, sticky='ew')

        self.fragtama_option = {'0 mm': 'no aplica',
                                'Ø= 2-76 mm': 'grava',
                                'Ø= 2-5 mm': 'grava fina',
                                'Ø= 5-20 mm': 'grava media',
                                'Ø= 20-76 mm': 'grava gruesa',
                                'Ø= 76-250 mm': 'guijarro',
                                'Ø= 250-600 mm': ' canto',
                                'Ø= 600 mm': 'bloque',
                                'L= 2-150 mm': ' guijarro plano',
                                'L= 150-380 mm': 'laja',
                                'L= 380-600 mm': 'canto plano',
                                'L= >600 mm': 'bloque plano'}

        self.fragtama_vars =[]
        self.fragtama_choices = list(self.fragtama_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.fragtama_vars.append(var)

            seleccion_fragtama = ttk.Combobox(self,
                                              width = 6,
                                              textvariable=var,
                                              values = self.fragtama_choices,
                                              state='readonly')
            
            seleccion_fragtama.set(self.fragtama_choices[0])
            seleccion_fragtama.grid(row=i + 24, column=7)

        # ==== Meteorización =====
        self.meteorizacion_label = ttk.Label(self,
                                        text = 'Meteorización',
                                        background='olive',
                                        width = 6,
                                        anchor='center')
        self.meteorizacion_label.grid(row = 21, column = 8, columnspan = 2, sticky = 'ew')
        
        # Redondez
        self.redondez_label = ttk.Label(self,
                                        text = 'Redon.',
                                        background='snow3',
                                        width = 6,
                                        anchor='center')
        self.redondez_label.grid(row=22, column=8, sticky = 'ew')
        
        self.redondez_var = tk.StringVar()
        
        self.redondez_option = {'Ninguna': '0',
                                'Muy angular': '0.5',
                                'Angular': '1.5',
                                'Subangular': '2.5',
                                'Subredondeado': '3.5',
                                'Redondeado': '4.5',
                                'Bien redondeado': '5.5'}
        self.redondez_vars = []
        self.redondez_choices = list(self.redondez_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.redondez_vars.append(var)

            seleccion_redondez = ttk.Combobox(self,
                                              width = 6,
                                              textvariable = var,
                                              values = self.redondez_choices,
                                              state = 'readonly')
            
            seleccion_redondez.set(self.redondez_choices[0])          
            seleccion_redondez.grid(row=i + 24, column=8)

        # Esfericidad
        self.esfericidad_label = ttk.Label(self,
                                        text = 'Esfer.',
                                        background='snow3',
                                        width = 6,
                                        anchor='center')
        self.esfericidad_label.grid(row=22, column=9, sticky = 'ew')
        
        self.esfericidad_var = tk.StringVar()
        
        self.esfericidad_option = {'Ninguna': '0',
                                   'Discoidal': '0.5',
                                   'Subdiscoidal': '1.5',
                                   'Esférica': '2.5',
                                   'Subprismoidal': '3.5',
                                   'Prismoidal': '4.5'}
        self.esfericidad_vars = []
        self.esfericidad_choices = list(self.esfericidad_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.esfericidad_vars.append(var)

            seleccion_esfericidad = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable = var,
                                                 values = self.esfericidad_choices,
                                                 state = 'readonly')
            
            seleccion_esfericidad.set(self.esfericidad_choices[0])          
            seleccion_esfericidad.grid(row=i + 24, column=9)

        # Porcentaje fragmentos 10 g suelo                
        self.fragporc_label = ttk.Label(self,
                                        text='% Frag.',
                                        background='bisque',
                                        width = 6,
                                        anchor='center')
        self.fragporc_label.grid(row=21, column=10, sticky='ew')

        self.fragporc_option = {'No gravoso (0%)': 'NGR',
                                'Gravoso (15-35%)': 'GR',
                                'Grava fina (15-35%)': 'FGR',
                                'Grava media (15-35%)': 'MGR',
                                'Grava gruesa (15-35%)': 'CGR',
                                'Muy Gravoso (35-60%)': 'VGR',
                                'Ext. Gravoso (60-90%)': 'XGR'}
        
        self.fragporc_vars =[]
        self.fragporc_choices = list(self.fragporc_option.keys())

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            var = tk.StringVar(self)
            self.fragporc_vars.append(var)

            seleccion_fragporc = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable = var,
                                                 values = self.fragporc_choices,
                                                 state='readonly')
            
            seleccion_fragporc.set(self.fragporc_choices[0])
            seleccion_fragporc.grid(row=i + 24, column = 10)
       
        """
        # Textura visual  (FAO)
                
        self.texvis_label = ttk.Label(self,
                                      text = 'Textura visual (FAO)',
                                      background='olive',
                                      border = 1,
                                      width = 6,
                                      anchor='center')
        self.texvis_label.grid(row=20, column=9, columnspan=4, sticky = 'ew')
        
        # Arena (%)
        self.arenavis_var = tk.IntVar()
        self.arenavis_vars = []
       
        self.arenavis_label = ttk.Label(self, text = 'Arena',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.arenavis_label.grid(row=21, column=9, sticky = 'ew')
        self.arenavis1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.arenavis1_label.grid(row=22, column=9, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_entero), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.arenavis_var = (tk.IntVar(self))
            self.arenavis_vars.append(self.arenavis_var)

            self.arenavis_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.arenavis_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.arenavis_entrybox.grid(row=i + 24, column=9)

        # limo (%)
        self.limovis_var = tk.IntVar()
        self.limovis_vars = []
       
        self.limovis_label = ttk.Label(self, text = 'Limo',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.limovis_label.grid(row=21, column=10, sticky = 'ew')
        self.limovis1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.limovis1_label.grid(row=22, column=10, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_entero), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.limovis_var = (tk.IntVar(self))
            self.limovis_vars.append(self.limovis_var)

            self.limovis_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.limovis_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.limovis_entrybox.grid(row=i + 24, column=10)

        # Arcilla (%)
        self.arcillavis_var = tk.IntVar()
        self.arcillavis_vars = []
       
        self.arcillavis_label = ttk.Label(self, text = 'Arcilla',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.arcillavis_label.grid(row=21, column=11, sticky = 'ew')
        self.arcillavis1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.arcillavis1_label.grid(row=22, column=11, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_entero), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.arcillavis_var = (tk.IntVar(self))
            self.arcillavis_vars.append(self.arcillavis_var)

            self.arcillavis_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.arcillavis_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.arcillavis_entrybox.grid(row=i + 24, column=11)
            
        # Clase textural visual       
        self.texvis_var = tk.StringVar()
        self.texvis_valor = ('A', 'Aa', 'AL',
                             'F', 'FA', 'FL',
                             'Fa', 'FAa', 'FAL',
                             'aF', 'a', 'L')
        self.texvis_vars = []


        self.texvis1_label = ttk.Label(self,
                                       text = 'Textura',
                                       background='snow3',
                                       border = 1,
                                       width = 6,
                                       anchor='center')
        self.texvis1_label.grid(row=21, column=12, sticky = 'ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            self.texvis_var = tk.StringVar(self)
            self.texvis_vars.append(self.texvis_var)

            self.seleccion_texvis = ttk.Combobox(self,
                                                 width = 6,
                                                 textvariable = self.texvis_var,
                                                 state = 'readonly'
                                                 )
            self.seleccion_texvis['values'] = self.texvis_valor            
            self.seleccion_texvis.grid(row=i + 24, column=12)

        # Textura Laboratorio     
        self.texlab_label = ttk.Label(self, text = 'Textura suelo (USDA)',
                                 background='bisque', border = 1, width = 6,  anchor='center')
        self.texlab_label.grid(row=20, column = 10, columnspan=4, sticky = 'ew')

        # Arena (%)
        self.arenalab_var = tk.DoubleVar()
        self.arenalab_vars = []
       
        self.arenalab_label = ttk.Label(self,
                                        text = 'Arena',
                                        background='olive',
                                        border = 1,
                                        width = 6,
                                        anchor='center'
                                        )
        self.arenalab_label.grid(row=21, column=10, sticky = 'ew')
        
        self.arenalab1_label = ttk.Label(self,
                                         text = '(%)',
                                         background='snow3',
                                         border = 1,
                                         width = 6,
                                         anchor='center'
                                         )
        self.arenalab1_label.grid(row=22, column=10, sticky = 'ew')

        # Registrar la función de validación
        vcmd = (self.register(self.validar_flotante), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.arenalab_var = (tk.IntVar(self))
            self.arenalab_vars.append(self.arenalab_var)

            self.arenalab_entrybox = ttk.Entry(self,
                                               width = 6,
                                               textvariable = self.arenalab_var,
                                               validate='key',
                                               validatecommand=vcmd
                                               )
            self.arenalab_entrybox.grid(row=i + 24, column=10)

        # limo (%)
        self.limolab_var = tk.DoubleVar()
        self.limolab_vars = []
       
        self.limolab_label = ttk.Label(self, text = 'Limo',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.limolab_label.grid(row=21, column=11, sticky = 'ew')
        self.limolab1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.limolab1_label.grid(row=22, column=11, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_flotante), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.limolab_var = (tk.IntVar(self))
            self.limolab_vars.append(self.limolab_var)

            self.limolab_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.limolab_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.limolab_entrybox.grid(row=i + 24, column=11)

        # Arcilla (%)
        self.arcillalab_var = tk.DoubleVar()
        self.arcillalab_vars = []
       
        self.arcillalab_label = ttk.Label(self, text = 'Arcilla',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.arcillalab_label.grid(row=21, column=12, sticky = 'ew')
        self.arcillalab1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.arcillalab1_label.grid(row=22, column=12, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_flotante), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.arcillalab_var = (tk.IntVar(self))
            self.arcillalab_vars.append(self.arcillalab_var)

            self.arcillalab_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.arcillalab_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.arcillalab_entrybox.grid(row=i + 24, column=12)

        # Clase textural laboratorio
        self.texlab_var = tk.StringVar()
        self.texlab_valor = ('A', 'Aa', 'AL',
                             'F', 'FA', 'FL', 'Fa',
                             'FAa', 'FAL', 'aF',
                             'a', 'L')
        self.texlab_vars = []

        self.texlab1_label = ttk.Label(self, text = 'Textura',
                                 background='snow3', border = 1, width = 6,  anchor='center')
        self.texlab1_label.grid(row=21, column=13, sticky = 'ew')

        # Bucle para crear los Combobox para cada fila
        for i in range(self.num_filas):
            self.texlab_var = tk.StringVar(self)
            self.texlab_vars.append(self.texlab_var)

            self.seleccion_texlab = ttk.Combobox(self, width = 6,
                                        textvariable = self.texlab_var, state = 'readonly')
            self.seleccion_texlab['values'] = self.texlab_valor            
            self.seleccion_texlab.grid(row=i + 24, column=13)
    """

        # Humedad (%)
        self.humedad_var = tk.DoubleVar()
        self.humedad_vars = []
       
        self.humedad_label = ttk.Label(self, text = 'Humedad',
                               background='olive', border = 1, width = 6,  anchor='center')
        self.humedad_label.grid(row=20, column=14, sticky = 'ew')
        self.humedad1_label = ttk.Label(self, text = '(%)',
                               background='snow3', border = 1, width = 6,  anchor='center')
        self.humedad1_label.grid(row=21, column=14, sticky = 'ew')

         # Registrar la función de validación
        vcmd = (self.register(self.validar_flotante), '%P')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.humedad_var = (tk.IntVar(self))
            self.humedad_vars.append(self.humedad_var)

            self.humedad_entrybox = ttk.Entry(self, width = 6,
                                      textvariable = self.humedad_var,
                                      validate='key',
                                      validatecommand=vcmd
                                      )
            self.humedad_entrybox.grid(row=i + 24, column=14)

        # Nº muestra alterada
        self.muestraalt_var = tk.StringVar()
        self.muestraalt_vars = []
        
        self.muestraalt_label = ttk.Label(self, text = 'NºMuestra',
                                 background='wheat', border = 1, width = 6,  anchor='center')
        self.muestraalt_label.grid(row=20, column=15, sticky = 'ew')
        
        self.muestraalt1_label = ttk.Label(self, text = 'alterada',
                                 background='wheat', border = 1, width = 6,  anchor='center')
        self.muestraalt1_label.grid(row=21, column=15, sticky = 'ew')

        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.muestraalt_var = tk.StringVar(self)
            self.muestraalt_vars.append(self.muestraalt_var)

            self.muestraalt_entrybox = ttk.Entry(self, width = 6,
                                        textvariable = self.muestraalt_var
                                        )            
            self.muestraalt_entrybox.grid(row=i + 24, column = 15)

        # Nº muestra no alterada
        self.muestranoalt_var = tk.StringVar()
        self.muestranoalt_vars = []
        
        self.muestranoalt_label = ttk.Label(self, text = 'NºMuestra',
                                 background='olive', border = 1, width = 6,  anchor='center')
        self.muestranoalt_label.grid(row=20, column=16, sticky = 'ew')
        
        self.muestranoalt1_label = ttk.Label(self, text = 'no alter.',
                                 background='olive', border = 1, width = 6,  anchor='center')
        self.muestranoalt1_label.grid(row=21, column=16, sticky = 'ew')
        
        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.muestranoalt_var = tk.StringVar(self)
            self.muestranoalt_vars.append(self.muestranoalt_var)

            self.muestranoalt_entrybox = ttk.Entry(self, width = 6,
                                        textvariable = self.muestranoalt_var
                                        )            
            self.muestranoalt_entrybox.grid(row=i + 24, column = 16)

        # Observaciones
        self.observaciones_var = tk.StringVar()
        self.observaciones_vars = []
        
        observaciones_label = ttk.Label(self, text = 'Observaciones',
                                 background='wheat', border = 1, width = 12,  anchor='center')
        observaciones_label.grid(row=20, column=17, columnspan = 3, sticky = 'ew')

        # Bucle para crear los Entrybox para cada fila
        for i in range(self.num_filas):
            self.observaciones_var = tk.StringVar(self)
            self.observaciones_vars.append(self.observaciones_var)

            observaciones_entrybox = ttk.Entry(self, width = 12,
                                        textvariable = self.observaciones_var
                                        )            
            observaciones_entrybox.grid(row=i + 24, column = 17, columnspan = 3)
            
        ## Buttons for navigation and submission ##########################
        back_button = ttk.Button(self, text='Regresar', command=lambda: controller.show_frame('PageOne'))
        back_button.grid(row=0, column = 19, sticky='w')

        submit_button = ttk.Button(self, text='Guardar', command=self.submit_form)
        submit_button.grid(row=0, column = 20, sticky='w')

        # Configure grid column weights for responsiveness
        self.grid_columnconfigure(1, weight=1)

        # Configure a row weight to push the buttons towards the bottom if window resizes
        self.grid_rowconfigure(4, weight=1)

    def validar_entero(self, nuevo_valor):
        """
        Esta función se ejecutará cada vez que se presione una tecla en el Entry.
        'nuevo_valor' (%P) es el valor final del Entry después de la edición.
        """
        # Aceptar cadena vacía para permitir borrar el contenido
        if nuevo_valor == '':
            return True
        
        # Verificar si el valor es un entero
        try:
            int(nuevo_valor)
            return True
        except ValueError:
            # Si no se puede convertir a entero, no permitir la entrada
            return False

    def validar_flotante(self, nuevo_valor):
        """
        Esta función se ejecutará cada vez que se presione una tecla en el Entry.
        'nuevo_valor' (%P) es el valor final del Entry después de la edición.
        """
        # Permitir una cadena vacía para borrar el contenido
        if nuevo_valor == '':
            return True

        """
        # Permitir el signo de menos al inicio para números negativos
        if nuevo_valor == '-':
            return True
        # Verificar si el valor es un flotante
        """
        try:
            float(nuevo_valor)
            return True
        except ValueError:
            # Si no se puede convertir a flotante, no permitir la entrada
            return False

    def calcular_espesores(self, index): # 'index' no se usa, pero lo mantenemos por el lambda
        """
        Calcula el espesor de cada fila (diferencia entre la profundidad actual y la anterior),
        recorriendo todas las filas.
        """
        
        # 1. Recoger y normalizar todas las profundidades
        profundidades_normalizadas = []
        for var in self.prof_vars:
            try:
                # Intentamos obtener el valor y convertirlo a entero
                prof = int(var.get())
                profundidades_normalizadas.append(prof)
            except ValueError:
                # Si está vacío ('') o no es un dígito, guardamos None
                profundidades_normalizadas.append(None)
        
        # 2. Iterar y calcular el espesor
        profundidad_anterior = 0 # El punto de partida es 0 cm (la superficie)
        
        # Recorremos TODAS las filas para recalcular la cadena completa
        for i in range(self.num_filas):
            profundidad_actual = profundidades_normalizadas[i]
            
            espesor = 0
            
            # Solo calculamos si la profundidad actual es un número válido (no es None)
            if profundidad_actual is not None:
                # Si el valor actual es mayor o igual que la profundidad anterior (correcta)
                if profundidad_actual >= profundidad_anterior:
                    espesor = profundidad_actual - profundidad_anterior
                    # Actualizamos la profundidad anterior para el siguiente horizonte
                    profundidad_anterior = profundidad_actual
                else:
                    # Caso de valor decreciente (posible error de entrada, limpiamos el espesor)
                    espesor = 0
                    # NO actualizamos profundidad_anterior; mantenemos el valor correcto para el siguiente.
            
            # 3. Actualizar la variable de espesor (y por ende el Entrybox)
            # Aunque la variable de espesor debería ser StringVar (para manejar vacíos)
            # la definiste como IntVar. Si solo calculas números, está bien usar set(int).
            self.espesor_vars[i].set(espesor)

    def _setup_labels(self):
        """Configura las etiquetas de cabecera para los campos de color."""
        labels_data = [('Color matríz húmedo', 3, 'sandybrown'),
                       ('Color matríz seco', 7, 'olive'),
                       ('Color moteados', 17, 'mediumseagreen') # Nueva etiqueta
                       ]
        # 1. Definición de colores fijos para las etiquetas de componente
        component_color_map = {'H.': 'bisque',
                               'V.': 'lightcyan',
                               'C.': '#FFCCCC',
                               'Color': 'lavender'}
        
        # Aseguramos que la columna 0 y 1 existan para alinear bien
        #ttk.Label(self, text='Hor.', background='gray', width=6, anchor='center').grid(
         #   row=1, column=0, rowspan=2, sticky='nsew')
        
        for text, start_col, color in labels_data:
            ttk.Label(self, text=text, background=color, width=5, anchor='center').grid(
                row=1, column=start_col, columnspan=4, sticky='ew')
        
        # Etiquetas de componentes (H., V., C., Color)
        component_labels = [
            ('H.', 3), ('V.', 4), ('C.', 5), ('Color', 6), # Húmedo
            ('H.', 7), ('V.', 8), ('C.', 9), ('Color', 10), # Seco
            ('H.', 17), ('V.', 18), ('C.', 19), ('Color', 20) # Moteados
        ]
        
        for text, col in component_labels:
            # 2. Obtenemos el color de fondo usando el mapeo de componente fijo
            background_color = component_color_map.get(text, 'white') # 'white' como fallback
            ttk.Label(self,
                      text=text,
                      background=background_color, 
                      width=5 if text == 'H.' else 3 if text != 'Color' else 6, 
                      anchor='center').grid(row=2, column=col, sticky='ew')


    def _setup_color_entries(self):
        # ... (código para crear filas) ...
        for i in range(self.num_filas):
            row_index = i + 4
            # Etiqueta de Estrato (Columna 0)
            #ttk.Label(self, text=str(i + 1), background='lightgray', width=5, anchor='center').grid(
            #    row=row_index, column=0, sticky='ew')
            
            # --- Configuración para Color HÚMEDO (offset 3) ---
            self._create_munsell_entry_row(row_index, i, col_offset=3,
                                           hue_vars=self.huehum_vars, val_vars=self.valorhum_vars,
                                           chr_vars=self.chromahum_vars, matrix_vars=self.matriz_colorhum_vars
                                           )

            # --- Configuración para Color SECO (offset 7) ---
            self._create_munsell_entry_row(row_index, i, col_offset=7,
                                           hue_vars=self.hueseco_vars, val_vars=self.valorseco_vars,
                                           chr_vars=self.chromaseco_vars, matrix_vars=self.matriz_colorseco_vars
                                           )
            
            # --- Configuración para MOTEADOS (offset 17) ---
            self._create_munsell_entry_row(row_index, i, col_offset=17,
                                           hue_vars=self.huemota_vars,
                                           val_vars=self.valormota_vars,
                                           chr_vars=self.chromamota_vars,
                                           matrix_vars=self.colormota_vars
                                           )


    def _create_munsell_entry_row(self, row_index, list_index, col_offset, hue_vars, val_vars, chr_vars, matrix_vars):
        """Crea una fila de widgets de entrada Munsell (Hue, Value, Chroma, Salida)."""
        
        # 1. Inicializar StringVars y añadirlas a las listas
        hue_var = tk.StringVar(self)
        valor_var = tk.StringVar(self)
        chroma_var = tk.StringVar(self)
        matriz_color_var = tk.StringVar(self)

        hue_vars.append(hue_var)
        val_vars.append(valor_var)
        chr_vars.append(chroma_var)
        matrix_vars.append(matriz_color_var)

        # 2. Crear Entryboxes con validatecommand
        
        # --- Hue (Ahora usa un comando de validación específico: self.vcmd_hue) ---
        hue_entry = ttk.Entry(self, width=6, textvariable=hue_var,
                              validate='key', validatecommand=self.vcmd_hue)
        hue_entry.grid(row=row_index, column=col_offset)
        
        # --- Value (Ahora usa un comando de validación específico: self.vcmd_value) ---
        valor_entry = ttk.Entry(self, width=6, textvariable=valor_var,
                                validate='key', validatecommand=self.vcmd_value)
        valor_entry.grid(row=row_index, column=col_offset + 1)
        
        # --- Chroma (Ahora usa un comando de validación específico: self.vcmd_chroma) ---
        chroma_entry = ttk.Entry(self, width=6, textvariable=chroma_var,
                                 validate='key', validatecommand=self.vcmd_chroma)
        chroma_entry.grid(row=row_index, column=col_offset + 2)
        
        # --- Color Concatenado (Etiqueta de Salida) ---
        matriz_label = ttk.Label(self, textvariable=matriz_color_var, background='snow3', width=10, anchor='center')
        matriz_label.grid(row=row_index, column=col_offset + 3, sticky='ew')

        # 3. Vincular Callbacks (Para concatenación y actualización de color de fondo)
        hue_var.trace_add('write', lambda name, index, mode, v=hue_var: v.set(v.get().upper()))

        callback = self.create_update_callback(
            list_index, hue_var, valor_var, chroma_var, matriz_color_var, 
            hue_entry, valor_entry, chroma_entry
        )
        
        hue_var.trace_add('write', callback)
        valor_var.trace_add('write', callback)
        chroma_var.trace_add('write', callback)

    # =================================================================
    # NUEVOS MÉTODOS DE VALIDACIÓN ESTRICTA (ESPECÍFICOS Y ROBUSTOS)
    # =================================================================

    def _validate_munsell_part(self, new_value: str, valid_set: set) -> bool:
        """Lógica genérica para validar Hue, Value o Chroma."""
        
        # Permitir entrada si está vacío (para borrado)
        if not new_value:
            return True
        
        # 1. Chequeo de valor final válido
        if new_value in valid_set:
            return True
        
        # 2. Chequeo de prefijo válido
        if any(val.startswith(new_value) for val in valid_set):
            return True

        # Bloquear si no es válido ni prefijo
        return False


    def _validate_hue(self, new_value):
        """Valida específicamente la entrada de Hue."""
        return self._validate_munsell_part(new_value.upper(), self.VALID_HUES)

    def _validate_value(self, new_value):
        """Valida específicamente la entrada de Value (permite decimales con '.')."""
        # Reemplazar ',' por '.' internamente para la validación
        validated_value = new_value.replace(',', '.')
        return self._validate_munsell_part(validated_value, self.VALID_VALUES)

    def _validate_chroma(self, new_value):
        """Valida específicamente la entrada de Chroma."""
        return self._validate_munsell_part(new_value, self.VALID_CHROMA)
    
    # ... (Resto de métodos create_update_callback, validate_and_format_munsell, 
    # _check_munsell_part_validity, _update_entry_color se mantienen igual, 
    # solo usan los conjuntos de valores válidos de la clase) ...

    def create_update_callback(self, row_index, hue_var, valor_var, chroma_var, matriz_color_var, hue_entry, valor_entry, chroma_entry):
        # ... (código del callback, se mantiene igual) ...
        def callback(*args):
            hue_val = hue_var.get().strip()
            val_val = valor_var.get().strip()
            chr_val = chroma_var.get().strip()
            
            full_color, is_valid = self.validate_and_format_munsell(
                hue_val, val_val, chr_val, 
                hue_entry, valor_entry, chroma_entry
            )
            matriz_color_var.set(full_color)
        return callback
    
    def validate_and_format_munsell(self, hue: str, value: str, chroma: str, 
                                     hue_entry, value_entry, chroma_entry) -> tuple[str, bool]:
        all_valid = True 
        
        # --- Validar Hue y actualizar color de fondo ---
        hue_valid_status = self._check_munsell_part_validity(hue, self.VALID_HUES)
        self._update_entry_color(hue_entry, hue_valid_status)
        if hue_valid_status != 'valid': all_valid = False

        # --- Validar Value y actualizar color de fondo ---
        value_validated = value.replace(',', '.')
        value_valid_status = self._check_munsell_part_validity(value_validated, self.VALID_VALUES)
        self._update_entry_color(value_entry, value_valid_status)
        if value_valid_status != 'valid': all_valid = False

        # --- Validar Chroma y actualizar color de fondo ---
        chroma_valid_status = self._check_munsell_part_validity(chroma, self.VALID_CHROMA)
        self._update_entry_color(chroma_entry, chroma_valid_status)
        if chroma_valid_status != 'valid': all_valid = False
            
        # --- Concatenación y Retorno ---
        if all_valid:
            full_color = f"{hue}{value_validated}/{chroma}"
            return full_color, True
        
        elif hue or value or chroma:
            full_color = f"{hue}{value}/{chroma}" 
            return full_color, False

        else:
            return "", True

    def _check_munsell_part_validity(self, text: str, valid_set: set) -> str:
        """Verifica la validez de una parte (Valid, Prefix, Empty, Invalid)."""
        text = text.strip()
        if not text:
            return 'empty'
        
        if text in valid_set:
            return 'valid'
        
        if any(val.startswith(text) for val in valid_set):
            return 'prefix'
        
        return 'invalid'

    def _update_entry_color(self, entry_widget: ttk.Entry, status: str):
        # ... (código para actualizar color) ...
        if status == 'valid':
            entry_widget.config(background='#E6FFEE', foreground='black')
        elif status == 'invalid':
            entry_widget.config(background='#FFCCCC', foreground='red')
        elif status == 'prefix' or status == 'empty':
            entry_widget.config(background='white', foreground='black')
        else:
            entry_widget.config(background='white', foreground='black')

    def submit_form(self):
        # Collects data from Page 2 widgets and triggers the data saving
        # process in the main controller.

        barreno_nombre = self.barreno_var.get()
        barreno_codigo = self.barreno_option.get(barreno_nombre, 'ERROR')
        
        codigo_moteadoabund = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for moteado_var in self.moteadoabund_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            moteadoabund_nombre = moteado_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            moteadoabund_codigo = self.moteadoabund_option.get(moteadoabund_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if moteadoabund_codigo != 'ERROR':
                codigo_moteadoabund.append(moteadoabund_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Abundancia: {moteadoabund_nombre}")
                return # Detener el proceso de guardado si hay un error
            
        codigo_moteadotipo = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for moteadotipo_var in self.moteadotipo_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            moteadotipo_nombre = moteadotipo_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            moteadotipo_codigo = self.moteadotipo_option.get(moteadotipo_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if moteadotipo_codigo != 'ERROR':
                codigo_moteadotipo.append(moteadotipo_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Tipo: {moteadotipo_nombre}")
                return # Detener el proceso de guardado si hay un error

        codigo_moteadotama = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for moteadotama_var in self.moteadotama_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            moteadotama_nombre = moteadotama_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            moteadotama_codigo = self.moteadotama_option.get(moteadotama_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if moteadotama_codigo != 'ERROR':
                codigo_moteadotama.append(moteadotama_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Tamaño: {moteadotama_nombre}")
                return # Detener el proceso de guardado si hay un error            

        codigo_contraste = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for contraste_var in self.contraste_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            contraste_nombre = contraste_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            contraste_codigo = self.contraste_option.get(contraste_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if contraste_codigo != 'ERROR':
                codigo_contraste.append(contraste_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Contraste: {contraste_nombre}")
                return # Detener el proceso de guardado si hay un error            

        codigo_formot = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for formot_var in self.formot_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            formot_nombre = formot_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            formot_codigo = self.formot_option.get(formot_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if formot_codigo != 'ERROR':
                codigo_formot.append(formot_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Forma: {formot_nombre}")
                
                return # Detener el proceso de guardado si hay un error
    
        codigo_eferv = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for eferv_var in self.eferv_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            eferv_nombre = eferv_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            eferv_codigo = self.eferv_option.get(eferv_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if eferv_codigo != 'ERROR':
                codigo_eferv.append(eferv_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Efervescencia: {eferv_nombre}")
                return # Detener el proceso de guardado si hay un error

        codigo_estagua = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for estagua_var in self.estagua_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            estagua_nombre = estagua_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            estagua_codigo = self.estagua_option.get(estagua_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if estagua_codigo != 'ERROR':
                codigo_estagua.append(estagua_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Estado del agua: {eferv_nombre}")
                return # Detener el proceso de guardado si hay un error 

        codigo_plasticidad = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for plasticidad_var in self.plasticidad_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            plasticidad_nombre = plasticidad_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            plasticidad_codigo = self.plasticidad_option.get(plasticidad_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if plasticidad_codigo != 'ERROR':
                codigo_plasticidad.append(plasticidad_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Plasticidad: {plasticidad_nombre}")
                return # Detener el proceso de guardado si hay un error 

        codigo_fragtipo = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for fragtipo_var in self.fragtipo_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            fragtipo_nombre = fragtipo_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            fragtipo_codigo = self.fragtipo_option.get(fragtipo_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if fragtipo_codigo != 'ERROR':
                codigo_fragtipo.append(fragtipo_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Tipo fragmento: {plasticidad_nombre}")
                return # Detener el proceso de guardado si hay un error 

        codigo_fragvolumen = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for fragvolumen_var in self.fragvolumen_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            fragvolumen_nombre = fragvolumen_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            fragvolumen_codigo = self.fragvolumen_option.get(fragvolumen_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if fragvolumen_codigo != 'ERROR':
                codigo_fragvolumen.append(fragvolumen_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Volumen fragmento: {fragvolumen_nombre}")
                return # Detener el proceso de guardado si hay un error

        codigo_fragtama = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for fragtama_var in self.fragtama_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            fragtama_nombre = fragtama_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            fragtama_codigo = self.fragtama_option.get(fragtama_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if fragtama_codigo != 'ERROR':
                codigo_fragtama.append(fragtama_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Tamaño fragmento: {fragtama_nombre}")
                return # Detener el proceso de guardado si hay un error

        codigo_redondez = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for redondez_var in self.redondez_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            redondez_nombre = redondez_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            redondez_codigo = self.redondez_option.get(redondez_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if redondez_codigo != 'ERROR':
                codigo_redondez.append(redondez_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Redondez: {redondez_nombre}")
                return # Detener el proceso de guardado si hay un error

        codigo_esfericidad = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for esfericidad_var in self.esfericidad_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            esfericidad_nombre = esfericidad_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            esfericidad_codigo = self.esfericidad_option.get(esfericidad_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if esfericidad_codigo != 'ERROR':
                codigo_esfericidad.append(esfericidad_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Esfericidad: {esfericidad_nombre}")
                return # Detener el proceso de guardado si hay un error
            
        codigo_fragporc = []

        # 1. ITERAR sobre TODAS las variables de los Combobox (una por horizonte)
        for fragporc_var in self.fragporc_vars:
            # a. Obtener el texto seleccionado (Ej: 'poca (<2%)')
            fragporc_nombre = fragporc_var.get()
            
            # b. Buscar el código numérico asociado usando el diccionario
            fragporc_codigo = self.fragporc_option.get(fragporc_nombre, 'ERROR')
            
            # c. Si se encuentra un código válido, agrégalo a la lista
            if fragporc_codigo != 'ERROR':
                codigo_fragporc.append(fragporc_codigo)
            else:
                # Opcional: Manejar errores si un valor no se encuentra, aunque no debería pasar con 'readonly'
                messagebox.showerror("Error de datos", f"Valor no reconocido en Fragmento porcentaj: {fragporc_nombre}")
                
        #estacion_nombre = self.controller.estacion_var.get()
        #estacion_codigo = self.controller.estacion_option.get(estacion_nombre, 'ERROR')
            
        data = {'idestudio': self.controller.proyecto_var.get(),
                'codestacion': self.controller.estacion_codigo_var,
                'idpunto': self.controller.IDpunto_var.get(),
                'estrato': self.estrato_vars,
                'codtextacto': [var.get() for var in self.textacto_vars],
                'codestado_agua': codigo_estagua,
                'codtex_visual': '',
                'color_hum.': [var.get() for var in self.matriz_colorhum_vars],
                'color_seco': [var.get() for var in self.matriz_colorseco_vars],
                'codtex_lab.': [var.get() for var in self.texlab_vars],
                'codreaccion_ph': '',
                'codsalinidad': '',
                'codadherencia': '',
                'codplasticidad': codigo_plasticidad,
                'coddifc_excavacion':'',
                'codtopografia':'',
                'codefervescencia': codigo_eferv,
                'codorientacion_penetracion': '',
                'codpenetracion': '',
                'codpermeabilidad': '',
                'codkpa_agua': '',
                'codporc_fragm': codigo_fragporc,
                'codlimite': '',          
                'codmuestreador': barreno_codigo,
                'codburbujeo': '',
                'descripcion_detallada': '',
                
                'prof_alcanzable_m': self.prof_alc_m_var.get(),
                'nmuestraalt.': [var.get() for var in self.muestraalt_vars],
                'nmuestrainalt.': [var.get() for var in self.muestranoalt_vars],
                
                #'prof_inicial_cm': AÑADIR ################,
                'prof_final_cm': [var.get() for var in self.prof_vars],
                'espesor_cm': [var.get() for var in self.espesor_vars],
                'designacion': [var.get() for var in self.horizonte_vars],
                'humedad_porct': [var.get() for var in self.humedad_vars],
                'mo_porcentaje': '',
                'artfc_volumen': '',
                
                #'pesofrag10g_suelo': AÑADIR ##########,
                #'muestreador_long_m': AÑADIR ##########,
                #'muestreado_diam_ancho_m': AÑADIR ##########,
                'ph': '',
                'arena_visual': '', # [var.get() for var in self.arenavis_vars],
                'limo_visual': '', #  [var.get() for var in self.limovis_vars],
                'arcilla_visual': '', # [var.get() for var in self.arcillavis_vars],
                'arena_lab': '', #  [var.get() for var in self.arenalab_vars],
                'limo_lab': '', #  [var.get() for var in self.limolab_vars],
                'arcilla_lab': '', #  [var.get() for var in self.arcillalab_vars],
                #'frag_tamanno_mm': AÑADIR ###########
                'Observaciones': [var.get() for var in self.observaciones_vars], 
                
                'Hue hum.': [var.get() for var in self.huehum_vars],
                'Value hum.': [var.get() for var in self.valorhum_vars],
                'Croma hum.': [var.get() for var in self.chromahum_vars],

                'Hue seco': [var.get() for var in self.hueseco_vars],
                'Value seco': [var.get() for var in self.valorseco_vars],
                'Croma seco': [var.get() for var in self.chromaseco_vars],        

                'codmoteado_tipo': codigo_moteadotipo,
                'codmoteado_abund': codigo_moteadoabund,
                'codmoteado_tamanno': codigo_moteadotama,
                'codmoteado_contrst': codigo_contraste,
                'codmoteado_forma': codigo_formot,
                
                'Huemot': [var.get() for var in self.huemota_vars],
                'Valuemot': [var.get() for var in self.valormota_vars],
                'Cromamot': [var.get() for var in self.chromamota_vars],
                'color_moteado': [var.get() for var in self.colormota_vars],

                'codfrag_tipo': codigo_fragtipo,
                'codfragvolume': codigo_fragvolumen,
                'tipofragtamanno': codigo_fragtama,
                'codfrag_redondez': codigo_redondez,
                'codfrag_esfericidad': codigo_esfericidad,       
                }
        
        self.controller.update_form_data('PageTwo', data)
        self.controller.save_all_data_and_reset()

    def reset_variables(self):
        """
        Resets the StringVars on this page to clear the form fields.
        """
        self.prof_alc_m_var.set(value = 0)

        [var.set('') for var in self.textacto_vars]
        [var.set(self.estagua_choices[0]) for var in self.estagua_vars]
        #[var.set('') for var in self.texvis_vars]
        [var.set('') for var in self.texlab_vars]
        
        [var.set(self.fragporc_choices[0]) for var in self.fragporc_vars]

        barreno_choices = list(self.barreno_option.keys())
        self.barreno_var.set(barreno_choices[0] if barreno_choices else '')  
 
        [var.set(0) for var in self.prof_vars]
        [var.set(0) for var in self.espesor_vars]
        
        [var.set('') for var in self.huehum_vars]
        [var.set('') for var in self.valorhum_vars]
        [var.set('') for var in self.chromahum_vars]

        [var.set('') for var in self.hueseco_vars]
        [var.set('') for var in self.valorseco_vars]
        [var.set('') for var in self.chromaseco_vars]   

        [var.set('') for var in self.horizonte_vars]

        [var.set(self.moteadotipo_choices[0]) for var in self.moteadotipo_vars]
        [var.set(self.moteadoabund_choices[0]) for var in self.moteadoabund_vars]
        [var.set(self.moteadotama_choices[0]) for var in self.moteadotama_vars]
        [var.set(self.contraste_choices[0]) for var in self.contraste_vars]   
        [var.set(self.formot_choices[0]) for var in self.formot_vars]
        
        [var.set('') for var in self.huemota_vars]
        [var.set('') for var in self.valormota_vars]
        [var.set('') for var in self.chromamota_vars]
        [var.set('') for var in self.colormota_vars]        

        [var.set(self.eferv_choices[0]) for var in self.eferv_vars]

        [var.set(self.plasticidad_choices[0]) for var in self.plasticidad_vars]

        [var.set(self.fragtipo_choices[0]) for var in self.fragtipo_vars]
        [var.set(self.fragvolumen_choices[0]) for var in self.fragvolumen_vars]
        [var.set(self.fragtama_choices[0]) for var in self.fragtama_vars]
        [var.set(self.redondez_choices[0]) for var in self.redondez_vars]
        [var.set(self.esfericidad_choices[0]) for var in self.esfericidad_vars]
        
        #[var.set(0) for var in self.arenavis_vars]
        #[var.set(0) for var in self.limovis_vars]
        #[var.set(0) for var in self.arcillavis_vars]
        
        [var.set(0) for var in self.arenalab_vars]
        [var.set(0) for var in self.limolab_vars]
        [var.set(0) for var in self.arcillalab_vars]        

        [var.set(0) for var in self.humedad_vars]  

        [var.set('') for var in self.muestraalt_vars] 
        [var.set('') for var in self.muestranoalt_vars]        
        [var.set('') for var in self.observaciones_vars] 
        
if __name__ == '__main__':
    app = FormsApp()
    app.mainloop()
    
