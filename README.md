# Tesis

Repositorio LaTeX sincronizado con Overleaf y GitHub.

Repositorio remoto:

<https://github.com/JuanOrtiz97/Tesis>

## Sincronizacion con Overleaf

Este repositorio debe mantenerse liviano para evitar fallos al actualizar con Overleaf. Overleaf recomienda que los proyectos con GitHub Sync o Git integration se mantengan por debajo de 100 MB.

Los PDFs de lectura, documentos Word originales y otros binarios pesados se conservan localmente como insumos de trabajo, pero no se versionan. El documento compilable debe depender solo de `main.tex`, `capitulos/`, `anexos/`, `referencias.bib`, `bibliografia/`, `Imagenes/`, `figuras/` y las tablas `.tex` dentro de `insumos/`.

La sincronizacion directa de Overleaf con GitHub no es automatica: se ejecuta desde el menu de GitHub dentro de Overleaf. Para actualizar Overleaf automaticamente desde esta computadora, configura el remoto Git de Overleaf:

```powershell
git remote add overleaf https://git.overleaf.com/ID_DEL_PROYECTO
```

Luego usa:

```powershell
.\scripts\sincronizar-overleaf.ps1 -Mensaje "Actualizar tesis"
```

El script hace commit, envia a GitHub y, si existe el remoto `overleaf`, envia la rama actual a `master`, que es la rama usada por Overleaf.

## Estructura

- `main.tex`: archivo principal usado por Overleaf.
- `normativas/`: resumen operativo `normas-apa-uda.md` para futuros trabajos.
- `insumos/`: documentos fuente que se revisan antes de integrarlos al texto de la tesis.
- `plantilla-main.tex`: plantilla base creada inicialmente para referencia.
- `capitulos/`: capitulos separados que puedes usar si decides modularizar la tesis.
- `anexos/`: anexos del documento.
- `Imagenes/`: imagenes usadas actualmente por `main.tex`.
- `figuras/`: carpeta alternativa para figuras nuevas.
- `referencias.bib`: bibliografia manual en formato BibTeX/BibLaTeX.
- `bibliografia/Maestria.bib`: bibliografia exportada desde Zotero con Better BibTeX.
- `scripts/actualizar-bibliografia.ps1`: actualiza `bibliografia/Maestria.bib` desde Zotero local.

## Flujo recomendado

1. Edita en Overleaf o localmente.
2. Si editas en Overleaf, usa `Push Overleaf changes to GitHub`.
3. Si editas localmente, ejecuta:

```powershell
git pull
git add .
git commit -m "Actualizar tesis"
git push
```

## Compilacion recomendada

Usa `pdfLaTeX` con `Biber` para la bibliografia.

## Zotero y Better BibTeX

Para actualizar la bibliografia desde Zotero, abre Zotero en esta computadora y ejecuta:

```powershell
.\scripts\actualizar-bibliografia.ps1
```

El script descarga la coleccion `Maestria` desde Better BibTeX y elimina los campos `file` y `abstract` antes de guardar el archivo, para evitar subir rutas locales y textos largos innecesarios.

## Normas de formato

El archivo `main.tex` esta configurado para seguir las indicaciones de `normativas/Normas Apa UDA.docx`: papel A4, Times, margenes institucionales, portada UDA, numeracion preliminar romana, capitulos numerados, interlineado y referencias APA con `biblatex`.
