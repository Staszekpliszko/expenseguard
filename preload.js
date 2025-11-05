// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  searchCounterparties: (type, q) => ipcRenderer.invoke('searchCounterparties', {type, q}),
  addCounterparty: (data) => ipcRenderer.invoke('addCounterparty', data),
  getAllCounterparties: (type) => ipcRenderer.invoke('getAllCounterparties', {type}),
  updateCounterparty: (id, data) => ipcRenderer.invoke('updateCounterparty', {id, data}),
  deleteCounterparty: (id) => ipcRenderer.invoke('deleteCounterparty', {id}),
  getAllSalesInvoices: () => ipcRenderer.invoke('getAllSalesInvoices'),
  getAllPurchaseInvoices: () => ipcRenderer.invoke('getAllPurchaseInvoices'),
  addSalesInvoice: (data) => ipcRenderer.invoke('addSalesInvoice', data),
  addPurchaseInvoice: (data) => ipcRenderer.invoke('addPurchaseInvoice', data),
  monthlySummary: (year, month) => ipcRenderer.invoke('monthlySummary', {year, month}),
  getSettings: () => ipcRenderer.invoke('getSettings'),
  updateSetting: (key, value) => ipcRenderer.invoke('updateSetting', {key, value}),
  searchGus: (nip, useTestEnv) => ipcRenderer.invoke('searchGus', {nip, useTestEnv})
});
