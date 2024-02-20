# Written by Kresten Faarup Marcussen
# Licenced under MIT

import json
import tkinter as tk
import ttkbootstrap as ttk
import geopandas as gpd
import requests
#import pyi_splash
from pathlib import Path
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.style import Bootstyle

gpd.options.io_engine = "pyogrio"

def convert_to_geojson(input_data):
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    for item in input_data:
        byg404Koordinat = item.get("byg404Koordinat")
        if byg404Koordinat is None:
            # Skip items with missing coordinates
            continue

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": byg404Koordinat.replace("POINT(", "").replace(")", "").split()
            },
            "properties": {}
        }

        for key, value in item.items():
            if key in ["etageList", "opgangList", "bygningPåFremmedGrundList", "fordelingsarealList"]:
                # Flatten nested lists if present
                for i in range(len(value)):
                    nested_item = value[i].get(key[:-4], {})  # Remove "List" from key name
                    for nested_key, nested_value in nested_item.items():
                        feature["properties"][f"{key[:-4]}_{i + 1}_{nested_key}"] = nested_value
            elif key != "byg404Koordinat":
                feature["properties"][key] = value

        geojson_data["features"].append(feature)

    return geojson_data


def convert_to_geopackage(input_geojson, output_file):
    gdf = gpd.GeoDataFrame.from_features(input_geojson["features"])

    # Define spatial reference
    crs = {'init': 'epsg:7416'}  # EPSG:7416

    # Set spatial reference for GeoDataFrame
    gdf.crs = crs

    # Save GeoDataFrame to GeoPackage
    gdf.to_file(output_file, driver="GPKG", encoding='utf-8')

def convert_local():
    input_file = input_entry.get()
    output_file = output_entry.get()

    if not input_file:
        messagebox.showerror("Error", "Vælg venligst en input fil.")
        return

    try:
        with open(input_file, "r", encoding='utf-8') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "Ingen Input fil fundet.")
        return
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format i input fil.")
        return

    geojson_output = convert_to_geojson(input_data)

    try:
        convert_to_geopackage(geojson_output, output_file)
        messagebox.showinfo("Success", "Konvertering til GeoPackage fuldført.")
    except Exception as e:
        messagebox.showerror("Fejl", f"En fejl er opstået: {str(e)}")
        
import requests

def rest_call(payload):
    try:
        headers = {
            'accept': 'application/json',
            'accept-charset': 'utf-8'
        }
        response = requests.get('https://services.datafordeler.dk/BBR/BBRPublic/1/rest/bygning', params=payload, headers=headers)
        response.raise_for_status()
        response.encoding = 'UTF-8'
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during REST API call: {e}")
        return None


def remove_empty_values(payload):
    return {k: v for k, v in payload.items() if v}

def convert_rest():
    payload = {
        'username': username_entry_rest.get(),
        'password': password_entry_rest.get(),
        'kommunekode': selected_Komkode,
        'BFENummer': BFENummer_entry_rest.get(),
        'MedDybde': MedDybde_check_Tell,
        'pagesize': pagesize_entry_rest.get(),
        'page': page_entry_rest.get(),
        'Id': id_entry_rest.get(),
        'VirkningFra': VirkningFra_date_rest.get(),
        'VirkningTil': VirkningTil_date_rest.get(),
        'Virkningsaktoer': Virkningsaktoer_entry_rest.get(),
        'RegistreringFra': RegistreringFra_date_rest.get(),
        'RegistreringTil': RegistreringTil_date_rest.get(),
        'Registreringsaktoer': Registreringsaktoer_entry_rest.get(),
        'Status': Status_entry_rest.get(),
        'Forretningsproces': Forretningsproces_entry_rest.get(),
        'Forretningsomraade': Forretningsomraade_entry_rest.get(),
        'Forretningshaendelse': Forretningshaendelse_entry_rest.get(),
        'DAFTimestampFra': DAFTimestampFra_date_rest.get(),
        'DAFTimestampTil': DAFTimestampTil_date_rest.get(),
        'Etage': Etage_entry_rest.get(),
        'Fordelingsareal': Fordelingsareal_entry_rest.get(),
        'Opgang': Opgang_entry_rest.get(),
        'TekniskAnlaeg': TekniskAnlaeg_entry_rest.get(),
        'Grund': Grund_entry_rest.get(),
        'Jordstykke': Jordstykke_entry_rest.get(),
        'Ejendomsrelation': Ejendomsrelation_entry_rest.get(),
        'Husnummer': Husnummer_entry_rest.get(),
        'Nord': Nord_entry_rest.get(),
        'Syd': Opgang_entry_rest.get(),
        'Oest': Oest_entry_rest.get(),
        'Vest': Vest_entry_rest.get(),
        'PeriodeaendringFra': PeriodeaendringFra_date_rest.get(),
        'PeriodeaendringTil': PeriodeaendringTil_date_rest.get(),
        'KunNyesteIPeriode': KunNyesteIPeriode_check_Tell,
        'format': 'json',
    }

    payload = remove_empty_values(payload)

    input_data = rest_call(payload)
    if input_data:
        geojson_output = convert_to_geojson(input_data)
        try:
            convert_to_geopackage(geojson_output, output_entry_rest.get())
            messagebox.showinfo("Success", "Konvertering til GeoPackage fuldført.")
        except Exception as e:
            messagebox.showerror("Fejl", f"En fejl er opstået: {str(e)}")

