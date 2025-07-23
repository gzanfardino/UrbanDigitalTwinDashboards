# Risk zone
risk_map = {
    "residential": "Low",
    "apartments": "Low",
    "house": "Low",
    "industrial": "High",
    "construction": "High",
    "commercial": "Medium",
    "retail": "Medium",
    "school": "Medium",
    "warehouse": "High",
    "unknown": "Low"
}

istat_risk_map = {
    "1.00000000": "Low",
    "2.00000000": "Medium",
    "4.00000000": "High"
}

# Risk color map
color_map = {
    "High": "#FF4C4C", #Red
    "Medium": "#FFA500", #Orange
    "Low": "#4CAF50" #Green
}



# Assign risk zone
def assign_risk_zone(building_tags):
    building_type = building_tags.get("building", "unknown").lower()
    return risk_map.get(building_type, "Low")




# Province change
province_name_mapping = {
    "BELLUNO": "Belluno",
    "FIRENZE": "Firenze",
    "RAGUSA": "Ragusa",
    "CREMONA": "Cremona",
    "MILANO": "Milano",
    "VARESE": "Varese",
    "PADOVA": "Padova",
    "PARMA": "Parma",
    "PRATO": "Prato",
    "COMO": "Como",
    "LA SPEZIA": "La Spezia",
    "PORDENONE": "Pordenone",
    "UDINE": "Udine",
    "BRESCIA": "Brescia",
    "GORIZIA": "Gorizia",
    "BIELLA": "Biella",
    "TREVISO": "Treviso",
    "TORINO": "Torino",
    "PISA": "Pisa",
    "LUCCA": "Lucca",
    "GENOVA": "Genova",
    "CUNEO": "Cuneo",
    "SONDRIO": "Sondrio",
    "VERONA": "Verona",
    "PIACENZA": "Piacenza",
    "PAVIA": "Pavia",
    "": "-",  # empty string mapped to '-' entry
    "TRIESTE": "Trieste",
    "FERRARA": "Ferrara",
    "LODI": "Lodi",
    "PISTOIA": "Pistoia",
    "LIVORNO": "Livorno",
    "ROVIGO": "Rovigo",
    "ASTI": "Asti",
    "VICENZA": "Vicenza",
    "MASSA CARRARA": "Massa Carrara",
    "TRENTO": "Trento",
    "BOLOGNA": "Bologna",
    "MODENA": "Modena",
    "VENEZIA": "Venice",
    "NOVARA": "Novara",
    "REGGIO EMILIA": "Reggio nell'Emilia",
    "VERCELLI": "Vercelli",
    "MANTOVA": "Mantova",
    "LECCO": "Lecco",
    "IMPERIA": "Imperia",
    "BERGAMO": "Bergamo",
    "BOLZANO": "Bolzano",
    "AOSTA": "Aosta",
    "ALESSANDRIA": "Alessandria",
    "RAVENNA": "Ravenna",
    "ISERNIA": "Isernia",
    "VITERBO": "Viterbo",
    "ROMA": "Rome",  
    "NAPOLI": "Napoli",
    "MACERATA": "Macerata",
    "SIENA": "Siena",
    "CHIETI": "Chieti",
    "SALERNO": "Salerno",
    "CASERTA": "Caserta",
    "RIMINI": "Rimini",
    "TERNI": "Terni",
    "RIETI": "Rieti",
    "PERUGIA": "Perugia",
    "PESCARA": "Pescara",
    "CAMPOBASSO": "Campobasso",
    "AREZZO": "Arezzo",
    "PESARO E URBINO": "Pesaro e Urbino",
    "FORLI'": "Forli'-Cesena",
    "L'AQUILA": "L'Aquila",
    "BENEVENTO": "Benevento",
    "ANCONA": "Ancona",
    "MESSINA": "Messina",
    "REGGIO CALABRIA": "Reggio Calabria",  
    "CAGLIARI": "Cagliari",
    "SASSARI": "Sassari",
    "BARI": "Bari",
    "VIBO VALENTIA": "Vibo Valentia",
    "BRINDISI": "Brindisi",
    "ENNA": "Enna",
    "MATERA": "Matera",
    "PALERMO": "Palermo",
    "TRAPANI": "Trapani",
    "NUORO": "Nuoro",
    "ORISTANO": "Oristano",
    "CATANIA": "Catania",
    "LECCE": "Lecce",
    "TARANTO": "Taranto",
    "CROTONE": "Crotone",
    "COSENZA": "Cosenza",
    "SIRACUSA": "Siracusa",
    "ASCOLI PICENO": "Ascoli Piceno",
    "LATINA": "Latina",
    "AVELLINO": "Avellino",
    "FROSINONE": "Frosinone",
    "TERAMO": "Teramo",
    "FOGGIA": "Foggia",
    "CALTANISSETTA": "Caltanissetta",
    "CATANZARO": "Catanzaro",
    "VERBANO-CUSIO-OSSOLA": "Verbano-Cusio-Ossola",
    "SAVONA": "Savona",
    "POTENZA": "Potenza",
    "AGRIGENTO": "Agrigento",
    "GROSSETO": "Grosseto",
    "MONZA E DELLA BRIANZA": "Monza e della Brianza",
    "FERMO": "Fermo",
    "BARLETTA-ANDRIA-TRANI": "Barletta-Andria-Trani",
    "SUD SARDEGNA": "Sud Sardegna",
}
