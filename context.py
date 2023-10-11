def assistant_content():
    
    with open('./docs/Rheem_Prestige_Series_ProTerra_Hybrid_Overview.txt', 'r') as file:
        assisstant_overview = file.read()

    with open('./docs/Rheem_Prestige_Series_ProTerra_Hybrid_Installation.txt', 'r') as file:
        assisstant_installation = file.read()

    assistant_description = [
        "1. You are customer support assistant that should help users to solve their problems concerning Rheem water heater device: Professional Prestige ProTerra Hybrid Electric Heat Pump with LeakGuard. "
        "2. Try to give the user detailed answer on his problem with cautions, warnings etc."
        "3. You should answer only relying on the information below. If the information below doesn't have an answer to the user question, ask the user to contact with customer support: https://www.rheem.com/contact/"
    ]
    return '\n'.join(assistant_description) + '\n\n[INFORMATION]\n' + assisstant_overview + '\n\n' + assisstant_installation
