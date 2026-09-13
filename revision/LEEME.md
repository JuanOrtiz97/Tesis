# Revisión de las 64 observaciones

Se conserva el título aprobado. El registro observaciones.csv contiene 64 entradas: 53 atendidas o verificadas y 11 parciales o pendientes de evidencia. Las correcciones propuestas por el informe se contrastaron con las fuentes; verificar una cifra correcta no exige cambiarla.

## Cambios integrados

- Figuras 1.3 a 1.7 unificadas con el lenguaje gráfico de 1.2; título de objetivos sin marcador circular.
- Tres nuevas ilustraciones técnicas en el marco teórico, además de los esquemas existentes.
- Croquis de ubicación y tres láminas arquitectónicas obtenidas del modelo Revit disponible; no se presentan como planos aprobados ni georreferenciados.
- Reorganización del texto y eliminación de saltos evitables: PDF de 129 páginas, sin páginas vacías ni referencias pendientes.
- Confort PMV/PPD de seis oficinas en cinco casos, con 3130 horas de análisis por oficina y supuestos explícitos; aperturas geométricas verificadas sin equipararlas a caudales reales.
- Sensibilidad de carga del datacenter: 150, 300 y 500 W/m²; mejora térmica relativa de C3 de 31,84 %, 27,04 % y 22,41 %. Son hipótesis, no inventario medido.

## Trazabilidad de simulación

Se preservaron los archivos originales de DesignBuilder y las cinco corridas principales. Los nuevos ensayos usaron EnergyPlus 9.4 sobre copias IDF aisladas. Dos controles reprodujeron exactamente las demandas originales de CB y C3; se aceptaron cuatro sensibilidades adicionales sin errores severos. Persisten 318 advertencias en CB y 324 en C3.

Se excluyeron un ensayo C3-150 sin convergencia con 100 días máximos de inicialización y un archivo ESO CB-300 incompleto. C3-150 se repitió ampliando el máximo a 500 días, sin relajar tolerancias; CB-300 se repitió con entrada idéntica. Los seis resultados aceptados y sus hashes se registran en sensibilidad-datacenter.json. Los CSV resumidos están en datos/ y los procedimientos en scripts/revision/. Las rutas de entrada corresponden a esta estación de trabajo; los grandes archivos ESO permanecen en el directorio de resultados externo.

## Límites y pendientes

- **INC-11 — Parcial**: Plantas A02/A03 incorporadas y programa visible. Falta conciliar nombres, límites y áreas BIM-BES y confirmar juego definitivo.
- **GAP-01 — Pendiente de evidencia**: Productos, cantidades y declaraciones ambientales para ACV y emisiones.
- **GAP-02 — Parcial avanzado**: Dos controles reproducen originales; cuatro sensibilidades aceptadas a 150/300 W/m², cero severos. Ahorro C3: 31,84/27,04/22,41% a 150/300/500. Inventario real pendiente.
- **GAP-03 — Parcial**: A01, A02 y A03 exportadas de Revit e incorporadas. Fachadas A04, cortes A05 y coordinación definitiva pendientes; Revit minimizado impidió continuar la exportación.
- **GAP-04 — Parcial**: EUI sobre 281,6308 m² explícitos IDF; no se denomina SRE sin verificación normativa.
- **GAP-07 — Parcial avanzado**: U, SHGC, VT y WWR documentados; se explicita discrepancia de soluciones A01 frente a IDF. Conciliar capas, productos y propiedades del conjunto con marcos.
- **GAP-08 — Parcial avanzado**: PMV/PPD de seis oficinas en cinco corridas: 3.130 horas por oficina. Supuestos de actividad, ropa y aire verificados. Falta separar regímenes y cubrir todos los espacios regulares para WELL.
- **GAP-09 — Pendiente de verificación y exportación**: Se intentó cálculo puntual/anual en C3. La exportación pierde foco y no guarda CSV; no se incorporan cifras sin archivo y trazabilidad. Falta comparación lumínica CB-C1-C3 validada.
- **GAP-11 — Parcial avanzado**: CSV con capacidad geométrica de apertura de seis oficinas en cinco casos y tabla C3. Falta área neta de producto, operación real y caudales; ventilación diurna no acredita criterio nocturno P01.
- **GAP-15 — Parcial**: Retirado mapa de IA con límite supuesto. Figura 1.1 usa croquis A01 de Revit con calles y predio identificados; no se presenta como cartografía georreferenciada ni escala métrica.
- **REF-04 — Parcial**: Identificada ASHRAE 55-2013 en WELL v2 Q4 2020. ASHRAE 62.1 se conserva como referencia condicional de Minergie, sin tasas ni comprobación normativa propia.

El área energética 281,6308 m² no se presenta como SRE certificada. La energía eléctrica se estima con COP constantes. La matriz no constituye certificación Minergie, WELL, CEELA, EDGE o LEED.