# Create GUI
#pyi_splash.close()

IMG_PATH = Path(__file__).parent / 'Resources'

root = ttk.Window(themename="litera",iconphoto='bbr2gp.png')
root.title("JSON to GeoPackage Converter")

#Collapsing Frame




class CollapsingFrame(ttk.Frame):
    """A collapsible frame widget that opens and closes with a click."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.cumulative_rows = 0

        # widget images
        self.images = [
            ttk.PhotoImage(file=IMG_PATH/'icons8-slide-up-26.png'),
            ttk.PhotoImage(file=IMG_PATH/'icons8-next-page-26.png')
        ]
        
        # page icons by https://icons8.com Icons8
        

    def add(self, child, title="", bootstyle=PRIMARY, is_collapsed=False, **kwargs):
        """Add a child to the collapsible frame

        Parameters:

            child (Frame):
                The child frame to add to the widget.

            title (str):
                The title appearing on the collapsible section header.

            bootstyle (str):
                The style to apply to the collapsible section header.

            **kwargs (Dict):
                Other optional keyword arguments.
        """
        if child.winfo_class() != 'TFrame':
            return

        style_color = Bootstyle.ttkstyle_widget_color(bootstyle)
        frm = ttk.Frame(self, bootstyle=style_color)
        frm.grid(row=self.cumulative_rows, column=0, sticky=EW)

        # header title
        header = ttk.Label(
            master=frm,
            text=title,
            bootstyle=(style_color, INVERSE)
        )
        if kwargs.get('textvariable'):
            header.configure(textvariable=kwargs.get('textvariable'))
        header.pack(side=LEFT, fill=BOTH, padx=10)

        # header toggle button
        def _func(c=child): return self._toggle_open_close(c)
        btn = ttk.Button(
            master=frm,
            image=self.images[0],
            bootstyle=style_color,
            command=_func
        )
        btn.pack(side=RIGHT)

        # assign toggle button to child so that it can be toggled
        child.btn = btn
        child.grid(row=self.cumulative_rows + 1, column=0, sticky=NSEW)

        # increment the row assignment
        self.cumulative_rows += 2
        
        if is_collapsed:
            child.grid_remove()
            child.btn.configure(image=self.images[1])
        else:
            child.grid()
            child.btn.configure(image=self.images[0])

    def _toggle_open_close(self, child):
        """Open or close the section and change the toggle button 
        image accordingly.

        Parameters:

            child (Frame):
                The child element to add or remove from grid manager.
        """
        if child.winfo_viewable():
            child.grid_remove()
            child.btn.configure(image=self.images[1])
        else:
            child.grid()
            child.btn.configure(image=self.images[0])

class CollapsingFrame2(ttk.Frame):
    """A collapsible frame widget that opens and closes with a click."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.cumulative_rows = 0
        

    def add(self, child, title="", bootstyle=PRIMARY, **kwargs):
        """Add a child to the collapsible frame

        Parameters:

            child (Frame):
                The child frame to add to the widget.

            title (str):
                The title appearing on the collapsible section header.

            bootstyle (str):
                The style to apply to the collapsible section header.

            **kwargs (Dict):
                Other optional keyword arguments.
        """
        if child.winfo_class() != 'TFrame':
            return

        style_color = Bootstyle.ttkstyle_widget_color(bootstyle)
        frm = ttk.Frame(self, bootstyle=style_color)
        frm.grid(row=self.cumulative_rows, column=0, sticky=EW)

        # header title
        header = ttk.Label(
            master=frm,
            text=title,
            bootstyle=(style_color, INVERSE)
        )
        if kwargs.get('textvariable'):
            header.configure(textvariable=kwargs.get('textvariable'))
        header.pack(side=LEFT, fill=BOTH, padx=10)

        # header toggle button
        def _func(c=child): return self._toggle_open_close(c)
        btn = ttk.Button(
            master=frm,
            bootstyle=style_color,
            command=_func
        )
        btn.pack(side=RIGHT)

        # assign toggle button to child so that it can be toggled
        child.btn = btn
        child.grid(row=self.cumulative_rows + 1, column=0, sticky=NSEW)

        # increment the row assignment
        self.cumulative_rows += 2

    def _toggle_open_close(self, child):
        """Open or close the section and change the toggle button 
        image accordingly.

        Parameters:

            child (Frame):
                The child element to add or remove from grid manager.
        """
        if child.winfo_viewable():
            child.grid_remove()
        else:
            child.grid()
