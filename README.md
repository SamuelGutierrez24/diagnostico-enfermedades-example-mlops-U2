# Servicio de diagnóstico

## Propósito del repositorio

Este repositorio implementa un **servicio de diagnóstico médico** basado en reglas determinísticas para propósitos educativos y de demostración. El objetivo principal es proporcionar una aplicación web simple (construida con Flask) que permita a un médico o usuario final ingresar parámetros clínicos básicos (temperatura, presencia de tos, duración de síntomas) y obtener una clasificación de estado de salud:

- `NO ENFERMO`
- `ENFERMEDAD LEVE`
- `ENFERMEDAD AGUDA`
- `ENFERMEDAD CRÓNICA`
- `ENFERMEDAD TERMINAL`

**Nota importante**: No hay entrenamiento de modelos de Machine Learning reales en este proyecto. La función `simple_diagnosis` es una implementación demostrativa con reglas fijas, diseñada para satisfacer los requerimientos del taller universitario.

---

## Estructura del repositorio

El repositorio está organizado en dos componentes principales:

### 📁 `docs/`
Contiene la documentación técnica del proyecto:
- **`Pipeline Description.md`**: Descripción detallada de la pipeline de ML propuesta para diagnóstico de enfermedades (comunes y huérfanas). Incluye fases conceptuales, diseño de arquitectura, componentes (ingesta, ETL, feature store, entrenamiento, validación, despliegue, monitoreo), modelos candidatos, métricas de evaluación y estrategia de MLOps. Este documento sirve como referencia conceptual para el desarrollo futuro del sistema completo.

### 📁 `src/`
Contiene el código fuente de la aplicación:
- **`main.py`**: Aplicación Flask que implementa:
  - La función `simple_diagnosis(temperature, cough, duration_days)` con lógica determinística.
  - Endpoint web (`/`) con formulario HTML para entrada de datos.
  - Endpoint API REST (`/api/predict`) que recibe y devuelve JSON.

### Archivos adicionales
- **`Dockerfile`**: Configuración para construir la imagen Docker del servicio (usa `gunicorn` como servidor WSGI en Linux).
- **`requirements.txt`**: Dependencias de Python (Flask, gunicorn).
- **`.gitignore`**: Exclusión de archivos temporales, entornos virtuales, etc.

---

## Arquitectura de branching

El repositorio sigue una estrategia de branching basada en funcionalidades:

- **`main`**: Rama principal que representa el entorno de **"producción"** o versión estable y completa del proyecto. Todo el código en `main` está probado y listo para ser usado.
- **Ramas de feature**: Para cada nueva funcionalidad o mejora se crea una rama independiente (por ejemplo, `feature/api-diagnostico`, `feature/ui-mejoras`). Una vez completada y validada, la funcionalidad se integra a `main` mediante pull request.

Esta estrategia permite:
- Desarrollo paralelo de múltiples características.
- Revisión de código antes de integrar cambios críticos.
- Mantener `main` siempre en estado funcional.

---

## Documentación de la función

Inputs (requeridos):

- `temperature` (float) — temperatura corporal en °C.
- `cough` (0|1) — indicador de tos (0 = no, 1 = sí).
- `duration_days` (int) — número de días con síntomas.

Output: cadena con uno de los cuatro estados enumerados arriba.

Errores: si faltan campos o son inválidos, el endpoint devuelve HTTP 400 con `{"error": "..."}`.

---

## Endpoints

- UI web: `GET /` — formulario para ingresar los 3 parámetros y ver el resultado.
- API JSON: `POST /api/predict` — espera JSON con los campos `temperature`, `cough`, `duration_days`.

Ejemplo request JSON:

```json
{"temperature": 38.5, "cough": 1, "duration_days": 3}
```

Ejemplo response:

```json
{"prediction": "ENFERMEDAD AGUDA", "inputs": {"temperature":38.5,"cough":1,"duration_days":3}}
```

---

## Ejecutación con Docker

Estos pasos asumen que tienes Docker instalado y corriendo en tu máquina.

1) Construir la imagen (desde la raíz del repo donde están `Dockerfile` y `requirements.txt`):

```powershell
docker build -t mlops-diagnosis:latest .
```

2) Ejecutar el contenedor (mapear puerto 5000):

Ejecución en segundo plano:
```powershell
docker run -d --name mlops-diagnosis -p 5000:5000 mlops-diagnosis:latest
```
Ejecutar el contenedor en primer plano (verás logs en la consola)
 ```powershell
docker run --rm -p 5000:5000 mlops-diagnosis:latest
```

3) Abrir la UI en el navegador: `http://localhost:5000/`.

4) Probar la API (ejemplo PowerShell / curl):

PowerShell:
```powershell
$body = @{ temperature = 38.5; cough = 1; duration_days = 3 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/predict -Body $body -ContentType 'application/json'
```

curl (bash):
```bash
curl -X POST http://localhost:5000/api/predict -H "Content-Type: application/json" -d '{"temperature":38.5,"cough":1,"duration_days":3}'
```

---

## Notas
- Si modificas el código y quieres probar los cambios en la imagen, reconstruye:

```powershell
docker build -t mlops-diagnosis:latest .
```
- Si quieres detener el contenedor ejecutando el proyecto (si esta en segundo plano):
```powershell
docker stop mlops-diagnosis.
```

---

## Desarrollo rápido sin Docker

1. Crear y activar virtualenv (ubicado desde la carpeta fuente del proyecto):

```bash
python -m venv .venv
source .venv/bin/activate   # bash/WSL/macOS
# o en PowerShell: .\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar en modo dev:

```bash
cd src
python main.py
```

---

## Pruebas sugeridas

Para que pruebes diferentes resultados aqui hay 4 diferentes consultas que puedes hacer:

* Inputs: {"Temperatura": 38.5, "Tos": 1, "Duración de sintomas": 3}

    Respuesta esperada: ENFERMEDAD AGUDA
    
* Inputs: {"Temperatura": 36.6, "Tos": 0, "Duración de sintomas": 0}

    Respuesta esperada: NO ENFERMO

* Inputs: {"Temperatura": 39, "Tos": 1, "Duración de sintomas": 30}

    Respuesta esperada: ENFERMEDAD CRÓNICA
* Inputs: {"Temperatura": 36.6, "Tos": 1, "Duración de sintomas": 15}

    Respuesta esperada: ENFERMEDAD LEVE


---
