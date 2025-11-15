from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime
from threading import Lock

app = Flask(__name__)

PREDICTIONS_LOG_FILE = 'predictions_log.json'
log_lock = Lock()


def log_prediction(temperature: float, cough: int, duration_days: int, prediction: str):
		"""Registra una predicción en el archivo de log."""
		prediction_entry = {
				"fecha_hora": datetime.now().isoformat(),
				"datos_de_entrada": {
						"temperatura": float(temperature),
						"tos": int(cough),
						"duracion_dias": int(duration_days)
				},
				"prediccion": prediction
		}
		
		with log_lock:
				
				if os.path.exists(PREDICTIONS_LOG_FILE):
						try:
								with open(PREDICTIONS_LOG_FILE, 'r', encoding='utf-8') as f:
										predictions = json.load(f)
						except (json.JSONDecodeError, IOError):
								predictions = []
				else:
						predictions = []
				
				
				predictions.append(prediction_entry)
				
				
				try:
						with open(PREDICTIONS_LOG_FILE, 'w', encoding='utf-8') as f:
								json.dump(predictions, f, ensure_ascii=False, indent=2)
				except IOError as e:
						print(f"Error al guardar predicción: {e}")


def get_statistics():
		"""Obtiene las estadísticas de las predicciones realizadas."""
		if not os.path.exists(PREDICTIONS_LOG_FILE):
				return {
						"total_predicciones": 0,
						"predicciones_por_categoria": {
								"NO ENFERMO": 0,
								"ENFERMEDAD LEVE": 0,
								"ENFERMEDAD AGUDA": 0,
								"ENFERMEDAD CRÓNICA": 0,
								"ENFERMEDAD TERMINAL": 0
						},
						"ultimas_5_predicciones": [],
						"fecha_ultima_prediccion": None
				}
		
		with log_lock:
				try:
						with open(PREDICTIONS_LOG_FILE, 'r', encoding='utf-8') as f:
								predictions = json.load(f)
				except (json.JSONDecodeError, IOError):
						predictions = []
		
		if not predictions:
				return {
						"total_predicciones": 0,
						"predicciones_por_categoria": {
								"NO ENFERMO": 0,
								"ENFERMEDAD LEVE": 0,
								"ENFERMEDAD AGUDA": 0,
								"ENFERMEDAD CRÓNICA": 0,
								"ENFERMEDAD TERMINAL": 0
						},
						"ultimas_5_predicciones": [],
						"fecha_ultima_prediccion": None
				}
		
		
		category_counts = {
				"NO ENFERMO": 0,
				"ENFERMEDAD LEVE": 0,
				"ENFERMEDAD AGUDA": 0,
				"ENFERMEDAD CRÓNICA": 0,
				"ENFERMEDAD TERMINAL": 0
		}
		
		for pred in predictions:
				category = pred.get("prediccion", "")
				if category in category_counts:
						category_counts[category] += 1
		
		
		last_5 = predictions[-5:] if len(predictions) >= 5 else predictions
		last_5.reverse()
		
		
		last_date = predictions[-1]["fecha_hora"] if predictions else None
		
		return {
				"total_predicciones": len(predictions),
				"predicciones_por_categoria": category_counts,
				"ultimas_5_predicciones": last_5,
				"fecha_ultima_prediccion": last_date
		}


def simple_diagnosis(temperature: float, cough: int, duration_days: int) -> str:
		try:
				t = float(temperature)
				c = int(bool(int(cough)))
				d = int(duration_days)
		except Exception:
				raise ValueError("Parámetros inválidos. temperature(float), cough(0/1), duration_days(int) son requeridos.")

		if (t >= 40.0 and d >= 14) or (t >= 39.5 and c == 1 and d >= 21) or (d >= 60):
				return "ENFERMEDAD TERMINAL"

		if d >= 30:
				return "ENFERMEDAD CRÓNICA"

		if t >= 39.0 or (t >= 38.0 and c == 1 and d <= 14):
				return "ENFERMEDAD AGUDA"

		if (t >= 37.0 and t < 38.0) or (c == 1 and d <= 7) or (5 <= d < 30):
				return "ENFERMEDAD LEVE"
		return "NO ENFERMO"


