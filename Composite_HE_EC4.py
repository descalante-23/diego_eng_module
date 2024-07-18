import numpy as np
import math
import matplotlib.pyplot as plt

def chi_coeff(lambda_value: float, line_type: str) -> float:
    """
    Calculates the Chi coefficient of the buckling lines of the EC4.
    
    Parameters:
        lambda_value (float): The coefficient for Column Slenderness.
        line_type (str): Character of the line type for the EC4 ('a', 'b', 'c', 'd').
        
    Returns:
        float: The Chi coefficient.
    """
    lines = {
        'a': {'alpha': 0.21, 'lambda_1': 1.0},
        'b': {'alpha': 0.34, 'lambda_1': 1.0},
        'c': {'alpha': 0.49, 'lambda_1': 1.0},
        'd': {'alpha': 0.76, 'lambda_1': 1.0}
    }
    
    if line_type not in lines:
        raise ValueError("Invalid buckling curve type. Valid types are 'a', 'b', 'c', 'd'.")
    
    alpha = lines[line_type]['alpha']
    lambda_1 = lines[line_type]['lambda_1']
    bar_lambda = lambda_value / lambda_1
    phi = 0.5 * (1 + alpha * (bar_lambda - 0.2) + bar_lambda**2)
    chi = 1 / (phi + (phi**2 - bar_lambda**2)**0.5)
    
    return chi

def composite_HE_ec4(L: float, b: float, h: float, A_st: float, I_st: float, As_b: float, I_by: float, fy: int, fc: int,fs:int =500, Ec: int = 34,Es: int = 200):
    """
    Designs a HE-Profile Steel-Concrete composite column according to the EC4.
    
    Parameters:
        L (float): Column length in m.
        b (float): Column width in mm.
        h (float): Column height in mm.
        A_st (float): H-Profile cross section in cm².
        I_st (float): H-Profile Inertia along Y-Y axis in cm⁴.
        As_b (float): Reinforcement cross section in cm².
        I_by (float): Reinforcement inertia in cm⁴.
        fy (int): Steel nominal yield strength in MPa.
        fc (int): Concrete nominal compressive strength in MPa.
        fs (int): Reinforcement steel nominal yield strength in MPa. Defaults to 500 MPa.
        Ec (int, optional): Concrete E-Module in GPa. Defaults to 34 GPa.
        Es (int, optional): Steel E-Module in GPa. Defaults to 200 GPa and 210 GPa for reinforcement.
    """
    # Safety factors
    gamma_M = 1.0  # Safety factor for steel
    gamma_C = 1.5  # Safety factor for concrete
    gamma_B = 1.15 # Safety factor for reinforcement steel 

    fyd = fy / gamma_M
    fcd = 0.85 * fc / gamma_C
    fsd = fs/ gamma_B

    E_sm = Es * 1e3    # Steel E-Module in MPa
    E_cm = Ec * 1e3 # Concrete E-Module in MPa
    phi_t = 2.5     # Concrete creep coefficient

    # Load Inputs (N and N*m)
    N_ed = 2200e3  # Total applied axial load
    N_gd = 1400e3  # Total constantly applied vertical load (dead load)

    # Geometrical Properties
    b_c = b / 1000    # Column base in meters
    h_c = h / 1000    # Column height in meters
    I_s = I_st / 1e8  # H-Profile Inertia in m⁴
    I_b = I_by / 1e8  # Steel reinforcement inertia in m⁴
    I_c = (1/12) * b_c * h_c**3 - I_s - I_b # Concrete Inertia in m⁴

    Ec_eff = E_cm / (1 + (N_gd / N_ed) * phi_t) # Effective E-Modul of concrete

    EI_eff = E_sm * I_s + 0.6 * Ec_eff * I_c + I_b * 200e3 # Effective EI of Composite section
    N_cr = EI_eff * math.pi**2 / L**2 # Critical buckling load
    A_st = A_st / 1e4 # Profile cross section 
    As_b = As_b / 1e4 # Reinforcement cross section
    A_c = (b_c * h_c) - (A_st + As_b) #Concrete cross section

    # Plastic compressive strength
    Npl_rk = fy * A_st + fsd * As_b + fc * A_c
    Npl_rd = fyd * A_st + fsd * As_b + fcd * A_c

    # Slenderness and Chi coefficients
    lambda_k = math.sqrt(Npl_rk / N_cr)
    chi = chi_coeff(lambda_k, "c")

    # Point D - Fully plastic moment capacity 
    t_w = 1 / 100 # HE Profile Web thickness 
    h_n = A_c / (2 * (b_c - t_w + (2 * t_w * (fyd / (0.85 * fcd)))))

    W_pla = 1283 * 1e-6  # HE Profile plastic section modulus in m³
    W_pls = 40 * 1e-6  # Reinforcement plastic section modulus in m³
    W_plc = (b_c * h_c**2) / 4 - W_pla - W_pls # Concrete cross section plastic modulus in m³
    

    M_max_rd = W_pla * fyd + 0.5 * W_plc * fcd + W_pls * fsd # Maximum plastic moment
    N_d_rd = 0.5 * A_c * fcd # Vertical load at point D

    # Maximal moment capacity
    M_b_rd = M_max_rd - (2 * h_n**2 * t_w / 6 * fsd) - (2 * h_n**2 * (b_c - t_w) / 6 ) * fcd # Moment capacity at point B
    M_c_rd = M_b_rd # Moment capacity at point C and B
    N_b_rd = A_c * fcd # Vertical load at point B

    #print(f"I_c= {I_c*1e8:.2f} cm⁴")
    #print(f"Ec_eff= {Ec_eff:.2f} MPa.m²")
    #print(f"EI_eff= {EI_eff:.2f} MPa.m²")
    print(f"N_cr= {N_cr*1e3:.2f} kN")
    print(f"N_pl_rd= {Npl_rd*1e3:.2f} kN")
    #print(f"h_n= {h_n*100:.2f} cm")
    print(f"M_max_rd= {M_max_rd*1e3:.2f} kNm")
    print(f"M_pl_rd= {M_b_rd*1e3:.2f} kNm")

    # Plotting
    points = {
        "A": (0, Npl_rd * 1e3),
        "B": (M_b_rd * 1e3, N_b_rd * 1e3),
        "D": (M_max_rd * 1e3, N_d_rd * 1e3),
        "C": (M_c_rd * 1e3, 0)
    }

    x_vals = [points[p][0] for p in points]
    y_vals = [points[p][1] for p in points]

    plt.figure(figsize=(10, 6))
    plt.scatter(x_vals, y_vals, color='red')
    for label, (x, y) in points.items():
        plt.annotate(label, (x, y), textcoords="offset points", xytext=(5, 5), ha='center')
        
    plt.plot(x_vals, y_vals, linestyle='--', color='blue')

    plt.xlabel('Moment M_Rd (kNm)')
    plt.ylabel('Vertical Load N_Rd (kN)')
    plt.title('Interaction Diagram for Composite HEB')
    
    # Set the aspect ratio
    plt.gca().set_aspect(0.1)  # This sets the y-axis to be 1/10th of the x-axis

    # Set axis limits to start from 0
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    
    plt.grid(True)
    plt.show()





