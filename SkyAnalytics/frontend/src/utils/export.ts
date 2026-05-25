import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

/**
 * Exporta datos a formato Excel (.xlsx)
 */
export const downloadExcel = (data: any[], fileName: string) => {
    const worksheet = XLSX.utils.json_to_sheet(data)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, "Datos")
    XLSX.writeFile(workbook, `${fileName}_${new Date().getTime()}.xlsx`)
}

/**
 * Exporta datos a formato PDF (.pdf) con diseño empresarial
 */
export const downloadPDF = (title: string, headers: string[], rows: any[][], fileName: string) => {
    const doc = new jsPDF()

    // Cabecera del Documento
    doc.setFontSize(20)
    doc.setTextColor(255, 255, 255)
    doc.setFillColor(15, 23, 42) // Slate-900
    doc.rect(0, 0, 210, 40, 'F')
    doc.text("SkyAnalytics Business Report", 14, 25)

    doc.setFontSize(14)
    doc.setTextColor(15, 23, 42)
    doc.text(title, 14, 55)

    doc.setFontSize(10)
    doc.setTextColor(100)
    doc.text(`Fecha de generación: ${new Date().toLocaleString()}`, 14, 62)
    doc.text(`Sistema de Inteligencia Operacional`, 14, 67)

    // Generar tabla de datos
    autoTable(doc, {
        startY: 75,
        head: [headers],
        body: rows,
        theme: 'striped',
        headStyles: {
            fillColor: [14, 165, 233], // Sky-500
            textColor: [255, 255, 255],
            fontSize: 10,
            fontStyle: 'bold'
        },
        styles: { fontSize: 9, cellPadding: 3 },
        alternateRowStyles: { fillColor: [248, 250, 252] }
    })

    doc.save(`${fileName}_${new Date().getTime()}.pdf`)
}