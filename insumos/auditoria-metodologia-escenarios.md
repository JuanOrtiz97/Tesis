# Auditoría de cumplimiento metodológico y definición de C3
Fecha: 12 de septiembre de 2026. Revisión documental y de auditorías existentes, sin cambios a la tesis ni al modelo.

## Definición operativa exacta de C3

C3 es la unión de los paquetes realmente simulados C1 revisión 01 y C2 revisión 01, sobre la misma línea base CB revisión de cargas/corrida 09. Puede construirse como copia separada del C1 vigente y aplicar exclusivamente el cambio C2; esto conserva independencia de archivo y ejecución. No sumar porcentajes de ahorro: ejecutar C3 y medir interacción.

1. C1: tres aleros locales de 0,50 m en ventanas exteriores de PB-OF-01, PB-OF-02 y PB-OF-03.
2. C1: fracción practicable 20 % en ventanas exteriores de esas oficinas y 1PA-OF-01, 1PA-OF-02 y 1PA-OF-03; ventilación natural con control por temperatura y modo mixto en las seis oficinas, intervalo exterior 20–26 °C, conservando consignas HVAC.
3. C2: en las mismas 15 superficies Roof/Outdoors (136,475369 m² brutos), acabado exterior de cubierta con absortancia solar 0,40 a 0,20. Conservar absortancia visible 0,40, emisividad 0,90, espesor 0,02 m, conductividad 1,3 W/(m K), densidad 2300 kg/m³ y calor específico 840 J/(kg K), además de todas las otras capas.
4. No añadir otras medidas: conservar orientación, atrio cubierto, conexiones interiores existentes, vidrios, cargas, ocupación y configuraciones comunes del CB. Mantener mismo clima, calendario, resolución y salidas.

Denominación científicamente sustentada actual: **C3, ensayo combinado de estrategias pasivas y acabado reflectante hipotético**. La denominación metodológica “materiales sostenibles” sigue siendo un objetivo no acreditado, no un resultado.

## Matriz de cumplimiento

