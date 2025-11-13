from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)


def simple_diagnosis(temperature: float, cough: int, duration_days: int) -> str:
		try:
				t = float(temperature)
				c = int(bool(int(cough)))
				d = int(duration_days)
		except Exception:
				raise ValueError("Parámetros inválidos. temperature(float), cough(0/1), duration_days(int) son requeridos.")

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

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

