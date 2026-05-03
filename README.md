# Tesis

Repositorio LaTeX sincronizado con Overleaf y GitHub.

Repositorio remoto:

<https://github.com/JuanOrtiz97/Tesis>

## Estructura

- `main.tex`: archivo principal usado por Overleaf.
- `plantilla-main.tex`: plantilla base creada inicialmente para referencia.
- `capitulos/`: capitulos separados que puedes usar si decides modularizar la tesis.
- `anexos/`: anexos del documento.
- `Imagenes/`: imagenes usadas actualmente por `main.tex`.
- `figuras/`: carpeta alternativa para figuras nuevas.
- `referencias.bib`: bibliografia en formato BibTeX/BibLaTeX.

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