INDEX_HTML = """
<!doctype html>
<html lang="es">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>Demo diagnóstico</title>
		<style>
			body { font-family: Arial, sans-serif; max-width: 640px; margin: 2rem auto; }
			label { display:block; margin-top:0.5rem }
			input[type=text], input[type=number] { width:100%; padding:8px }
			button { margin-top:1rem; padding:10px 16px }
			.result { margin-top:1rem; padding:12px; border-radius:6px; background:#f3f3f3 }
			.export-section { margin-top:2rem; padding:16px; border-radius:8px; border:1px solid #b3d9e6 }
			.export-btn {color:white; border:none; cursor:pointer; border-radius:4px }
			.export-btn:hover { background:#0052a3 }
		</style>
	</head>
	<body>
		<h2>Servicio demo: diagnóstico (reglas simples)</h2>
		<p>Ingrese al menos los 3 parámetros requeridos: temperatura (°C), tos (0/1) y duración (días).</p>
		<form method="post" action="/predict">
			<label>Temperatura (°C)
				<input name="temperature" type="text" value="36.6" required />
			</label>
			<label>Tos (0 = no, 1 = sí)
				<input name="cough" type="number" min="0" max="1" value="0" required />
			</label>
			<label>Duración de síntomas (días)
				<input name="duration_days" type="number" min="0" value="0" required />
			</label>
			<button type="submit">Consultar</button>
		</form>

		{% if result %}
			<div class="result">
				<strong>Resultado:</strong> {{ result }}<br/>
				<em>Reglas aplicadas</em>: temperatura={{ temperature }}, tos={{ cough }}, duración={{ duration_days }} días
			</div>
		{% endif %}
		
		<div class="export-section">
			<h3>Estadísticas de Predicciones</h3>
			<p>Descargue un reporte con las estadísticas de todas las predicciones realizadas.</p>
			<a href="/export/stats" download="estadisticas_predicciones.json">
				<button class="export-btn">Descargar Estadísticas (JSON)</button>
			</a>
		</div>
		<hr />
	</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
		return render_template_string(INDEX_HTML)


@app.route('/predict', methods=['POST'])
def predict_form():
		# Obtener desde form
		temperature = request.form.get('temperature')
		cough = request.form.get('cough')
		duration = request.form.get('duration_days')
		try:
				result = simple_diagnosis(temperature, cough, duration)
				log_prediction(temperature, cough, duration, result)
		except ValueError as e:
				return render_template_string(INDEX_HTML, result=str(e), temperature=temperature, cough=cough, duration_days=duration), 400

		return render_template_string(INDEX_HTML, result=result, temperature=temperature, cough=cough, duration_days=duration)


@app.route('/api/predict', methods=['POST']) 
def predict_api():
		if not request.is_json:
				return jsonify({"error": "Se requiere JSON en el body"}), 400

		data = request.get_json()
		for field in ('temperature', 'cough', 'duration_days'):
				if field not in data:
						return jsonify({"error": f"Falta campo requerido: {field}"}), 400

		try:
				prediction = simple_diagnosis(data['temperature'], data['cough'], data['duration_days'])
				log_prediction(
						float(data['temperature']),
						int(bool(int(data['cough']))),
						int(data['duration_days']),
						prediction
				)
		except ValueError as e:
				return jsonify({"error": str(e)}), 400

		return jsonify({
				"prediction": prediction,
				"inputs": {
						"temperature": float(data['temperature']),
						"cough": int(bool(int(data['cough']))),
						"duration_days": int(data['duration_days'])
				}
		})


@app.route('/api/stats', methods=['GET'])
def get_stats():
		"""Endpoint para obtener estadísticas de las predicciones."""
		stats = get_statistics()
		return jsonify(stats)


@app.route('/export/stats', methods=['GET'])
def export_stats():
		"""Endpoint para exportar estadísticas como archivo JSON descargable."""
		from flask import Response
		
		stats = get_statistics()
		stats_json = json.dumps(stats, ensure_ascii=False, indent=2)
		
		return Response(
				stats_json,
				mimetype='application/json',
				headers={'Content-Disposition': 'attachment; filename=estadisticas_predicciones.json'}
		)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

