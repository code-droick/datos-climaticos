import requests
import pandas as pd
from jinja2 import Template

# ==========================================
# 1. EXTRACCIÓN DE DATOS (API)
# ==========================================
def obtener_datos_api():
    """
    Nos conectamos a una API pública. En este ejemplo, datos climáticos 
    históricos y actuales de una ubicación para hacer análisis.
    """
    # API de Open-Meteo para datos diarios (temperaturas máx/mín)
    url = "https://api.open-meteo.com/v1/forecast?latitude=10.9981&longitude=-63.801&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error al consultar la API")

# ==========================================
# 2. PROCESAMIENTO Y ANÁLISIS DE DATOS
# ==========================================
def analizar_datos(raw_data):
    """
    Aquí es donde entra la magia del Análisis de Datos. 
    Convertimos la respuesta de la API a un DataFrame de Pandas para analizar.
    """
    df = pd.DataFrame(raw_data['daily'])
    
    # Calculamos el rango térmico diario
    df['rango_termico'] = df['temperature_2m_max'] - df['temperature_2m_min']
    
    # Extraemos métricas y "Datos Curiosos" analíticos
    dia_mas_caluroso = df.loc[df['temperature_2m_max'].idxmax()]
    dia_mas_frio = df.loc[df['temperature_2m_min'].idxmin()]
    promedio_max = round(df['temperature_2m_max'].mean(), 1)
    
    # Creamos nuestra colección de "Datos Curiosos" derivados del análisis
    insights = [
        f"🔥 El día más caluroso del periodo será el {dia_mas_caluroso['time']} alcanzando {dia_mas_caluroso['temperature_2m_max']}°C.",
        f"❄️ La temperatura más baja registrada en el pronóstico es de {dia_mas_frio['temperature_2m_min']}°C el {dia_mas_frio['time']}.",
        f"📊 La temperatura máxima promedio estimada es de {promedio_max}°C.",
        f"🌧️ Total de precipitación acumulada prevista: {round(df['precipitation_sum'].sum(), 2)} mm."
    ]
    
    return {
        "fechas": df['time'].tolist(),
        "temp_max": df['temperature_2m_max'].tolist(),
        "temp_min": df['temperature_2m_min'].tolist(),
        "insights": insights
    }

# ==========================================
# 3. GENERACIÓN DE LA PÁGINA WEB (HTML)
# ==========================================
def generar_html(analisis):
    """
    Inyectamos nuestros datos analizados en una plantilla HTML 
    usando Jinja2 para visualizar los resultados e incluir gráficos.
    """
    template_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Coleccionista de Datos & Insights</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h1 { color: #2c3e50; text-align: center; }
            .badge { background: #3498db; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.9em; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
            .card { background: #eef2f5; border-left: 5px solid #3498db; padding: 15px; border-radius: 6px; }
            .chart-box { margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 Dashboard: Coleccionista de Datos Curiosos</h1>
            <p style="text-align: center;"><span class="badge">Actualizado con Python + API</span></p>

            <h2>💡 Insights & Datos Curiosos Extraídos</h2>
            <div class="grid">
                {% for fact in insights %}
                    <div class="card">
                        <p>{{ fact }}</p>
                    </div>
                {% endfor %}
            </div>

            <div class="chart-box">
                <h2>📊 Tendencia de Temperaturas</h2>
                <canvas id="weatherChart"></canvas>
            </div>
        </div>

        <script>
            // Pasamos las listas de Python a JavaScript para el gráfico
            const ctx = document.getElementById('weatherChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ fechas | tojson }},
                    datasets: [
                        { label: 'Temp Máxima (°C)', data: {{ temp_max | tojson }}, borderColor: '#e74c3c', fill: false, tension: 0.3 },
                        { label: 'Temp Mínima (°C)', data: {{ temp_min | tojson }}, borderColor: '#3498db', fill: false, tension: 0.3 }
                    ]
                }
            });
        </script>
    </body>
    </html>
    """
    
    # Renderizamos la plantilla con los datos
    template = Template(template_html)
    html_output = template.render(
        insights=analisis['insights'],
        fechas=analisis['fechas'],
        temp_max=analisis['temp_max'],
        temp_min=analisis['temp_min']
    )
    
    # Guardamos el resultado en un archivo index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("¡Página 'index.html' generada con éxito!")

# Execute
if __name__ == "__main__":
    datos = obtener_datos_api()
    resultado_analisis = analizar_datos(datos)
    generar_html(resultado_analisis)
