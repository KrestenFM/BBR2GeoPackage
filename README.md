# BBR2GeoPackage
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python](https://img.shields.io/badge/Python-3.12.1-green) ![Language](https://img.shields.io/badge/Language-🇩🇰_Danish-red)

A repository for the conversion software between BBR Bygning from the datafordeler.dk REST API JSON output and the GeoPackage format.
The software was primarily created for use by the students, faculty and alumni of the Department of Sustainability and Planning at AAU - Aalborg University.

Notice that the packages geopandas, pyogrio, ttkbootstrap and requests are required for the python script, BBR2GeoPackage.py, to run.


# Running the script yourself

The executable has no requirements, but due to a lack of Windows certification and being compiled by Pyinstaller, it is considered "unsafe" by the OS and a false positive trojan can appear.
If this makes you uncomftable you can run the application yourself in the following steps. 

 1) Create a new conda enviroment, i recommend using [Miniforge-pypy3](https://github.com/conda-forge/miniforge) and i will be assuming this or another conda setup is what you are using.
    
      * If you havent allready run the command ```conda create [ENV_NAME]```
    
      * Run the command ```conda activate [ENV_NAME]```
 2) run the command ```conda install geopandas pyogrio -y```
 3) Run the command ```pip install ttkbootstrap -y```
 4) Navigate to the directory in which you have placed the BBR2GeoPackage.py Directory alongside its 'Resources' folder
    
      * You can do this using the command    cd [PATH TO DIRECTORY]
 5) Run the command ```Python BBR2GeoPackage.py```
