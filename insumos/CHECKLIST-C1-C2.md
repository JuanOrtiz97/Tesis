# Lista de trabajo: C1 y C2

Base documental: capítulos 3 y 5 de la tesis. Entrega: lunes 14 de septiembre, 07:00. Estimaciones de trabajo, no garantía de duración de las simulaciones. Este archivo organiza tareas; no afirma que los escenarios ya estén ejecutados.

## Antes de ambos casos — 60–90 minutos

- [ ] Confirmar inventario y potencia del datacenter: el modelo conserva 500 W/m² y funcionamiento continuo. Reunir potencia, cantidad y horario de servidores, red y otros equipos; no asumir que un rack acredita esa carga.
- [ ] Confirmar si existe calefacción y justificar/corregir el día de dimensionamiento de invierno; resolver la incidencia psicrométrica.
- [ ] Revisar los pequeños encuentros geométricos, las dos aberturas horizontales AFN y las construcciones interzonales pendientes. Documentar cualquier advertencia aceptada y su efecto.
- [ ] Guardar el CB validado y una copia inalterable con fecha. Si cambia, regenerar las tablas y gráficas del capítulo 4 antes de comparar.
- [ ] Fijar clima TMYx 2011–2025, calendario 2025, UTC−6, ocupación, equipos, iluminación, consignas, eficiencias, paso de 10 minutos y salidas iguales.
- [ ] Definir criterio de confort y horario ocupado por zona. Las medias diarias del edificio no sirven para contar horas de confort.

Entregable: CB validado, registro de advertencias y tabla de parámetros comunes.

## C1 — Estrategias pasivas — 3–4 horas

### 1. Delimitar el paquete — 30–45 minutos
- [ ] Crear C1 como copia del CB validado, sin sobrescribirlo.
- [ ] Elegir las medidas que se evaluarán: protección solar exterior y ventilación natural son las familias ya definidas en la tesis.
- [ ] Preparar dimensiones y posición de aleros/celosías, fachadas afectadas y capturas del antes/después.
- [ ] Preparar áreas libres de aberturas/rejillas, horarios, control de apertura y recorrido del aire por el atrio y los pasillos. Conservar la cubierta y los cerramientos que corresponden al proyecto.
- [ ] Registrar cada parámetro CB → C1, unidad, zona/superficie y fundamento. No introducir mejoras simultáneas en materiales si se pretende separar el efecto de C2.
- [ ] Resolver la mención de “inercia térmica” de la metodología: si se modifican capas, densidad o calor específico, asignar ese cambio a C2 o declarar expresamente otra separación. No atribuirlo a dos casos.

### 2. Modelar y comprobar — 45–60 minutos
- [ ] Aplicar únicamente el paquete acordado. Mantener emplazamiento/orientación real; una rotación hipotética requeriría justificación explícita.
- [ ] Verificar conexiones de aire, superficies y sombras en las zonas intervenidas.
- [ ] Exportar el IDF de C1 y comparar parámetros con CB; comprobar que las cargas y condiciones comunes no cambiaron.

### 3. Simular y analizar — 60–90 minutos
- [ ] Ejecutar simulación anual; revisar errores severos y nuevas advertencias antes de usar resultados.
- [ ] Exportar las mismas 30 variables diarias y las series horarias por zona necesarias para confort y ventilación.
- [ ] Recalcular iluminación natural con el mismo cielo, malla y plano de trabajo del CB; comprobar el efecto del sombreado sobre el acceso a luz natural.
- [ ] Comparar demanda térmica sensible/total, electricidad estimada, temperaturas ocupadas y ventilación; no mezclar kWh térmicos y eléctricos.
- [ ] Calcular reducción por indicador: (CB − C1) / CB × 100. Si CB es cero, informar diferencia absoluta. Conservar resultados desfavorables si aparecen.

### 4. Documentar — 30–45 minutos
- [ ] Guardar modelo, IDF, CSV, registro de errores y tres vistas de las modificaciones.
- [ ] Crear tabla CB/C1 y gráficos con el estilo común; redactar qué mejora, qué empeora y por qué.

Entregable: C1 ejecutado, trazable y comparable; no basta la captura del modelo.

## C2 — Materiales sostenibles — 3–4 horas

### 1. Reunir y seleccionar alternativas — 45–60 minutos
- [ ] Crear C2 desde el mismo CB validado, no desde C1. La combinación se reserva para C3.
- [ ] Elegir las soluciones de muro/cubierta que realmente se van a sustituir y su alcance en m².
- [ ] Reunir ficha técnica de cada capa: espesor, conductividad, densidad, calor específico y propiedades ópticas pertinentes; datos de humedad si habrá evaluación higrotérmica.
- [ ] Reunir evidencia de carbono incorporado: declaración ambiental o fuente compatible, unidad declarada, etapas del ciclo de vida y vida útil. “Reciclado” o “local” por sí solo no cuantifica ahorro de CO₂.
- [ ] Registrar disponibilidad, transporte a Galápagos, mantenimiento y durabilidad con fuentes o declarar estos aspectos pendientes.
- [ ] Preparar una tabla de capas CB/C2. No reutilizar las propiedades del antiguo informe Ubakus: difieren del IDF actual.

### 2. Modelar y comprobar — 45–60 minutos
- [ ] Crear construcciones específicas de C2 y asignarlas a las superficies acordadas.
- [ ] Revisar orden exterior–interior, unidades y correspondencia de construcciones interzonales.
- [ ] Mantener la geometría, protecciones solares, aberturas y controles del CB para separar el efecto de materiales.
- [ ] Exportar y contrastar el IDF con CB; registrar exclusivamente los cambios de materialidad previstos.

### 3. Simular y comparar — 60–90 minutos
- [ ] Ejecutar simulación anual y revisar advertencias; exportar datos con igual periodo y resolución.
- [ ] Comparar energía y confort con CB y, en una columna independiente, con C1.
- [ ] Recalcular iluminación si cambian vidrios, transmitancia visible o reflectancias; conservar los mismos parámetros de cálculo lumínico.
- [ ] Calcular carbono incorporado con cantidades y fuentes homogéneas. No interpretar ahorro eléctrico como reducción de carbono incorporado.
- [ ] Si falta evidencia ambiental, presentar la comparación energética y dejar la afirmación de menor huella sin cuantificar.

### 4. Documentar — 30–45 minutos
- [ ] Guardar C2, IDF, exportaciones, fichas y tabla de sustituciones.
- [ ] Completar tabla CB/C1/C2 y gráficos comparativos; redactar ventajas, costes/logística documentados y limitaciones.

## Control de cierre
- [ ] Ningún resultado de CB se reutiliza como si fuera de C1 o C2.
- [ ] Todas las cifras tienen unidad, fuente, periodo y escenario identificado.
- [ ] Separar energía térmica, electricidad, confort y carbono incorporado.
- [ ] Compilar capítulo 5 y revisar figuras, referencias y conclusiones contra los datos.
- [ ] Preparar C3 solamente después de elegir y documentar los paquetes de C1 y C2.

Orden previsto: validación CB → C1 → C2 → comparación → C3. Reservar al menos 2 horas adicionales para integración y revisión del capítulo 5; el plazo restante también debe cubrir C3, conclusiones y entrega.
