USE PROYECTO_PRUEBA;
GO

/* TABLA DE PARÁMETROS DEL MODELO DSM */
IF OBJECT_ID('dbo.Parametros', 'U') IS NOT NULL
    DROP TABLE dbo.Parametros;
GO
CREATE TABLE dbo.Parametros (
    nombre_parametro VARCHAR(50) PRIMARY KEY,
    valor_parametro INT NOT NULL
);
GO

/* TABLA DE TRABAJOS */
IF OBJECT_ID('dbo.Trabajos', 'U') IS NOT NULL
    DROP TABLE dbo.Trabajos;
GO
CREATE TABLE dbo.Trabajos (
    id_trabajo INT PRIMARY KEY,
    tiempo_llegada INT NOT NULL,   -- a_i
    duracion INT NOT NULL,         -- p_i
    espera_maxima INT NOT NULL     -- w_i
);
GO

/* PARÁMETROS DEL EJERCICIO 2.5 (PAPER)
   3 máquinas; L = 7; T = 14 (2 períodos) */
INSERT INTO dbo.Parametros (nombre_parametro, valor_parametro)
VALUES
('duracion_periodo', 7),
('num_maquinas', 3),
('horizonte', 14);
GO

/* TRABAJOS DEL EJERCICIO 2.5 */
INSERT INTO dbo.Trabajos (id_trabajo, tiempo_llegada, duracion, espera_maxima)
VALUES
(1, 1, 5, 1),
(2, 4, 6, 1);
GO
SELECT * FROM dbo.Parametros;
SELECT * FROM dbo.Trabajos;
GO
