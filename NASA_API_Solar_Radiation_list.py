import requests

def get_global_radiation(lat, lon):
    """
    Fetches the median global radiation for a given latitude and longitude.
    
    Parameters:
    lat (float): Latitude of the location.
    lon (float): Longitude of the location.
    
    Returns:
    float: Median global radiation in kWh/m^2/day.
    """
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&start=20230101&end=20231231&format=JSON"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        radiation = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        annual_average_radiation = sum(radiation.values()) / len(radiation)
        return annual_average_radiation
    else:
        raise Exception("Error fetching data from the API")

def calculate_pv_module_area_tilt_lat_lon(W_el_hh, W_car, s, eta_laden, eta_pv, lat, lon, eta_tilt):
    """
    Calculate the required area of the PV module for a household and an electric car, considering the tilt of the panels
    and retrieving the global radiation based on latitude and longitude.

    Parameters:
    W_el_hh (float): Electricity consumption of the household in kWh/day.
    W_car (float): Electricity consumption of the car per 100 km in kWh/100 km.
    s (float): Daily driving distance of the car in km/day.
    eta_laden (float): Efficiency when charging the car.
    eta_pv (float): Efficiency of the PV system.
    lat (float): Latitude of the location.
    lon (float): Longitude of the location.
    eta_tilt (float): Efficiency adjustment factor due to tilt.

    Returns:
    float: Required area of the PV module in m^2.
    """
    q_global = get_global_radiation(lat, lon)
    
    W_car_day = W_car * (s / 100)
    W_car_eff = W_car_day / eta_laden
    W_total = W_el_hh + W_car_eff
    W_pv_needed = W_total / eta_pv
    q_tilt = q_global * eta_tilt
    A = W_pv_needed / q_tilt
    
    return A

# Given variables
W_el_hh = 10  # kWh/day
W_car = 20  # kWh/100 km
s = 40  # km/day
eta_laden = 0.90
eta_pv = 0.15
eta_tilt = 0.9  # Adjustment factor for the tilt angle (example value)

# List of cities with coordinates
cities = {
    "México DF": (19.4326, -99.1332),
    "Quito": (-0.1807, -78.4678),
    "Buenos Aires": (-34.6037, -58.3816),
    "Zaragoza": (41.6488, -0.8891),
    "Lima": (-12.0464, -77.0428)
}

# Calculate and print the required PV module area for each city
for city, (latitude, longitude) in cities.items():
    try:
        required_pv_area = calculate_pv_module_area_tilt_lat_lon(W_el_hh, W_car, s, eta_laden, eta_pv, latitude, longitude, eta_tilt)
        print(f"Required PV module area for {city}: {required_pv_area:.2f} m²")
    except Exception as e:
        print(f"Could not calculate PV module area for {city}: {e}")

