// Script para converter datas em arquivos Excel para o formato brasileiro (dd-MM-yyyy)
// Requer as bibliotecas SheetJS e PapaParse

const fs = require('fs');
const XLSX = require('xlsx');

// Caminho do arquivo de entrada e saída
const inputFile = 'basePedidosSeparacao03.xlsx';
const outputFile = 'basePedidosSeparacao03_formatoBR.xlsx';

// Lê o arquivo Excel
const workbook = XLSX.readFile(inputFile, {
    cellDates: true,
    cellNF: true
});

// Obtém a primeira planilha
const firstSheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[firstSheetName];

// Converte para CSV para processar os dados
const csvData = XLSX.utils.sheet_to_csv(worksheet);

// Divide o CSV em linhas e processa cada linha
const rows = csvData.trim().split('\n');

// Processa o cabeçalho separadamente
const headerRow = rows[0].split(',');
// Remove aspas se presentes no cabeçalho
const cleanHeader = headerRow.map(h => h.replace(/^"|"$/g, ''));

// Processa cada linha de dados
const processedData = [];
processedData.push(cleanHeader); // Adiciona a linha de cabeçalho primeiro

// Processa as linhas de dados
for (let i = 1; i < rows.length; i++) {
    const values = rows[i].split(',');
    const cleanValues = values.map(v => v.replace(/^"|"$/g, '')); // Remove aspas
    
    // DateOfSeparation está no índice 2 (3ª coluna)
    if (cleanValues.length > 2 && cleanValues[2].match(/^\d{4}-\d{2}-\d{2}$/)) {
        const [year, month, day] = cleanValues[2].split('-');
        cleanValues[2] = `${day}-${month}-${year}`;
    }
    
    // CreatedAt está no índice 4 (5ª coluna)
    if (cleanValues.length > 4 && cleanValues[4].includes(' ')) {
        const [datePart, timePart] = cleanValues[4].split(' ');
        if (datePart.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const [year, month, day] = datePart.split('-');
            cleanValues[4] = `${day}-${month}-${year} ${timePart}`;
        }
    }
    
    processedData.push(cleanValues);
}

// Cria um novo workbook com os dados formatados corretamente
const newWb = XLSX.utils.book_new();
const newWs = XLSX.utils.aoa_to_sheet(processedData);

// Define formatos de coluna para garantir que as datas sejam exibidas corretamente
const dateFormats = {
    'DateOfSeparation': 'dd-mm-yyyy',
    'CreatedAt': 'dd-mm-yyyy hh:mm:ss.000'
};

// Encontra os índices das colunas
const dateFormatColIndices = {};
for (const [colName, format] of Object.entries(dateFormats)) {
    const colIndex = processedData[0].indexOf(colName);
    if (colIndex !== -1) {
        dateFormatColIndices[colIndex] = format;
    }
}

// Define formatos de data para cada célula nas colunas de data
const range = XLSX.utils.decode_range(newWs['!ref']);
for (let r = 1; r <= range.e.r; r++) { // Pula a linha de cabeçalho
    for (const [colIndex, format] of Object.entries(dateFormatColIndices)) {
        const cellRef = XLSX.utils.encode_cell({r, c: parseInt(colIndex)});
        if (newWs[cellRef]) {
            newWs[cellRef].z = format;
        }
    }
}

// Adiciona a planilha ao workbook
XLSX.utils.book_append_sheet(newWb, newWs, "BasePedidosSeparacao");

// Grava o novo arquivo Excel
XLSX.writeFile(newWb, outputFile);

console.log(`Conversão concluída com sucesso! ${processedData.length - 1} linhas processadas.`);
console.log(`Novo arquivo salvo como: ${outputFile}`);

// Initialize a new npm project (if you haven't already)
// npm init -y

// Install SheetJS (xlsx) for Excel file operations
// npm install xlsx

// Install PapaParse for CSV parsing (mentioned in your script comment)
// npm install papaparse
