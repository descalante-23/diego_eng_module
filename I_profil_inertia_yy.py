import numpy as np

def propiedades_ipe(hw:float,tw:float,bf:float,tf:float) -> float:
    """ 
    Esta función calcula la inercia en el eje y-y de un perfil tipo IPE
    Inputs:
    hw = Altura del alma (mm)
    tw = Espesor del alma (mm)
    bf = Ancho del patín (mm)
    tf = Espesor del patín (mm)
    """
    hw = hw - 2*tf
    I_flange = 1/12 * bf * tf**3 # Componente de la inercia del patín
    I_web = 1/12 * tw * hw**3 # Componente de la inercia del alma
    a_d2 = (bf*tf) * ((hw+tf)/2)**2 # Componente de Steiner para el patín
    A_p = bf*tf*2+hw*tw
    I_yy = 2*I_flange + I_web + 2*a_d2 # Inercia del Perfil en su eje YY
    print(f'A= {A_p:.2f} mm2')
    print(f'Iy= {I_yy:.2f} mm4')
    return

profil_inertia_yy(200,5.6,100,8.1)
