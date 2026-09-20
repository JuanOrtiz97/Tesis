#target indesign

(function () {
    var sourcePdf = File("C:/Users/juand/Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia/piloto3.pdf");
    var outputFolder = Folder("C:/Users/juand/Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia/entregables/piloto3-indesign");
    if (!sourcePdf.exists) {
        throw new Error("No se encontro piloto3.pdf");
    }
    if (!outputFolder.exists && !outputFolder.create()) {
        throw new Error("No se pudo crear la carpeta de salida");
    }
    var packagedPdf = File(outputFolder.fsName + "/Piloto_3_Mix_Capitulo_1.pdf");
    if (packagedPdf.exists) {
        packagedPdf.remove();
    }
    if (!sourcePdf.copy(packagedPdf.fsName)) {
        throw new Error("No se pudo copiar el PDF vinculado al paquete");
    }
    sourcePdf = packagedPdf;

    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.documents.add();
    doc.documentPreferences.properties = {
        pageWidth: "297mm",
        pageHeight: "210mm",
        facingPages: false,
        pagesPerDocument: 9
    };

    function addRgb(name, values) {
        var color;
        try {
            color = doc.colors.itemByName(name);
            color.name;
        } catch (e) {
            color = doc.colors.add({
                name: name,
                model: ColorModel.PROCESS,
                space: ColorSpace.RGB,
                colorValue: values
            });
        }
        return color;
    }

    var coral = addRgb("P3 Coral", [239, 62, 70]);
    var navy = addRgb("P3 Azul tinta", [37, 37, 63]);
    var ivory = addRgb("P3 Marfil", [246, 242, 234]);

    function addParagraphStyle(name, size, leading, color) {
        var style = doc.paragraphStyles.add({name: name});
        style.pointSize = size;
        style.leading = leading;
        style.fillColor = color;
        return style;
    }

    addParagraphStyle("P3 Titulo de capitulo", 31, 34, coral);
    addParagraphStyle("P3 Codigo de seccion", 28, 28, navy);
    addParagraphStyle("P3 Titulo de seccion", 10, 12, navy);
    addParagraphStyle("P3 Cuerpo", 8, 10, navy);
    addParagraphStyle("P3 Pie y fuente", 7, 9, navy);

    var referenceLayer = doc.layers.item(0);
    referenceLayer.name = "REFERENCIA_PDF";
    var editableLayer = doc.layers.add({name: "CONTENIDO_EDITABLE"});
    editableLayer.move(LocationOptions.AT_BEGINNING);

    var margin = 18;
    var gutter = 5;
    var usableWidth = 297 - (margin * 2);
    var columnWidth = (usableWidth - (gutter * 5)) / 6;
    var usableHeight = 210 - (margin * 2);
    var rowGutter = 5;
    var rowHeight = (usableHeight - (rowGutter * 3)) / 4;

    for (var i = 0; i < 9; i++) {
        var page = doc.pages.item(i);
        page.marginPreferences.properties = {
            top: margin + "mm",
            bottom: margin + "mm",
            left: margin + "mm",
            right: margin + "mm",
            columnCount: 6,
            columnGutter: gutter + "mm"
        };

        for (var c = 1; c < 6; c++) {
            var x = margin + (columnWidth * c) + (gutter * (c - 0.5));
            page.guides.add(undefined, {
                orientation: HorizontalOrVertical.VERTICAL,
                location: x + "mm",
                guideType: GuideTypeOptions.RULER
            });
        }
        for (var r = 1; r < 4; r++) {
            var y = margin + (rowHeight * r) + (rowGutter * (r - 0.5));
            page.guides.add(undefined, {
                orientation: HorizontalOrVertical.HORIZONTAL,
                location: y + "mm",
                guideType: GuideTypeOptions.RULER
            });
        }

        app.pdfPlacePreferences.pageNumber = 16 + i;
        app.pdfPlacePreferences.pdfCrop = PDFCrop.CROP_MEDIA;
        var frame = page.rectangles.add(referenceLayer, {
            geometricBounds: ["0mm", "0mm", "210mm", "297mm"],
            strokeWeight: 0,
            fillColor: doc.swatches.itemByName("None")
        });
        frame.place(sourcePdf);
        frame.fit(FitOptions.PROPORTIONALLY);
        frame.fit(FitOptions.CENTER_CONTENT);
        frame.label = "Piloto 3 - pagina PDF " + (16 + i);
    }

    referenceLayer.locked = true;
    doc.activeLayer = editableLayer;
    doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
    doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;

    var inddFile = File(outputFolder.fsName + "/Piloto_3_Mix_Capitulo_1.indd");
    var idmlFile = File(outputFolder.fsName + "/Piloto_3_Mix_Capitulo_1.idml");
    doc.save(inddFile);
    doc.exportFile(ExportFormat.INDESIGN_MARKUP, idmlFile);
    doc.close(SaveOptions.YES);

    var report = File(outputFolder.fsName + "/LEEME.txt");
    report.encoding = "UTF-8";
    report.open("w");
    report.writeln("PILOTO 3 - MIX EDITORIAL, CAPITULO 1");
    report.writeln("");
    report.writeln("Documento A4 horizontal de 9 paginas.");
    report.writeln("Grilla: 6 columnas, margen 18 mm, medianil 5 mm y 4 bandas horizontales.");
    report.writeln("La capa REFERENCIA_PDF contiene las paginas 16-24 de piloto3.pdf y esta bloqueada.");
    report.writeln("La capa CONTENIDO_EDITABLE queda activa para reconstruir o ajustar la composicion.");
    report.writeln("Incluye muestras P3 Coral, P3 Azul tinta y P3 Marfil, ademas de estilos de parrafo base.");
    report.close();
})();
