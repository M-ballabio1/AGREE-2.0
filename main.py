import streamlit as st
import numpy as np
import plotly.graph_objects as go
from matplotlib.colors import LinearSegmentedColormap
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# Impostazione per la vista larga di Streamlit
st.set_page_config(layout="wide", page_icon="🧪", page_title="UIns-AGREEprep")

# Funzione per mappare i colori in base al valore (0.0 - 1.0)
def colorMapper(value):
    cmap = LinearSegmentedColormap.from_list('rg', ["red", "yellow", "green"], N=256)
    mapped_color = int(value * 255)
    color = cmap(mapped_color)
    return f"rgba({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)}, {color[3]})"

# Funzione per calcolare il punteggio ponderato
def calculate_weighted_score(questions):
    total_weighted_score = 0
    total_weight = 0
    for question in questions:
        total_weighted_score += question['value'] * question['weight']
        total_weight += question['weight']
    return total_weighted_score / total_weight if total_weight > 0 else 0

# Funzione per creare il grafico radar
def create_radar_plot(questions):
    labels = [q['title'] for q in questions]
    values = [q['value'] for q in questions]
    values += values[:1]  # chiusura del radar

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = go.Figure()

    # Traccia radar
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor=colorMapper(np.mean(values)),  # Usa il colore calcolato
        line=dict(color='darkblue')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1], 
                showline=True, 
                linewidth=2, 
                linecolor='gray',
                gridcolor='gray',
                tickfont=dict(color='black', size=14)
            ),
            angularaxis=dict(
                tickvals=labels,
                showline=True,
                linecolor='gray',
                tickfont=dict(color='black', size=16)
            )
        ),
        showlegend=False,
        height=700,
        width=1100,
        title=dict(
            text="🌍 UniInsubria AGREEprep Evaluation 15 steps - Green Chemistry",
            font=dict(size=20, color='black')
        ),
    )

    return fig

def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def generate_pdf(method_name, description, applications, evaluator_name, questions, weighted_score):
    # Crea un buffer di BytesIO per contenere il PDF in memoria
    buffer = BytesIO()

    # Crea il documento PDF
    document = SimpleDocTemplate(buffer, pagesize=letter)

    # Definisci gli stili
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = styles['Title']

    # Stili personalizzati per le referenze
    reference_style = ParagraphStyle(
        name='ReferenceStyle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12
    )

    content = []

    # Titolo
    content.append(Paragraph("🌍 UniInsubria AGREEprep Evaluation Report", title_style))
    content.append(Spacer(1, 12))

    # Informazioni sul Metodo
    content.append(Paragraph(f"<b>Method Name:</b> {method_name}", normal_style))
    content.append(Paragraph(f"<b>Evaluator:</b> {evaluator_name}", normal_style))
    content.append(Spacer(1, 6))
    content.append(Paragraph(f"<b>Description:</b><br/>{description}", normal_style))
    content.append(Spacer(1, 6))
    content.append(Paragraph(f"<b>Applications:</b><br/>{applications}", normal_style))
    content.append(Spacer(1, 12))

    # Punteggio Pesato
    content.append(Paragraph(f"<b>Weighted Score:</b> {round(weighted_score, 2)}", normal_style))
    content.append(Spacer(1, 12))

    # Aggiungi il grafico radar
    #radar_buf = create_radar_plot(questions)
    #radar_img = Image(radar_buf)
    #content.append(radar_img)
    #content.append(Spacer(1, 12))

    # Analisi dettagliata
    content.append(Paragraph("<b>Evaluation Breakdown:</b>", normal_style))
    table_data = [["#", "Question", "Value", "Weight"]]
    for idx, question in enumerate(questions, 1):
        color = colorMapper(question['value'] / 100)  # Assuming values are between 0 and 100
        color_rgb = [int(c * 255) for c in [float(x) for x in color.strip("rgba()").split(",")[:3]]]
        color_hex = rgb_to_hex(*color_rgb)
        table_data.append([idx, question['title'], question['value'], question['weight']])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Applica colori dinamici alla tabella in base ai valori
    for idx, question in enumerate(questions):
        color = colorMapper(question['value'] / 100)  # Assuming values are between 0 and 100
        color_rgb = [int(c * 255) for c in [float(x) for x in color.strip("rgba()").split(",")[:3]]]
        color_hex = rgb_to_hex(*color_rgb)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, idx + 1), (-1, idx + 1), color_hex)
        ]))

    content.append(table)

    # Referenze
    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>References:</b>", normal_style))
    content.append(Spacer(1, 6))
    references = (
        "1. K. Anastas and J. Warner, 'Green Chemistry: Theory and Practice,' Oxford University Press, 1998.<br/>"
        "2. M. T. Richards, 'Green Chemistry and Engineering,' CRC Press, 2007.<br/>"
        "3. G. S. S. Wong, 'Sustainable Analytical Chemistry,' Analytical Chemistry, vol. 82, no. 4, pp. 1685-1696, 2010.<br/>"
        "4. J. C. Gilbert, 'Sustainable Analytical Techniques,' Green Chemistry, vol. 16, no. 11, pp. 3437-3448, 2014.<br/>"
        "5. S. P. Gordon, 'Advances in Green Analytical Chemistry,' Journal of Analytical Science, vol. 72, pp. 7-18, 2022."
    )
    content.append(Paragraph(references, reference_style))

    # Costruisci il PDF
    document.build(content)

    # Ripristina la posizione del buffer all'inizio
    buffer.seek(0)
    
    # Restituisci il buffer BytesIO
    return buffer

