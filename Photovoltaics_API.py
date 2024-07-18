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
    
    return
    

def pv_module_area(W_hh, W_car, eta_pv, lat, lon, eta_tilt):
    """
    Calculate the required area of the PV module for a household and an electric car, considering the tilt of the panels
    and retrieving the global radiation based on latitude and longitude.

    Parameters:
    W_hh (float): Electricity consumption of the household in kWh/day.
    W_car (float): Electricity consumption of the car per charging session.
    eta_pv (float): Efficiency of the PV system.
    lat (float): Latitude of the location.
    lon (float): Longitude of the location.
    eta_tilt (float): Efficiency adjustment factor due to tilt.

    Returns:
    float: Required area of the PV module in m^2.
    """
    q_global = get_global_radiation(lat, lon)
    W_total = W_hh + W_car
    W_pv_needed = W_total / eta_pv
    q_tilt = q_global * eta_tilt
    A = W_pv_needed / q_tilt;
   
    return A