# Tabs

tab_control = ttk.Notebook(root)
tab_local = ttk.Frame(tab_control)
tab_rest = ScrolledFrame(tab_control, autohide=True, bootstyle="SECONDARY-round", height=525, width=400)

tab_control.add(tab_local, text='Lokal fil konvertering')
tab_control.add(tab_rest.container, text='REST konvertering')
tab_control.pack(expand=1, fill="both")


# Tab Lokal konventering

cf1 = CollapsingFrame2(tab_local)
cf1.pack(fill=BOTH)

group0 = ttk.Frame(cf1, padding=10)
cf1.add(child=group0, title='Lokal konventering', bootstyle=SECONDARY)

# Lokal konventering

input_label = ttk.Label(group0, text="Input JSON fil:")
input_label.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.W)
input_entry = ttk.Entry(group0, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
input_button = ttk.Button(group0, text="Vælg", command=lambda: input_entry.insert(tk.END, filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])))
input_button.grid(row=0, column=2, padx=5, pady=5)

output_label = ttk.Label(group0, text="Output GeoPackage fil:")
output_label.grid(row=1, column=0, padx=5, pady=5, sticky=ttk.W)
output_entry = ttk.Entry(group0, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
output_button = ttk.Button(group0, text="Vælg", command=lambda: output_entry.insert(tk.END, filedialog.asksaveasfilename(defaultextension=".gpkg", filetypes=[("GeoPackage files", "*.gpkg")])))
output_button.grid(row=1, column=2, padx=5, pady=5)

convert_button_local = ttk.Button(group0, text="Konverter", command=convert_local)
convert_button_local.grid(row=2, column=1, padx=5, pady=5)


# Tab Rest konventering

cf2 = CollapsingFrame(tab_rest)
cf2.pack(fill=BOTH)

cf3 = CollapsingFrame2(tab_rest)
cf3.pack(fill=BOTH)


# Tjenestebruger
group2 = ttk.Frame(cf2, padding=10)
cf2.add(child=group2, title='Tjenestebruger', bootstyle=PRIMARY)

username_label_rest = ttk.Label(group2, text="Brugernavn:")
username_label_rest.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
username_entry_rest = ttk.Entry(group2, width=30)
username_entry_rest.grid(row=0, column=1, padx=5, pady=5)

password_label_rest = ttk.Label(group2, text="Adgangskode:")
password_label_rest.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
password_entry_rest = ttk.Entry(group2, width=30, show='•')
password_entry_rest.grid(row=1, column=1, padx=5, pady=5)

# Grundlæggende parametere
group3 = ttk.Frame(cf2, padding=10)
cf2.add(group3, title='Grundlæggende Parametre', bootstyle=PRIMARY)

Kommunedata = [
    "0101: København",
    "0147: Frederiksberg",
    "0151: Ballerup",
    "0153: Brøndby",
    "0155: Dragør",
    "0157: Gentofte",
    "0159: Gladsaxe",
    "0161: Glostrup",
    "0163: Herlev",
    "0165: Albertslund",
    "0167: Hvidovre",
    "0169: Høje-Taastrup",
    "0173: Lyngby-Taarbæk",
    "0175: Rødovre",
    "0183: Ishøj",
    "0185: Tårnby",
    "0187: Vallensbæk",
    "0190: Furesø",
    "0201: Allerød",
    "0210: Fredensborg",
    "0217: Helsingør",
    "0219: Hillerød",
    "0223: Hørsholm",
    "0230: Rudersdal",
    "0240: Egedal",
    "0250: Frederikssund",
    "0253: Greve",
    "0259: Køge",
    "0260: Halsnæs",
    "0265: Roskilde",
    "0269: Solrød",
    "0270: Gribskov",
    "0306: Odsherred",
    "0316: Holbæk",
    "0320: Faxe",
    "0326: Kalundborg",
    "0329: Ringsted",
    "0330: Slagelse",
    "0336: Stevns",
    "0340: Sorø",
    "0350: Lejre",
    "0360: Lolland",
    "0370: Næstved",
    "0376: Guldborgsund",
    "0390: Vordingborg",
    "0400: Bornholm",
    "0410: Middelfart",
    "0411: Christiansø",
    "0420: Assens",
    "0430: Faaborg-Midtfyn",
    "0440: Kerteminde",
    "0450: Nyborg",
    "0461: Odense",
    "0479: Svendborg",
    "0480: Nordfyns",
    "0482: Langeland",
    "0492: Ærø",
    "0510: Haderslev",
    "0530: Billund",
    "0540: Sønderborg",
    "0550: Tønder",
    "0561: Esbjerg",
    "0563: Fanø",
    "0573: Varde",
    "0575: Vejen",
    "0580: Aabenraa",
    "0607: Fredericia",
    "0615: Horsens",
    "0621: Kolding",
    "0630: Vejle",
    "0657: Herning",
    "0661: Holstebro",
    "0665: Lemvig",
    "0671: Struer",
    "0706: Syddjurs",
    "0707: Norddjurs",
    "0710: Favrskov",
    "0727: Odder",
    "0730: Randers",
    "0740: Silkeborg",
    "0741: Samsø",
    "0746: Skanderborg",
    "0751: Aarhus",
    "0756: Ikast-Brande",
    "0760: Ringkøbing-Skjern",
    "0766: Hedensted",
    "0773: Morsø",
    "0779: Skive",
    "0787: Thisted",
    "0791: Viborg",
    "0810: Brønderslev",
    "0813: Frederikshavn",
    "0820: Vesthimmerlands",
    "0825: Læsø",
    "0840: Rebild",
    "0846: Mariagerfjord",
    "0849: Jammerbugt",
    "0851: Aalborg",
    "0860: Hjørring",
    ": ",
]

value_to_code = {item.split(": ")[1]: item.split(": ")[0] for item in Kommunedata}

def on_select(event):
    global selected_Komkode
    selected_Kommune = kommunekode_entry_rest.get()
    selected_Komkode = value_to_code[selected_Kommune]
    print("Selected Value:", selected_Kommune)
    print("Corresponding Code:", selected_Komkode)

kommunekode_label_rest = ttk.Label(group3, text="Kommunekode:")
kommunekode_label_rest.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
kommunekode_entry_rest = ttk.Combobox(group3, values=[item.split(": ")[1] for item in Kommunedata], width=30)
kommunekode_entry_rest.bind("<<ComboboxSelected>>", on_select)
kommunekode_entry_rest.grid(row=0, column=1, padx=5, pady=5)

BFENummer_label_rest = ttk.Label(group3, text="BFE Nummer:")
BFENummer_label_rest.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
BFENummer_entry_rest = ttk.Entry(group3, width=30)
BFENummer_entry_rest.grid(row=1, column=1, padx=5, pady=5)

def MedDybdeFunc():
    global MedDybde_check_Tell  # Declare new_variable as global to access it outside the function
    if MedDybde_var.get() == 1:
        MedDybde_check_Tell = "True"
    else:
        MedDybde_check_Tell = "False"

MedDybde_var = tk.IntVar()
MedDybde_label_rest = ttk.Label(group3, text="Medtag Nested elementer (Etage, Opgang m.m.):")
MedDybde_label_rest.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
MedDybde_check_rest = ttk.Checkbutton(group3, bootstyle="PRIMARY-round-toggle", variable=MedDybde_var, onvalue=1, offvalue=0,command=MedDybdeFunc)
MedDybde_check_rest.grid(row=2, column=1, padx=5, pady=5)
MedDybde_check_rest.invoke()
MedDybde_check_rest.invoke()

# Advancerede parametre
group4 = ttk.Frame(cf2, padding=10)
cf2.add(group4, title='Advancerede Parametre', bootstyle=PRIMARY, is_collapsed=True)
ToolTip(group4,"Ændre kun i disse instillinger hvis du ved hvad du laver", bootstyle="PRIMARY-INVERSE")

pagesize_label_rest = ttk.Label(group4, text="Maks data per side:")
pagesize_label_rest.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
pagesize_entry_rest = ttk.Entry(group4, width=30)
pagesize_entry_rest.grid(row=0, column=1, padx=5, pady=5)
pagesize_entry_rest.insert(0, '100000')
ToolTip(pagesize_label_rest,"Maks systemet kan håndtere er 100.000, for størrere kommuner anvend sider.", bootstyle="PRIMARY-INVERSE")

page_label_rest = ttk.Label(group4, text="Side:")
page_label_rest.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
page_entry_rest = ttk.Entry(group4, width=30)
page_entry_rest.grid(row=1, column=1, padx=5, pady=5)
page_entry_rest.insert(0, '1')

id_label_rest = ttk.Label(group4, text="ID:")
id_label_rest.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
id_entry_rest = ttk.Entry(group4, width=30)
id_entry_rest.grid(row=2, column=1, padx=5, pady=5)

VirkningFra_label_rest = ttk.Label(group4, text="Virkning fra:")
VirkningFra_label_rest.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
VirkningFra_date_rest = ttk.Entry(group4, width=30)
VirkningFra_date_rest.grid(row=3, column=1, padx=5, pady=5)

VirkningTil_label_rest = ttk.Label(group4, text="Virkning til:")
VirkningTil_label_rest.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
VirkningTil_date_rest = ttk.Entry(group4, width=30)
VirkningTil_date_rest.grid(row=4, column=1, padx=5, pady=5)

Virkningsaktoer_label_rest = ttk.Label(group4, text="Virknings aktør:")
Virkningsaktoer_label_rest.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
Virkningsaktoer_entry_rest = ttk.Entry(group4, width=30)
Virkningsaktoer_entry_rest.grid(row=5, column=1, padx=5, pady=5)

RegistreringFra_label_rest = ttk.Label(group4, text="Registrering fra:")
RegistreringFra_label_rest.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
RegistreringFra_date_rest = ttk.Entry(group4, width=30)
RegistreringFra_date_rest.grid(row=6, column=1, padx=5, pady=5)

RegistreringTil_label_rest = ttk.Label(group4, text="Registrering til:")
RegistreringTil_label_rest.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
RegistreringTil_date_rest = ttk.Entry(group4, width=30)
RegistreringTil_date_rest.grid(row=7, column=1, padx=5, pady=5)

Registreringsaktoer_label_rest = ttk.Label(group4, text="Registrerings aktør:")
Registreringsaktoer_label_rest.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
Registreringsaktoer_entry_rest = ttk.Entry(group4, width=30)
Registreringsaktoer_entry_rest.grid(row=8, column=1, padx=5, pady=5)

Status_label_rest = ttk.Label(group4, text="Bygningsstatus:")
Status_label_rest.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)
Status_entry_rest = ttk.Entry(group4, width=30)
Status_entry_rest.grid(row=9, column=1, padx=5, pady=5)

