# World map regions - simplified polygon coordinates (0.0 to 1.0 normalized)
# Format: (name, iso, continent, population_millions, climate, [polygon_points_x_y...])

REGIONS = [
    {
        "id": "br", "name": "Brasil", "continent": "América do Sul",
        "pop": 215, "climate": "tropical", "gdp": 2, "ports": 3, "airports": 3,
        "color_base": (0.1, 0.6, 0.1),
        "center": (0.285, 0.68),
        "poly": [
            0.22,0.58, 0.30,0.55, 0.38,0.57, 0.40,0.62, 0.38,0.70,
            0.33,0.75, 0.27,0.78, 0.22,0.74, 0.20,0.68, 0.22,0.62
        ]
    },
    {
        "id": "us", "name": "EUA", "continent": "América do Norte",
        "pop": 335, "climate": "temperate", "gdp": 3, "ports": 3, "airports": 3,
        "color_base": (0.2, 0.3, 0.7),
        "center": (0.185, 0.42),
        "poly": [
            0.10,0.34, 0.25,0.32, 0.27,0.38, 0.25,0.44, 0.22,0.50,
            0.15,0.52, 0.10,0.48, 0.08,0.42, 0.10,0.36
        ]
    },
    {
        "id": "ca", "name": "Canadá", "continent": "América do Norte",
        "pop": 38, "climate": "cold", "gdp": 2, "ports": 2, "airports": 2,
        "color_base": (0.6, 0.4, 0.2),
        "center": (0.175, 0.30),
        "poly": [
            0.07,0.22, 0.28,0.20, 0.29,0.30, 0.26,0.33, 0.10,0.34,
            0.07,0.30, 0.07,0.24
        ]
    },
    {
        "id": "mx", "name": "México", "continent": "América do Norte",
        "pop": 130, "climate": "arid", "gdp": 2, "ports": 2, "airports": 2,
        "color_base": (0.8, 0.6, 0.1),
        "center": (0.165, 0.525),
        "poly": [
            0.10,0.48, 0.22,0.50, 0.20,0.57, 0.15,0.59, 0.10,0.55, 0.10,0.50
        ]
    },
    {
        "id": "ar", "name": "Argentina", "continent": "América do Sul",
        "pop": 46, "climate": "temperate", "gdp": 1, "ports": 2, "airports": 2,
        "color_base": (0.5, 0.7, 0.9),
        "center": (0.265, 0.82),
        "poly": [
            0.22,0.74, 0.27,0.78, 0.28,0.84, 0.26,0.90, 0.23,0.93,
            0.20,0.88, 0.20,0.80, 0.22,0.76
        ]
    },
    {
        "id": "co", "name": "Colômbia", "continent": "América do Sul",
        "pop": 52, "climate": "tropical", "gdp": 1, "ports": 2, "airports": 2,
        "color_base": (0.9, 0.7, 0.1),
        "center": (0.235, 0.58),
        "poly": [
            0.20,0.55, 0.27,0.55, 0.27,0.62, 0.22,0.62, 0.19,0.59
        ]
    },
    {
        "id": "uk", "name": "Reino Unido", "continent": "Europa",
        "pop": 68, "climate": "cold", "gdp": 2, "ports": 3, "airports": 3,
        "color_base": (0.3, 0.3, 0.8),
        "center": (0.453, 0.285),
        "poly": [
            0.445,0.26, 0.46,0.26, 0.465,0.31, 0.455,0.315, 0.445,0.30
        ]
    },
    {
        "id": "fr", "name": "França", "continent": "Europa",
        "pop": 68, "climate": "temperate", "gdp": 2, "ports": 2, "airports": 3,
        "color_base": (0.1, 0.2, 0.8),
        "center": (0.468, 0.315),
        "poly": [
            0.455,0.295, 0.48,0.295, 0.485,0.33, 0.470,0.345, 0.455,0.33
        ]
    },
    {
        "id": "de", "name": "Alemanha", "continent": "Europa",
        "pop": 84, "climate": "temperate", "gdp": 3, "ports": 2, "airports": 3,
        "color_base": (0.5, 0.5, 0.5),
        "center": (0.488, 0.295),
        "poly": [
            0.478,0.270, 0.505,0.270, 0.508,0.300, 0.490,0.305, 0.477,0.298
        ]
    },
    {
        "id": "ru", "name": "Rússia", "continent": "Europa/Ásia",
        "pop": 145, "climate": "cold", "gdp": 2, "ports": 2, "airports": 3,
        "color_base": (0.7, 0.1, 0.1),
        "center": (0.60, 0.25),
        "poly": [
            0.50,0.15, 0.75,0.13, 0.80,0.22, 0.76,0.32, 0.65,0.35,
            0.55,0.33, 0.50,0.27, 0.50,0.18
        ]
    },
    {
        "id": "cn", "name": "China", "continent": "Ásia",
        "pop": 1400, "climate": "temperate", "gdp": 3, "ports": 3, "airports": 3,
        "color_base": (0.8, 0.1, 0.1),
        "center": (0.705, 0.39),
        "poly": [
            0.62,0.30, 0.76,0.30, 0.80,0.38, 0.77,0.48, 0.68,0.50,
            0.62,0.47, 0.60,0.38, 0.62,0.32
        ]
    },
    {
        "id": "in", "name": "Índia", "continent": "Ásia",
        "pop": 1420, "climate": "tropical", "gdp": 2, "ports": 2, "airports": 3,
        "color_base": (0.9, 0.5, 0.1),
        "center": (0.655, 0.475),
        "poly": [
            0.62,0.40, 0.69,0.40, 0.72,0.48, 0.68,0.58, 0.63,0.58,
            0.60,0.50, 0.62,0.42
        ]
    },
    {
        "id": "jp", "name": "Japão", "continent": "Ásia",
        "pop": 125, "climate": "temperate", "gdp": 3, "ports": 3, "airports": 3,
        "color_base": (0.9, 0.9, 0.9),
        "center": (0.795, 0.375),
        "poly": [
            0.785,0.34, 0.80,0.34, 0.805,0.42, 0.790,0.42, 0.783,0.37
        ]
    },
    {
        "id": "id", "name": "Indonésia", "continent": "Ásia",
        "pop": 277, "climate": "tropical", "gdp": 2, "ports": 3, "airports": 2,
        "color_base": (0.8, 0.4, 0.0),
        "center": (0.755, 0.59),
        "poly": [
            0.70,0.56, 0.80,0.56, 0.83,0.61, 0.78,0.64, 0.70,0.63, 0.68,0.59
        ]
    },
    {
        "id": "ng", "name": "Nigéria", "continent": "África",
        "pop": 218, "climate": "tropical", "gdp": 1, "ports": 2, "airports": 2,
        "color_base": (0.1, 0.5, 0.1),
        "center": (0.487, 0.535),
        "poly": [
            0.462,0.505, 0.510,0.505, 0.515,0.545, 0.500,0.565,
            0.470,0.560, 0.458,0.535
        ]
    },
    {
        "id": "eg", "name": "Egito", "continent": "África",
        "pop": 105, "climate": "arid", "gdp": 1, "ports": 2, "airports": 2,
        "color_base": (0.9, 0.8, 0.3),
        "center": (0.528, 0.44),
        "poly": [
            0.510,0.40, 0.548,0.40, 0.550,0.47, 0.525,0.475, 0.508,0.455
        ]
    },
    {
        "id": "za", "name": "África do Sul", "continent": "África",
        "pop": 60, "climate": "temperate", "gdp": 1, "ports": 2, "airports": 2,
        "color_base": (0.2, 0.6, 0.4),
        "center": (0.528, 0.745),
        "poly": [
            0.500,0.695, 0.555,0.695, 0.558,0.748, 0.530,0.78,
            0.500,0.755, 0.498,0.72
        ]
    },
    {
        "id": "au", "name": "Austrália", "continent": "Oceania",
        "pop": 26, "climate": "arid", "gdp": 2, "ports": 2, "airports": 3,
        "color_base": (0.8, 0.5, 0.1),
        "center": (0.798, 0.70),
        "poly": [
            0.740,0.615, 0.850,0.615, 0.865,0.680, 0.845,0.745,
            0.790,0.775, 0.745,0.750, 0.730,0.685, 0.738,0.628
        ]
    },
    {
        "id": "sa", "name": "Arábia Saudita", "continent": "Oriente Médio",
        "pop": 36, "climate": "arid", "gdp": 2, "ports": 2, "airports": 2,
        "color_base": (0.9, 0.7, 0.0),
        "center": (0.582, 0.445),
        "poly": [
            0.555,0.400, 0.610,0.400, 0.618,0.450, 0.600,0.480,
            0.565,0.482, 0.550,0.450
        ]
    },
    {
        "id": "pk", "name": "Paquistão", "continent": "Ásia",
        "pop": 231, "climate": "arid", "gdp": 1, "ports": 1, "airports": 2,
        "color_base": (0.0, 0.6, 0.3),
        "center": (0.627, 0.405),
        "poly": [
            0.606,0.365, 0.645,0.365, 0.648,0.408, 0.628,0.428,
            0.603,0.415, 0.604,0.378
        ]
    },
]

CONTINENTS = {
    "América do Norte": {"color": (0.2, 0.4, 0.8, 0.3)},
    "América do Sul":   {"color": (0.1, 0.7, 0.2, 0.3)},
    "Europa":           {"color": (0.3, 0.3, 0.9, 0.3)},
    "Europa/Ásia":      {"color": (0.6, 0.2, 0.2, 0.3)},
    "Ásia":             {"color": (0.8, 0.3, 0.1, 0.3)},
    "África":           {"color": (0.8, 0.6, 0.1, 0.3)},
    "Oceania":          {"color": (0.1, 0.6, 0.7, 0.3)},
    "Oriente Médio":    {"color": (0.7, 0.6, 0.0, 0.3)},
}

WORLD_TOTAL_POP = sum(r["pop"] for r in REGIONS)