| Requisito y evidencia de la tesis | Estado | Evidencia ejecutada / diferencia / pendiente |
|---|---|---|
| CB como diseño actual; cap03, sección Caso de estudio | Parcial | Modelo y corrida 09 trazables. Persisten supuestos datacenter, dimensionamiento invierno e incidencias AFN descritas en checklist. No confundir modelo consistente con validación física/calibración. |
| Clima y operación equivalentes, cap03:173–177 | Verificado parcialmente | Auditorías C1/C2 confirman cargas y condiciones comunes; anual 2025. Registrar hashes EPW y parámetros comunes en comparación final C3. |
| C1 estrategias pasivas, cap03:166 | Cumple alcance seleccionado | Protección solar y ventilación natural implementadas. “Como orientación…inercia…” es listado ejemplificativo, no obligación de modificar todas. Declarar orientación e inercia no intervenidas. El control mixto es parte del paquete ensayado, no ahorro atribuible exclusivamente al alero. |
| C2 materiales de bajo carbono, reciclados o menor huella; cap03:167 y cap05:73–75 | No acreditado | Se simula solo sensibilidad óptica de un acabado sin ficha comercial ni EPD. Menor enfriamiento no demuestra menor carbono incorporado, contenido reciclado, durabilidad o viabilidad insular. Discrepancia sustantiva que debe mantenerse visible. |
| C3 combinación pasivo/materiales, cap03:168; cap05:77–79 | Parcial, por ejecutar/verificar | La unión exacta permite evaluar interacción energética, pero hereda la carencia ambiental de C2. Aun si mejora energía, no acredita cumplimiento completo de materiales sostenibles. |
| Modelos independientes y comparables, cap03:173 | Cumple con salvedad | CB/C1/C2 tienen archivos y resultados propios. C2 no contiene C1. Importación cambia teselación; área de suelo del atrio 6,2248 a 6,2174 m² y volumen pasillo 27,848 a 27,8479 m³. Áreas agregadas equivalentes. Conservar salvedad y verificar C3 contra ambos. |
| Energía térmica y consumo estimado, cap03:177–189 | Parcial | CB 84.759,410853 y C2 84.328,848723 kWh térmicos/año según LEEME-C2. Reducción 0,507982 %. C1 reducción 1,95 % según cap05:25. No son electricidad medida. Separar sensible/latente/total y supuestos de conversión eléctrica. |
| Confort térmico, cap03:177–189; cap05:27–29 | Pendiente | Temperaturas/medias diarias no bastan. Fijar criterio, horario ocupado por zona, contar horas y reportar zonas críticas bajo el mismo criterio en cuatro escenarios. |
| Luminosidad, cap03:177–189 | Pendiente C1/C3 | Recalcular efecto de aleros con mismo cielo, malla y plano. C2 conserva propiedades visibles: no atribuir mejora lumínica a reducción de absortancia solar. La igualdad de vidrios no prueba igual iluminación tras sombreado C1. |
| Matriz de materiales/huella, cap03:128 | Pendiente | Cantidades y fichas, unidad declarada, etapas, vida útil y datos ambientales compatibles. No reutilizar propiedades antiguas Ubakus (checklist:52). |
| Validación/estándares, cap03:193–197 | Parcial | Revisión de consistencia y advertencias en proceso; 0 severos no significa ausencia de problemas. C1/C2 registran 318 advertencias. No se identifica en este capítulo un umbral normativo operativo de confort/luz para declarar cumplimiento. Comparación con mediciones es condicional a disponibilidad, no obligación de inventarlas. |
| Viabilidad técnica/económica, cap03:224; cap05:41–59,107 | Pendiente | Ficha de acabado, reflectancia envejecida, compatibilidad, disponibilidad, transporte, mantenimiento, costes y durabilidad. Documentar desconocidos. |
| Registro y comparación integral, cap03:189–191 | Parcial | CB/C1/C2 tienen archivos/resultados propios. Cap05 aún anuncia C2 pendiente: integración documental desactualizada respecto ejecución. Completar matriz CB/C1/C2/C3 con resultado nuevo C3. |

## Verificaciones concretas de cierre C3

- Guardar modelo, IDF, resultados y log propios con procedencia y hashes.
- Comparar C3 con C1: exclusivamente cambios de material/construcción C2; comparar C3 con C2: exclusivamente medidas C1 y cambios menores de exportación documentados.
- Confirmar tres sombras añadidas, seis controles mixtos 20–26 °C y fracciones 20 %; mismas cubiertas exteriores C2 y ninguna sustitución interzonal.
- Revisar errores severos, advertencias nuevas, convergencia y balances; conservar resultados desfavorables.
- Calcular ahorro de C3 frente a CB y diferencias frente C1 y C2. Interacción de ahorro: (CB−C3)−[(CB−C1)+(CB−C2)], misma unidad térmica y periodo; no asumir aditividad.
- Resolver confort e iluminación comparados antes de seleccionar “mejor desempeño”; energía por sí sola no cierra cap05.
- Si se revisan entradas comunes CB, repetir los cuatro escenarios antes de presentar ahorros definitivos.
- No cambiar retrospectivamente cap03 para hacer parecer cumplida la caracterización ambiental. Informar alcance ejecutado, desviación, limitación y trabajo pendiente.

## Fuentes leídas

Repositorio documental: C:/Users/juand/Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia:
- capitulos/03-metodologia.tex
- capitulos/05-discusion-optimizacion.tex
- insumos/CHECKLIST-C1-C2.md

Resultados/modelos: C:/Users/juand/Documents/New project 3/Tesis-limpia/output:
- C1-estrategias-pasivas/PROPUESTA-C1.md, cambios-C1-revision01.json, procedencia.json.
- C2-materiales/LEEME-C2.md, procedencia.json, cambios-C2-revision01.json y validacion-modelo.json/.md (auditoría IDF realizada en esta tarea).