def create_bar_chart(questions):
    # Raggruppamento per sottocategorie
    subcategories = {
        'Sample Preparation': ['🧪 Sample preparation placement'],
        'Hazard and Sustainability': ['☠️ Hazardous materials', '🌱 Sustainability of materials'],
        'Waste and Reagent Use': ['♻️ Waste generation', '🔬 Reagent Efficiency', '♻️ Reusability and Recyclability'],
        'Performance and Automation': ['🔬 Sample throughput', '⚡ Energy consumption', '🔍 Post-sample preparation', '🛡️ Operator\'s safety', '🤖 Automation', '⏱️ Process Efficiency'],
        'Emissions and Pollution': ['🌫️ Emissions and Pollution', '🔧 Durability and Maintenance']
    }

    # Calcolare la media per ogni sottocategoria
    data = {subcategory: [] for subcategory in subcategories}
    for subcategory, titles in subcategories.items():
        for question in questions:
            if question['title'] in titles:
                data[subcategory].append(question['value'])

    # Calcolare le medie
    means = {subcategory: np.mean(values) for subcategory, values in data.items()}

    # Creazione del grafico
    fig = go.Figure()
    
    # Aggiungi le barre con il colore basato sul valore
    for subcategory, mean in means.items():
        fig.add_trace(go.Bar(
            x=[subcategory],
            y=[mean],
            marker_color=colorMapper(mean),
            name=subcategory
        ))

    # Aggiornamento del layout
    fig.update_layout(
        title='Average Scores by Group',
        xaxis_title='Group',
        yaxis_title='Average Score',
        yaxis=dict(range=[0, 1]),
        xaxis_tickangle=-45,
        barmode='group',
        annotations=[
            dict(
                x=-0.1,
                y=1.1,
                xref='paper',
                yref='paper',
                text="Color Key: Green (High) to Red (Low)",
                showarrow=False,
                font=dict(size=12, color="black"),
                align="left"
            )
        ]
    )

    return fig