Forretningsproces_label_rest = ttk.Label(group4, text="Forretningsproces:")
Forretningsproces_label_rest.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)
Forretningsproces_entry_rest = ttk.Entry(group4, width=30)
Forretningsproces_entry_rest.grid(row=10, column=1, padx=5, pady=5)

Forretningsomraade_label_rest = ttk.Label(group4, text="Forretningsområde:")
Forretningsomraade_label_rest.grid(row=11, column=0, padx=5, pady=5, sticky=tk.W)
Forretningsomraade_entry_rest = ttk.Entry(group4, width=30)
Forretningsomraade_entry_rest.grid(row=11, column=1, padx=5, pady=5)

Forretningshaendelse_label_rest = ttk.Label(group4, text="Forretningshændelse:")
Forretningshaendelse_label_rest.grid(row=12, column=0, padx=5, pady=5, sticky=tk.W)
Forretningshaendelse_entry_rest = ttk.Entry(group4, width=30)
Forretningshaendelse_entry_rest.grid(row=12, column=1, padx=5, pady=5)

DAFTimestampFra_label_rest = ttk.Label(group4, text="Datafordeler opdateringstidspunkt til:")
DAFTimestampFra_label_rest.grid(row=13, column=0, padx=5, pady=5, sticky=tk.W)
DAFTimestampFra_date_rest = ttk.Entry(group4, width=30)
DAFTimestampFra_date_rest.grid(row=13, column=1, padx=5, pady=5)

