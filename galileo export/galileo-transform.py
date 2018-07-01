# -*- coding: utf-8 -*-
"""
Galileo Transofrm
Imports two Galileo Exports, merges, transforms and exports a single file.
"""

import pandas
import glob
import os
import numpy as np
import datetime

### Import latest files
rapperswil = glob.glob('../*RAPPERSWIL.xlsx')
lachen = glob.glob('../*LACHEN.xlsx')
latest_rapperswil = max(rapperswil, key=os.path.getctime)
latest_lachen = max(lachen, key=os.path.getctime)
rapperswil_data = pandas.read_excel(latest_rapperswil, header=3, index_col="ISBN/EAN")
lachen_data = pandas.read_excel(latest_lachen, header=3, index_col="ISBN/EAN")

#remove duplicate empty indices
rapperswil_data = rapperswil_data[rapperswil_data.index != '             ']
lachen_data = lachen_data[lachen_data.index != '             ']

print('loading files:' + latest_rapperswil + ' & ' + latest_lachen)

### Add location info as column
rapperswil_data["Filiale"] = "Rapperswil"
lachen_data["Filiale"] = "Lachen"

### Add MWst, Author & Lieferant
rapperswil_data["MwstCode"] = 2
lachen_data["MwstCode"] = 2
rapperswil_data["Autor"] = ""
lachen_data["Autor"] = ""
rapperswil_data = rapperswil_data.rename(columns={"Letzter Lieferant":"Lieferant"})
lachen_data = lachen_data.rename(columns={"Letzter Lieferant":"Lieferant"})

### Map iShopCategoryId
category_map = { 
    1: 330, 2: 315, 3: 331, 4: 332, 5: 336, 6: 336, 7: 336, 8: 335, 9: 336, 
    11: 330, 14: 340, 15: 340, 16: 340, 17: 341, 18: 342, 20: 300, 21: 301,  
    22: 302, 23: 308, 24: 305, 25: 333, 26: 339, 27: 334, 28: 312, 29: 313, 
    30: 303, 31: 328, 32: 309, 33: 310, 34: 338, 35: 311, 36: 304, 37: 306, 
    38: 299, 39: 307, 40: 317, 41: 326, 42: 318, 43: 324, 44: 325, 45: 327, 
    46: 323, 47: 322, 48: 319, 49: 320, 50: 321,
}

# drop with no WG
drop_rap = rapperswil_data[rapperswil_data["WG"] == '   ']
drop_lach = lachen_data[lachen_data["WG"] == '   ']
print("DROPPING:")
print(drop_rap["Titel"])
print(drop_lach["Titel"])

rapperswil_data = rapperswil_data[rapperswil_data.WG != '   ']
lachen_data = lachen_data[lachen_data.WG != '   ']

# create iShpoCategory col and transform to int
rapperswil_data["iShopCategoryId"] = pandas.to_numeric(rapperswil_data["WG"]).astype(np.int64)
lachen_data["iShopCategoryId"] = pandas.to_numeric(lachen_data["WG"]).astype(np.int64)

# map category map 
lachen_data = lachen_data.replace({"iShopCategoryId": category_map})
rapperswil_data = rapperswil_data.replace({"iShopCategoryId": category_map})

### Merge files add _lachen suffix
merged_df = rapperswil_data.join(lachen_data, how="outer", rsuffix="_lachen")
print(lachen_data.index)
print(rapperswil_data.index)
print(merged_df.shape)

###select rapperswilproice if true
rapperswilpreise = [315, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328]
merged_df["Rapperswilpreis"] = merged_df["iShopCategoryId"].apply(lambda x: x in rapperswilpreise) 
merged_df.loc[~merged_df["Rapperswilpreis"], "Eigener Preis"] = merged_df["Eigener Preis_lachen"].loc[~merged_df["Rapperswilpreis"]]

# remove unused _lachen variables
merged_df["ISBN/EAN"] = merged_df.index
merged_df = merged_df[["BZ-Nr.","UVP","WG","MwstCode","Lieferant","Titel","Autor","Bestand","Eigener Preis","Filiale","iShopCategoryId"]]

# merged_df["BZ-Nr."] = merged_df["BZ-Nr."].str.strip()

createdatdate = datetime.date.today().strftime("%Y%m%d")
merged_df.to_csv('../Export/' + createdatdate + "_Titelstamm_utf", sep=";", encoding="utf-16")

# data = get_data("../import/LACHEN.xlsx")