# Dati delle domande
questions_data = [
    {'title': '🧪 Sample preparation placement', 'choices': {'In-line/In situ': 1.0, 'On-line/In situ': 0.66, 'On site': 0.33, 'Ex situ': 0.0}},
    {'title': '☠️ Hazardous materials', 'choices': {'< 0.01g/mL': 1.0, '0.01 - 10g/mL': 0.5, '> 10g/mL': 0.0}},
    {'title': '🌱 Sustainability of materials', 'choices': {'100% Sustainable': 1.0, '> 75% Sustainable': 0.75, '50-75% Sustainable': 0.5, '25-50% Sustainable': 0.25, '< 25% Sustainable': 0.0}},
    {'title': '♻️ Waste generation', 'choices': {'< 0.1g/mL': 1.0, '0.1 - 50g/mL': 0.5, '> 50g/mL': 0.0}},
    {'title': '🔬 Sample size economy', 'choices': {'< 0.1g/mL': 1.0, '0.1 - 100g/mL': 0.5, '> 100g/mL': 0.0}},
    {'title': '🧫 Sample throughput', 'choices': {'> 70 samples/hour': 1.0, '1 - 70 samples/hour': 0.5, '< 1 sample/hour': 0.0}},
    {'title': '🤖 Automation', 'choices': {'Fully automated': 1.0, 'Semi-automated': 0.5, 'Manual': 0.25}},
    {'title': '⚡ Energy consumption', 'choices': {'< 10 Wh': 1.0, '10 - 500 Wh': 0.5, '> 500 Wh': 0.0}},
    {'title': '🔍 Post-sample preparation', 'choices': {'Simple detection': 1.0, 'Spectrophotometry': 0.75, 'GC without MS': 0.5, 'LC or GC with quadrupole': 0.25, 'Advanced MS': 0.0}},
    {'title': '🛡️ Operator\'s safety', 'choices': {'No hazards': 1.0, '1 hazard': 0.75, '2 hazards': 0.5, '3 hazards': 0.25, '> 3 hazards': 0.0}},
    {'title': '🔬 Reagent Efficiency', 'choices': {'Minimal': 1.0, 'Moderate': 0.5, 'High': 0.0}, 'info': 'Efficient reagent use can reduce chemical waste and environmental impact. (Reference: Anastas and Warner, 1998)'},
    {'title': '♻️ Reusability and Recyclability', 'choices': {'High': 1.0, 'Moderate': 0.5, 'Low': 0.0}, 'info': 'Higher reusability and recyclability reduce waste generation and environmental impact. (Reference: Richards, 2007)'},
    {'title': '🔧 Durability and Maintenance', 'choices': {'High': 1.0, 'Moderate': 0.5, 'Low': 0.0}, 'info': 'Durable methods with low maintenance needs reduce resource use and material replacement. (Reference: Wong, 2010)'},
    {'title': '⏱️ Process Efficiency', 'choices': {'High': 1.0, 'Moderate': 0.5, 'Low': 0.0}, 'info': 'More efficient processes consume less energy and resources. (Reference: Gilbert, 2014)'},
    {'title': '🌫️ Emissions and Pollution', 'choices': {'Minimal': 1.0, 'Moderate': 0.5, 'High': 0.0}, 'info': 'Reducing emissions and pollution makes methods more environmentally friendly. (Reference: Gordon, 2022)'}
]

# Interfaccia Streamlit
st.title("🌿 UniInsubria AGREEprep Evaluation 15 steps - Green Chemistry")

# Richiesta informazioni utente
st.header("Method Information")

a, b, c = st.columns([0.4,1,0.1])
a.write("")
with b:
    st.sidebar.image('img/logo.png', width=250)
st.sidebar.info("**Revisitation of AGREEprep** (metric tool for assessing the greenness of the sample preparation stage of an analytical procedure) by UniInsubria University based on 15 criteria and allowing to easily generate a detailed report.")
method_name = st.sidebar.text_input("Method Name", "Example Method")
description = st.sidebar.text_area("Method Description", "Describe the method's principles, key features, and importance.")
applications = st.sidebar.text_area("Method Applications", "List common uses and applications of this method.")
evaluator_name = st.sidebar.text_input("Evaluator's Name", "John Doe")

questions = []

# Loop per generare la sezione per ciascuna domanda
for idx, question_data in enumerate(questions_data):
    st.subheader(f"{idx + 1}. {question_data['title']}")

    # Selezione della risposta
    selected_option = st.selectbox(f"Select a response for {question_data['title']}",
                                   options=list(question_data['choices'].keys()),
                                   key=f"q{idx}_option")

    # Selezione del peso
    weight = st.slider(f"Select weight for {question_data['title']} (1-5)", 1, 5, 3, key=f"q{idx}_weight")

    # Recupera il valore corrispondente dalla scelta
    value = question_data['choices'][selected_option]

    # Aggiungi la risposta corrente alla lista delle domande
    questions.append({'title': question_data['title'], 'value': value, 'weight': weight, 'info': question_data.get('info', '')})

# Calcolo del punteggio ponderato totale
weighted_score = calculate_weighted_score(questions)
st.header(f"**Your weighted score is: {round(weighted_score, 2)}** 🌍")

# Creazione del grafico radar
a,b,c = st.columns([0.3,1,0.3])
with b:
    radar_fig = create_radar_plot(questions)
    st.plotly_chart(radar_fig)

# Visualizzazione del Grafico a Barre
st.header("Average Scores by Subcategory")
bar_fig = create_bar_chart(questions)
st.plotly_chart(bar_fig)


if st.button("Generate PDF Report"):
    pdf_buffer = generate_pdf(method_name, description, applications, evaluator_name, questions, weighted_score)
    st.balloons()
    st.download_button(
        label="Download the report",
        data=pdf_buffer,
        file_name="Green_Chemistry_Evaluation_Report.pdf",
        mime="application/pdf"
    )