DAFTimestampTil_label_rest = ttk.Label(group4, text="Datafordeler opdateringstidspunkt fil:")
DAFTimestampTil_label_rest.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)
DAFTimestampTil_date_rest = ttk.Entry(group4, width=30)
DAFTimestampTil_date_rest.grid(row=14, column=1, padx=5, pady=5)

Etage_label_rest = ttk.Label(group4, text="BBR Etage ID:")
Etage_label_rest.grid(row=15, column=0, padx=5, pady=5, sticky=tk.W)
Etage_entry_rest = ttk.Entry(group4, width=30)
Etage_entry_rest.grid(row=15, column=1, padx=5, pady=5)

Fordelingsareal_label_rest = ttk.Label(group4, text="BBR Fordelingsareal ID:")
Fordelingsareal_label_rest.grid(row=16, column=0, padx=5, pady=5, sticky=tk.W)
Fordelingsareal_entry_rest = ttk.Entry(group4, width=30)
Fordelingsareal_entry_rest.grid(row=16, column=1, padx=5, pady=5)

Opgang_label_rest = ttk.Label(group4, text="BBR Opgang ID:")
Opgang_label_rest.grid(row=17, column=0, padx=5, pady=5, sticky=tk.W)
Opgang_entry_rest = ttk.Entry(group4, width=30)
Opgang_entry_rest.grid(row=17, column=1, padx=5, pady=5)

