// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { runMigrations } = require('./src/backend/migrations');
const {
  searchCounterparties,
  addCounterparty,
  getAllCounterparties,
  updateCounterparty,
  deleteCounterparty,
  getAllSalesInvoices,
  getAllPurchaseInvoices,
  addSalesInvoice,
  addPurchaseInvoice,
  getSettings,
  updateSetting
} = require('./src/backend/invoices');
const { monthlySummary } = require('./src/backend/taxes');
const { searchByNip } = require('./src/backend/gus');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'ui', 'index.html'));

  // W trybie dev otwórz DevTools
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  // Utwórz folder db/ jeśli nie istnieje
  const dbDir = path.join(__dirname, 'db');
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }

  // Uruchom migracje przy starcie
  runMigrations();

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers
ipcMain.handle('searchCounterparties', async (_e, {type, q}) => {
  return await searchCounterparties(type, q || '');
});

ipcMain.handle('addCounterparty', async (_e, data) => {
  return await addCounterparty(data);
});

ipcMain.handle('getAllCounterparties', async (_e, { type }) => {
  return await getAllCounterparties(type);
});

ipcMain.handle('updateCounterparty', async (_e, { id, data }) => {
  return await updateCounterparty(id, data);
});

ipcMain.handle('deleteCounterparty', async (_e, { id }) => {
  return await deleteCounterparty(id);
});

ipcMain.handle('getAllSalesInvoices', async () => {
  return await getAllSalesInvoices();
});

ipcMain.handle('getAllPurchaseInvoices', async () => {
  return await getAllPurchaseInvoices();
});

ipcMain.handle('addSalesInvoice', async (_e, data) => {
  return await addSalesInvoice(data);
});

ipcMain.handle('addPurchaseInvoice', async (_e, data) => {
  return await addPurchaseInvoice(data);
});

ipcMain.handle('monthlySummary', async (_e, {year, month}) => {
  return await monthlySummary(year, month);
});

ipcMain.handle('getSettings', async () => {
  return await getSettings();
});

ipcMain.handle('updateSetting', async (_e, {key, value}) => {
  return await updateSetting(key, value);
});

ipcMain.handle('searchGus', async (_e, { nip, useTestEnv }) => {
  try {
    return await searchByNip(nip, useTestEnv);
  } catch (error) {
    console.error('Błąd wyszukiwania GUS:', error);
    throw error;
  }
});
