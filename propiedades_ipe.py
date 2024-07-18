import numpy as np

def propiedades_ipe(hw:float,tw:float,bf:float,tf:float) -> float:
    """
    Calcula las propiedades geometricas de un perfil tipo IPE
    hw = Altura del alma (mm)
    tw = Espesor del alma (mm)
    bf = Ancho del patin (mm)
    tf = Espesor del patin (mm)
    """
    hw = hw-2*tf #Altura nominal - Espesor de los patines
    A_perfil = 2*bf*tf+hw*tw #Area del perfil

    I_web = 1/12 * tw * hw**3 #Inercia del alma
    I_flange = 1/12 * bf * tf**3  #Inercia del flange
    a_d2 = (bf*tf)*((hw+tf)/2)**2   #Componente de Steiner para el Flange
    
    I_yy = I_web + 2*I_flange + 2*a_d2 #Inercia del perfil en el Eje YY

    print(f"A={A_perfil:.2f} mm2")
    print(f"Iy={I_yy:.2f} mm4")

    return

propiedades_ipe(200,5.6,100,8.1)
