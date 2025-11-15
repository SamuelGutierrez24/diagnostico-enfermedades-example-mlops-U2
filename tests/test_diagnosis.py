import sys
import os
import pytest
import json

# Agregar el directorio src al path para poder importar main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import simple_diagnosis, get_statistics, PREDICTIONS_LOG_FILE


class TestDiagnosisModel:
		
		def test_enfermedad_aguda_con_fiebre_alta_y_tos(self):
				temperatura = 38.5
				tos = 1
				duracion = 3
				
				resultado = simple_diagnosis(temperatura, tos, duracion)
				
				assert resultado == "ENFERMEDAD AGUDA", \
						f"Esperado: ENFERMEDAD AGUDA, Obtenido: {resultado}"
		
		def test_no_enfermo_con_parametros_normales(self):
				temperatura = 36.6
				tos = 0
				duracion = 0
				
				resultado = simple_diagnosis(temperatura, tos, duracion)
				
				assert resultado == "NO ENFERMO", \
						f"Esperado: NO ENFERMO, Obtenido: {resultado}"
		
		def test_enfermedad_cronica_con_duracion_larga(self):
				temperatura = 37.5
				tos = 1
				duracion = 35
				
				resultado = simple_diagnosis(temperatura, tos, duracion)
				
				assert resultado == "ENFERMEDAD CRÓNICA", \
						f"Esperado: ENFERMEDAD CRÓNICA, Obtenido: {resultado}"
		
		def test_enfermedad_terminal_con_fiebre_muy_alta_y_duracion_larga(self):
				temperatura = 40.5
				tos = 1
				duracion = 20
				
				resultado = simple_diagnosis(temperatura, tos, duracion)
				
				assert resultado == "ENFERMEDAD TERMINAL", \
						f"Esperado: ENFERMEDAD TERMINAL, Obtenido: {resultado}"
		
		def test_enfermedad_leve_con_sintomas_leves(self):
				temperatura = 37.5
				tos = 0
				duracion = 2
				
				resultado = simple_diagnosis(temperatura, tos, duracion)
				
				assert resultado == "ENFERMEDAD LEVE", \
						f"Esperado: ENFERMEDAD LEVE, Obtenido: {resultado}"


class TestStatistics:
		
		def setup_method(self):
				# Eliminar el archivo de log si existe
				if os.path.exists(PREDICTIONS_LOG_FILE):
						os.remove(PREDICTIONS_LOG_FILE)
		
		def teardown_method(self):
				# Eliminar el archivo de log si existe
				if os.path.exists(PREDICTIONS_LOG_FILE):
						os.remove(PREDICTIONS_LOG_FILE)
		
		def test_estadisticas_vacias_sin_predicciones(self):
				stats = get_statistics()
				
				# Verificar que el total de predicciones sea 0
				assert stats["total_predicciones"] == 0, \
						f"Esperado 0 predicciones, obtenido: {stats['total_predicciones']}"
				
				# Verificar que todas las categorías estén en 0
				for categoria, count in stats["predicciones_por_categoria"].items():
						assert count == 0, \
								f"Categoría {categoria} debería estar en 0, obtenido: {count}"
				
				# Verificar que la lista de últimas predicciones esté vacía
				assert len(stats["ultimas_5_predicciones"]) == 0, \
						f"La lista de predicciones debería estar vacía, tiene {len(stats['ultimas_5_predicciones'])} elementos"
				
				# Verificar que la fecha de última predicción sea None
				assert stats["fecha_ultima_prediccion"] is None, \
						f"La fecha de última predicción debería ser None, obtenido: {stats['fecha_ultima_prediccion']}"


if __name__ == "__main__":
		# Ejecutar los tests con pytest
		pytest.main([__file__, "-v"])