TekniskAnlaeg_label_rest = ttk.Label(group4, text="BBR Teknisk Anlæg ID:")
TekniskAnlaeg_label_rest.grid(row=18, column=0, padx=5, pady=5, sticky=tk.W)
TekniskAnlaeg_entry_rest = ttk.Entry(group4, width=30)
TekniskAnlaeg_entry_rest.grid(row=18, column=1, padx=5, pady=5)

Grund_label_rest = ttk.Label(group4, text="BBR Grund ID:")
Grund_label_rest.grid(row=19, column=0, padx=5, pady=5, sticky=tk.W)
Grund_entry_rest = ttk.Entry(group4, width=30)
Grund_entry_rest.grid(row=19, column=1, padx=5, pady=5)

Jordstykke_label_rest = ttk.Label(group4, text="BBR Jordstykke ID:")
Jordstykke_label_rest.grid(row=20, column=0, padx=5, pady=5, sticky=tk.W)
Jordstykke_entry_rest = ttk.Entry(group4, width=30)
Jordstykke_entry_rest.grid(row=20, column=1, padx=5, pady=5)

Ejendomsrelation_label_rest = ttk.Label(group4, text="BBR Ejendomsrelation ID:")
Ejendomsrelation_label_rest.grid(row=21, column=0, padx=5, pady=5, sticky=tk.W)
Ejendomsrelation_entry_rest = ttk.Entry(group4, width=30)
Ejendomsrelation_entry_rest.grid(row=21, column=1, padx=5, pady=5)

Husnummer_label_rest = ttk.Label(group4, text="DAR Husnummer ID:")
Husnummer_label_rest.grid(row=22, column=0, padx=5, pady=5, sticky=tk.W)
Husnummer_entry_rest = ttk.Entry(group4, width=30)
Husnummer_entry_rest.grid(row=22, column=1, padx=5, pady=5)

