import json
import tkinter as tk
from tkinter import filedialog, messagebox
import geopandas as gpd

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
            if key == "etageList":
                # Flatten etage data
                for i, etage in enumerate(value):
                    for etage_key, etage_value in etage["etage"].items():
                        feature["properties"][f"etage_{i + 1}_{etage_key}"] = etage_value
            elif key == "opgangList":
                # Flatten opgang data
                for i, opgang in enumerate(value):
                    for opgang_key, opgang_value in opgang["opgang"].items():
                        feature["properties"][f"opgang_{i + 1}_{opgang_key}"] = opgang_value
            elif key == "bygningPåFremmedGrundList":
                # Flatten bygningPåFremmedGrund data
                for i, bygningPåFremmedGrund in enumerate(value):
                    for bygningPåFremmedGrund_key, bygningPåFremmedGrund_value in bygningPåFremmedGrund["bygningPåFremmedGrund"].items():
                        feature["properties"][f"bygningPåFremmedGrund_{i + 1}_{bygningPåFremmedGrund_key}"] = bygningPåFremmedGrund_value
            elif key == "fordelingsarealList":
                # Flatten fordelingsareal data
                for i, fordelingsareal in enumerate(value):
                    for fordelingsareal_key, fordelingsareal_value in fordelingsareal["fordelingsareal"].items():
                        feature["properties"][f"fordelingsareal_{i + 1}_{fordelingsareal_key}"] = fordelingsareal_value
            elif key != "byg404Koordinat":
                feature["properties"][key] = value

        geojson_data["features"].append(feature)

    return geojson_data

def convert_to_geopackage(input_geojson, output_file):
    gdf = gpd.GeoDataFrame.from_features(input_geojson["features"])
    gdf.to_file(output_file, driver="GPKG", encoding='utf-8')  # Ensure proper encoding

def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".gpkg", filetypes=[("GeoPackage files", "*.gpkg")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)

def convert():
    input_file = input_entry.get()
    output_file = output_entry.get()

    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return

    try:
        with open(input_file, "r", encoding='utf-8') as f:  # Ensure proper encoding
            input_data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "Input file not found.")
        return
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in input file.")
        return

    geojson_output = convert_to_geojson(input_data)

    try:
        convert_to_geopackage(geojson_output, output_file)
        messagebox.showinfo("Success", "Conversion to GeoPackage completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create GUI
root = tk.Tk()
root.title("BBR - JSON2GeoPackage Konverter")

input_label = tk.Label(root, text="Input JSON fil:")
input_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)

input_button = tk.Button(root, text="Vælg", command=select_input_file)
input_button.grid(row=0, column=2, padx=5, pady=5)

output_label = tk.Label(root, text="Output GeoPackage fil:")
output_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)

output_button = tk.Button(root, text="Vælg", command=select_output_file)
output_button.grid(row=1, column=2, padx=5, pady=5)

convert_button = tk.Button(root, text="Konventer", command=convert)
convert_button.grid(row=2, column=1, padx=5, pady=5)

root.mainloop()
