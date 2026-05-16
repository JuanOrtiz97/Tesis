# PDFs del marco teórico

Esta carpeta guarda copias locales de los PDFs de acceso abierto citados en el capítulo 2 de la tesis.

- `manifest-pdfs-marco-teorico.csv` registra todas las referencias citadas en el marco teórico, el estado de descarga, el DOI, la URL fuente y la URL del PDF cuando fue posible descargarlo.
- Los archivos `.pdf` incluidos corresponden únicamente a documentos detectados como PDF real y descargados desde fuentes abiertas o editoriales.
- Las referencias con estado distinto a `descargado` no se guardaron porque el sitio bloqueó la descarga automática, no se detectó PDF abierto o la referencia no tenía URL/DOI suficiente.

El script que genera esta carpeta es `scripts/descargar-pdfs-marco-teorico.py`.
