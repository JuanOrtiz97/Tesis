# Interpretación del IDF del caso base

Fuente local: `datos/proyecto-caso-base-1-3.idf`

Archivo original: `C:/Users/juand/Desktop/EnergyPlus_IDF/PROYECTO CASO BASE 1.3.idf`

## Identificación del modelo

| Campo | Valor |
|---|---:|
| Software de origen | DesignBuilder 7.3.1.003 |
| Motor de simulación | EnergyPlus 9.4.0.002 |
| Archivo fuente DesignBuilder | `Defensoria del Pueblo.dsb` |
| Nombre del edificio | Defensoria del Pueblo |
| Convención geométrica | Medidas exteriores |
| Archivo climático indicado | `ECU_GA_San.Cristobal.Intl.AP.840080_TMYx.2011-2025.epw` |
| Zonas térmicas totales | 28 |
| Zonas con cargas/HVAC ideal | 19 |
| Superficies constructivas detalladas | 320 |
| Superficies de sombreado | 204 |
| Superficies de fenestración | 102 |

## Configuración climática y de simulación

El IDF indica una simulación anual para San Cristóbal, con inicio el 1 de enero y fin el 31 de diciembre. El comentario del archivo señala como clima horario el EPW TMYx 2011-2025 de San Cristóbal.

Puntos a revisar antes de correr resultados finales:

- El `RunPeriod` está rotulado con el año 2002, aunque el EPW corresponde a un TMYx 2011-2025.
- El `Site:Location` del IDF usa zona horaria -5 y elevación 9,8 m, mientras que el encabezado del EPW revisado indica zona horaria -6 y elevación 18,9 m.
- Las temperaturas de terreno `BuildingSurface`, `Deep` y `Shallow` aparecen simplificadas como 18 °C y 14 °C en varios objetos, mientras que el EPW contiene temperaturas de terreno mensuales calculadas.

Estos puntos no invalidan el modelo como caso base, pero conviene corregirlos o documentarlos para que la simulación sea coherente con el archivo climático final.

## Geometría y envolvente

| Indicador | Valor |
|---|---:|
| Área de pisos modelada | 378,17 m2 |
| Área de muros neta | 1399,33 m2 |
| Área de cubierta | 136,48 m2 |
| Área de cielos/entrepisos | 241,70 m2 |
| Área de superficies hacia exterior | 650,15 m2 |
| Área de superficies hacia terreno | 126,00 m2 |
| Área de superficies adiabáticas/interiores | 1379,53 m2 |

La mayor parte del modelo está compuesta por muros interiores o particiones entre zonas. Las superficies expuestas al exterior suman 650,15 m2, por lo que la evaluación energética debe concentrarse en muros exteriores, cubierta, vanos y control solar.

## Fenestración

| Indicador | Valor |
|---|---:|
| Área total de ventanas | 337,25 m2 |
| Área total de puertas/aberturas | 191,92 m2 |
| Área de fenestración exterior | 108,75 m2 |
| Relación aproximada ventana-muro exterior | 17,77 % |

Las superficies exteriores de fenestración se concentran principalmente hacia NE y SO:

| Orientación aproximada | Área |
|---|---:|
| NE | 46,54 m2 |
| SO | 54,24 m2 |
| SE | 7,97 m2 |

Esta distribución permite formular hipótesis de análisis para el caso base: el desempeño térmico estará condicionado por la radiación recibida en vanos exteriores, el control solar disponible y la relación entre orientación, ventilación natural y cargas internas.

## Materiales y construcciones relevantes

El modelo contiene 35 construcciones, 21 materiales de masa, 9 materiales sin masa y capas de vidrio/gas. Las construcciones más representativas por área son:

- Muros con enlucido, bloque de 15 cm y empaste/yeso.
- Tabiques de gypsum, bloque de 15 cm y gypsum.
- Entrepisos con porcelanato, cámara de aire y gypsum.
- Piso con porcelanato de 2 cm y hormigón de 15 cm.
- Cubierta metálica con aluminio de 0,4 mm, aislante PUR de 50 mm y aluminio de 0,4 mm.
- Muros con ladrillo de 14 cm, aislante de 2 cm y panel de gypsum de 2 cm.
- Vidrios de 6 mm y 8 mm.

Estas capas deben revisarse con fichas técnicas reales del proyecto, porque los valores de conductividad, densidad, calor específico y espesores determinan el comportamiento térmico de la línea base.

## Cargas internas y operación

El modelo incluye cargas de ocupación, iluminación y equipos para 19 zonas. Los horarios principales son:

- `8:00 - 18:00 Mon - Sat` para oficinas y varios espacios administrativos.
- `10:00 - 12:00 Lunes-Viernes` para baños.
- `Horario Circulacion` para pasillos.
- `On 24/7` en una zona técnica o de datos.

Valores representativos:

- Ocupación por área: 0,10 a 0,20 personas/m2 en oficinas y recepción; 0,50 personas/m2 en cafetería; 0,11 personas/m2 en baños y circulación.
- Iluminación: 10 a 25 W/m2 según tipo de espacio.
- Equipos: 3 a 7,5 W/m2 en oficinas, 15 W/m2 para carga de catering en cafetería, y una carga alta de 500 W/m2 en la zona `PRIMERAPLANTAALTA:1PAXDC`, que debe revisarse porque puede dominar el consumo.

## Ventilación, infiltración y HVAC

No se identificaron objetos explícitos `ZoneInfiltration:DesignFlowRate` ni `ZoneVentilation:DesignFlowRate`. En cambio, el modelo usa:

- `AirflowNetwork:SimulationControl`: modelo multizona sin distribución.
- 28 zonas en AirflowNetwork.
- 235 superficies en AirflowNetwork.
- 52 componentes de apertura detallada.
- 7 objetos `DesignSpecification:OutdoorAir` con 1,5 renovaciones/hora para algunas zonas.
- 19 sistemas `ZoneHVAC:IdealLoadsAirSystem`.

Esto indica que el caso base trabaja con flujo de aire multizona y sistemas ideales de carga térmica. Es adecuado para estimar demanda de calefacción/enfriamiento y comparar escenarios, pero no representa un sistema HVAC real con equipos, eficiencias y consumos específicos.

## Lectura metodológica

El IDF funciona como línea base de simulación del edificio. Permite evaluar el comportamiento térmico de la geometría, envolvente, horarios, cargas internas y ventilación modelada. Para que sirva como base sólida de comparación, se recomienda:

1. Corregir o justificar la diferencia entre el EPW TMYx 2011-2025 y el año 2002 indicado en el `RunPeriod`.
2. Alinear zona horaria y elevación del `Site:Location` con el encabezado del EPW.
3. Revisar la carga de equipos de `PRIMERAPLANTAALTA:1PAXDC`, porque 500 W/m2 es extremadamente alta para una zona administrativa convencional.
4. Confirmar si las ventanas exteriores y protecciones solares están modeladas de forma completa.
5. Documentar que el HVAC es ideal loads y que los resultados representan demanda térmica, no necesariamente consumo real de equipos.
6. Usar este IDF como escenario base y duplicarlo para los escenarios pasivo, material y combinado.

