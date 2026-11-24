# Optimización de máquinas paralelas

Proyecto académico colaborativo de Optimización Combinatoria (ESPOL).

## Objetivo
Programar trabajos no interrumpibles en máquinas paralelas, minimizando la suma de períodos de ocupación. El modelo utiliza arcos de espera y de trabajo, conservación de flujo y asignación única de cada trabajo, con restricciones de llegada, espera máxima y horizonte.

## Metodología
Python, PuLP, CBC y SQL Server. El código incluye relajación de variables y redondeo inspirado en Feasibility Pump; no implementa el algoritmo iterativo completo. La eficacia del arranque heurístico no ha sido verificada.

## Ejecución
1. Instalar Python, SQL Server Express y ODBC Driver 18.
2. Ejecutar `pip install -r requirements.txt`.
3. Preparar la base PROYECTO_PRUEBA con las tablas Parametros y Trabajos según el código; revisar la conexión local.
4. Ejecutar `python PROYECTO_OP.py`.

El programa muestra estado del solver, objetivo y trabajos programados. No se adjuntan resultados verificados de ejecución.
