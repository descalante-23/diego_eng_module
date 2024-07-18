from PyNite import FEModel3D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def continuous_beam(
    w: float, 
    l1: float,
    l2: float,
    l3: float,
    E: float = 1,
    I: float = 1,
    A: float = 1,
    J: float = 1,
    nu: float = 0.3,
    p: float = 1,
    ):
    
    """
    Returns the reactions of a continuous beam with three spans, based on the FEModel tool from PyNite
    w = uniform load (gravity direction)
    l1 = length of the first span
    l2 = length of the second span
    l3 = length of the third span
    E = Young Modulus
    I = Moment of Inertia respect to the flexural axis
    A = Cross section area
    J = Polar moment of Inertia
    nu = Poisson's ratio
    p = Density
    """
    beam_model = FEModel3D()
    G = E/(2*(1+nu))
    
    # Material properties
    beam_model.add_material("default", E, G, nu, p) 
    
    # Node definitions
    beam_model.add_node("N0", 0, 0, 0) 
    beam_model.add_node("N1", l1, 0, 0)
    beam_model.add_node("N2", l1 + l2, 0, 0)
    beam_model.add_node("N3", l1 + l2 + l3, 0, 0)
    
    # Support definitions
    beam_model.def_support("N0", True, True, True, True, True, False)
    beam_model.def_support("N1", False, True, False, False, False, False)
    beam_model.def_support("N2", False, True, False, False, False, False)
    beam_model.def_support("N3", False, True, False, False, False, False)
    
    # Member definitions
    beam_model.add_member("M0", "N0", "N1", "default", Iy=1, Iz=I, J=J, A=A)
    beam_model.add_member("M1", "N1", "N2", "default", Iy=1, Iz=I, J=J, A=A)
    beam_model.add_member("M2", "N2", "N3", "default", Iy=1, Iz=I, J=J, A=A)

    # Loads
    beam_model.add_member_dist_load("M0", "FY", w1=w, w2=w)
    beam_model.add_member_dist_load("M1", "FY", w1=w, w2=w)
    beam_model.add_member_dist_load("M2", "FY", w1=w, w2=w)
    
    # Analyze the model
    beam_model.analyze()
    
    # Extract moment and shear results
    members = ["M0", "M1", "M2"]
    shear_data = []
    moment_data = []
    num_points = 50  # Number of points to evaluate along each member

    x_offsets = [0, l1, l1 + l2]
    
    for i, member in enumerate(members):
        member_length = beam_model.Members[member].L()
        x_positions = np.linspace(0, member_length, num_points)
        
        shear = [(x + x_offsets[i], beam_model.Members[member].shear('Fy', x)) for x in x_positions]
        moment = [(x + x_offsets[i], beam_model.Members[member].moment('Mz', x)) for x in x_positions]
        
        shear_data.extend(shear)
        moment_data.extend(moment)
    
    # Plotting Moment and Shear diagrams
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), sharex=True)

    for i, (shear, moment) in enumerate([(shear_data, moment_data)]):
        x_shear, V = zip(*shear)
        x_moment, M = zip(*moment)
        
        ax1.plot(x_shear, V, label='Shear Diagram', color='blue')
        ax2.plot(x_moment, M, label='Moment Diagram', color='blue')
    
    ax1.set_title('Shear Diagram')
    ax1.set_ylabel('Shear Force (kN)')
    ax1.legend()
    ax1.grid(True)
    
    ax2.set_title('Moment Diagram')
    ax2.set_xlabel('Length (m)')
    ax2.set_ylabel('Moment (kNm)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return x_offsets, shear_data, moment_data

def create_summary_table(shear_data, moment_data):
    shear_values = [v for x, v in shear_data]
    moment_values = [m for x, m in moment_data]
    
    summary_data = {
        'Quantity': ['Shear Force (V)', 'Moment (M)'],
        'Minimum': [min(shear_values), min(moment_values)],
        'Maximum': [max(shear_values), max(moment_values)]
    }
    
    summary_table = pd.DataFrame(summary_data)
    return summary_table

def get_shear_moment_at_x(x_offset, shear_data, moment_data):
    """
    Returns the shear force and moment at a specific x_offset along the beam.
    """
    shear = None
    moment = None

    for x, v in shear_data:
        if x >= x_offset:
            shear = v
            break

    for x, m in moment_data:
        if x >= x_offset:
            moment = m
            break

    return shear, moment
