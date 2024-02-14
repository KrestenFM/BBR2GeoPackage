# Written by KrestenFM

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
        messagebox.showerror("Error", "Vælg venligst en input fil.")
        return

    try:
        with open(input_file, "r", encoding='utf-8') as f:  # Ensure proper encoding
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
        messagebox.showinfo("Success", "Konventering til GeoPackage fuldført.")
    except Exception as e:
        messagebox.showerror("Fejl", f"En fejl er opstået: {str(e)}")

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
