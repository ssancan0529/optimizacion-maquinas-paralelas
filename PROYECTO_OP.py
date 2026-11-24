import pyodbc
import math
from pulp import (
    LpProblem, LpMinimize, LpVariable, lpSum,
    LpBinary, LpInteger, PULP_CBC_CMD, LpStatus
)

# ---- 1. CONEXIÓN A SQL SERVER
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=PROYECTO_PRUEBA;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
)
cursor = conexion.cursor()
# ---- 2. PARÁMETROS
parametros = {
    fila.nombre_parametro.lower(): fila.valor_parametro
    for fila in cursor.execute(
        "SELECT nombre_parametro, valor_parametro FROM dbo.Parametros"
    )
}

L = parametros["duracion_periodo"] #duracion del período
M = parametros["num_maquinas"] #número máximo de máquinas
T = parametros["horizonte"] #horizonte de planificación


# ---- 3. TRABAJOS
trabajos = {}
for fila in cursor.execute(
    "SELECT id_trabajo, tiempo_llegada, duracion, espera_maxima FROM dbo.Trabajos"
):
    trabajos[fila.id_trabajo] = {
        "a": fila.tiempo_llegada,
        "p": fila.duracion,
        "w": fila.espera_maxima
    }

conexion.close()


# ---- 4. CONJUNTO Q
Q = set()

for k in range(T // L + 1):
    Q.add(k * L)
##Se agregan todos los tiempos factibles de inicio y finalización de trabajos.
for info in trabajos.values():
    for s in range(info["a"], info["a"] + info["w"] + 1):
        f = s + info["p"]
        if f <= T:
            Q.add(s)    
            Q.add(f)

Q = sorted(Q)
Q_idx = {t: i for i, t in enumerate(Q)}
# ---- 5. ARCOS 
# Arcos de espera 
arcos_espera = [] #Disponibilidad de máquinas entre eventos consecutivos.
for i in range(len(Q) - 1):
    arcos_espera.append((i, i + 1, 0))
    
# Función para calcular el número de periodos que la máquina está ocupada o 
#calcula cuantos periodos toma una trabajo para realizarse
def machine_periods(inicio, fin):
    return math.floor((fin - 1) / L) - math.floor((inicio - 1) / L) + 1

# Arcos de trabajos (equivalente a arcos_2_trabajos)
#Cada arco representa ejecutar un trabajo en un intervalo factible.
arcos_trabajos = []
for j, info in trabajos.items():
    inicio_min = info["a"]          # arrival
    duracion = info["p"]            # processing time
    espera_max = info["w"]          # ventana máxima de inicio
    for s in range(inicio_min, inicio_min + espera_max + 1):
        f = s + duracion
        if f <= T:
            # costo = número de periodos que la máquina está ocupada
            costo = machine_periods(s, f)
            arcos_trabajos.append((Q_idx[s], Q_idx[f], j, costo))
# ---- 6. MODELO
modelo = LpProblem("DSM_Ejemplo_2_5", LpMinimize)
l = LpVariable.dicts(                #l es el flujo de máquinas
    "l",
    [(i, j) for i, j, _ in arcos_espera],
    0, M, LpInteger)

x = LpVariable.dicts(                #x es la seleccion de trabajos 
    "x",
    [(i, f, j) for i, f, j, _ in arcos_trabajos],
    cat=LpBinary)

# Variable de periodo activo
K = T // L
y = LpVariable.dicts("y", range(K), cat=LpBinary)   # y representa si un período
                                                    #se activa o no


# ---- 7. FUNCIÓN OBJETIVO
modelo += lpSum(
    c * x[(i, f, j)]
    for i, f, j, c in arcos_trabajos
)



# ---- 8. RESTRICCIONES
for n in range(len(Q)):
    entrada = (
        lpSum(l[(i, j)] for i, j, _ in arcos_espera if j == n) +
        lpSum(x[(i, f, j)] for i, f, j, _ in arcos_trabajos if f == n)
    )

    salida = (
        lpSum(l[(i, j)] for i, j, _ in arcos_espera if i == n) +
        lpSum(x[(i, f, j)] for i, f, j, _ in arcos_trabajos if i == n)
    )


    if n == 0:
        modelo += salida - entrada == M
    elif n == len(Q) - 1:
        modelo += entrada - salida == M
    else:
        modelo += salida - entrada == 0

for j in trabajos:
    modelo += lpSum(
        x[(i, f, j)]
        for i, f, j2, _ in arcos_trabajos
        if j2 == j
    ) == 1

for k in range(K):
    for i, j_node, _ in arcos_espera:
        if Q[i] >= k * L and Q[j_node] <= (k + 1) * L:
            modelo += l[(i, j_node)] <= M * y[k]


# ---- 9. HEURÍSTICA TIPO FEASIBILITY PUMP (FP-INSPIRED)

# 9.1 Relajar variables binarias
for var in x.values():
    var.cat = 'Continuous'

print("Resolviendo relajación LP...")
modelo.solve(PULP_CBC_CMD(msg=0))

# Guardar solución LP
x_lp = {k: v.value() for k, v in x.items()}

#Se calcula una solución entera inicial.
x_round = {}
for k, val in x_lp.items():
    x_round[k] = 1 if val >= 0.5 else 0

#Restaurar variables binarias y cargar solución inicial
for k, var in x.items():
    var.cat = LpBinary
    var.setInitialValue(x_round[k])

# ---- 10. RESOLUCIÓN FINAL DEL MIP

print("Resolviendo MIP con solución inicial heurística...")
modelo.solve(PULP_CBC_CMD(msg=0))


# ---- 10. OUTPUT DETALLADO
print("ESTADO:", LpStatus[modelo.status])
print("COSTO ÓPTIMO:", modelo.objective.value())

print("\nTrabajos programados:")
for (i, f, j, c) in arcos_trabajos:
    if x[(i, f, j)].value() == 1:
        print(
            f"Trabajo {j}: "
            f"inicio {Q[i]}, "
            f"fin {Q[f]}, "
            f"costo {c}"
        )