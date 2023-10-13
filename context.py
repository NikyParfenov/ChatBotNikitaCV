from glob import glob


def assistant_content():
    # first 29 pages from https://s3.amazonaws.com/WebPartners/ProductDocuments/2679665F-4FDA-42AC-8DBF-A938F4CA2FAC.pdf
    context = []
    for path in glob('./docs/*.txt'):
        with open(path, 'r') as file:
            context.append(file.read())

    context = '\n\n'.join(context)

    assistant_description = [
        "1. You are customer support assistant that should help users to solve their problems concerning Rheem water heater device: Professional Prestige ProTerra Hybrid Electric Heat Pump with LeakGuard.",
        "2. Try to give the user detailed structured answer on his problem with solution, cautions, warnings etc.",
        "3. You should answer only relying on the information below. If the information below doesn't have an answer to the user question, ask the user to contact with customer support by the link https://www.rheem.com/contact/",
    ]
    return '\n'.join(assistant_description) + '\n\n[INFORMATION]\n' + context