Nord_label_rest = ttk.Label(group4, text="Nordlig koordinat afgrænsning:")
Nord_label_rest.grid(row=23, column=0, padx=5, pady=5, sticky=tk.W)
Nord_entry_rest = ttk.Entry(group4, width=30)
Nord_entry_rest.grid(row=23, column=1, padx=5, pady=5)

Syd_label_rest = ttk.Label(group4, text="Sydlig koordinat afgrænsning:")
Syd_label_rest.grid(row=24, column=0, padx=5, pady=5, sticky=tk.W)
Syd_entry_rest = ttk.Entry(group4, width=30)
Syd_entry_rest.grid(row=24, column=1, padx=5, pady=5)

Oest_label_rest = ttk.Label(group4, text="Østlig koordinat afgrænsning:")
Oest_label_rest.grid(row=25, column=0, padx=5, pady=5, sticky=tk.W)
Oest_entry_rest = ttk.Entry(group4, width=30)
Oest_entry_rest.grid(row=25, column=1, padx=5, pady=5)

Vest_label_rest = ttk.Label(group4, text="Vestlig koordinat afgrænsning:")
Vest_label_rest.grid(row=26, column=0, padx=5, pady=5, sticky=tk.W)
Vest_entry_rest = ttk.Entry(group4, width=30)
Vest_entry_rest.grid(row=26, column=1, padx=5, pady=5)

PeriodeaendringFra_label_rest = ttk.Label(group4, text="Periodeændring fra:")
PeriodeaendringFra_label_rest.grid(row=27, column=0, padx=5, pady=5, sticky=tk.W)
PeriodeaendringFra_date_rest = ttk.Entry(group4, width=30)
PeriodeaendringFra_date_rest.grid(row=27, column=1, padx=5, pady=5)

PeriodeaendringTil_label_rest = ttk.Label(group4, text="Periodeændring Til:")
PeriodeaendringTil_label_rest.grid(row=28, column=0, padx=5, pady=5, sticky=tk.W)
PeriodeaendringTil_date_rest = ttk.Entry(group4, width=30)
PeriodeaendringTil_date_rest.grid(row=28, column=1, padx=5, pady=5)

def KunNyesteIPeriodeFunc():
    global KunNyesteIPeriode_check_Tell
    if KunNyesteIPeriode_var.get() == 1:
        KunNyesteIPeriode_check_Tell = "True"
    else:
        KunNyesteIPeriode_check_Tell = "False"

KunNyesteIPeriode_var = tk.IntVar()

KunNyesteIPeriode_label_rest = ttk.Label(group4, text="Kun nyeste version af dataobjekterne:")
KunNyesteIPeriode_label_rest.grid(row=29, column=0, padx=5, pady=5, sticky=tk.W)
KunNyesteIPeriode_check_rest = ttk.Checkbutton(group4, bootstyle="PRIMARY-round-toggle", variable=KunNyesteIPeriode_var, onvalue=1, offvalue=0,command=KunNyesteIPeriodeFunc)
KunNyesteIPeriode_check_rest.grid(row=29, column=1, padx=5, pady=5)
KunNyesteIPeriode_check_rest.invoke()
KunNyesteIPeriode_check_rest.invoke()
ToolTip(KunNyesteIPeriode_label_rest,"Kun relevant i forbindelse med brug af Periodeændring", bootstyle="PRIMARY-INVERSE")

#Konventering

group5 = ttk.Frame(cf3, padding=10)
cf3.add(group5, title='Konventering', bootstyle=LIGHT)

output_label_rest = ttk.Label(group5, text="Output GeoPackage fil:")
output_label_rest.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.W)
output_entry_rest = ttk.Entry(group5, width=50)
output_entry_rest.grid(row=0, column=1, padx=5, pady=5)
output_button_rest = ttk.Button(group5, text="Vælg", command=lambda: output_entry_rest.insert(tk.END, filedialog.asksaveasfilename(defaultextension=".gpkg", filetypes=[("GeoPackage files", "*.gpkg")])))
output_button_rest.grid(row=0, column=2, padx=5, pady=5)

convert_button_rest = ttk.Button(group5, text="Konverter", command=convert_rest)
convert_button_rest.grid(row=1, column=1, padx=5, pady=5)
ToolTip(convert_button_rest,"Programmet vil fryse, afvent konventering", bootstyle="PRIMARY-INVERSE")

root.mainloop()
