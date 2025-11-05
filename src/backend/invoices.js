// backend/invoices.js
const { getDb } = require('./database');

// AUTOUZUPEŁNIANIE klientów/dostawców
function searchCounterparties(type, query) {
  const db = getDb();
  const q = `%${query}%`;
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT id, name, vat_id FROM counterparties WHERE type=? AND name LIKE ? ORDER BY name LIMIT 20`,
      [type, q],
      (err, rows) => { db.close(); err ? reject(err) : resolve(rows); }
    );
  });
}

// Dodanie klienta (zabezpieczenie na duplikatach)
function addCounterparty({ type, name, vat_id, email, phone, address }) {
  const db = getDb();
  return new Promise((resolve, reject) => {
    // Najpierw sprawdź, czy klient o tej nazwie i typie już istnieje
    db.get(
      `SELECT id FROM counterparties WHERE type=? AND name=?`,
      [type, name],
      (err, row) => {
        if (err) {
          db.close();
          return reject(err);
        }

        // Jeśli istnieje, zwróć jego ID
        if (row) {
          db.close();
          return resolve(row.id);
        }

        // Jeśli nie istnieje, dodaj nowego klienta
        db.run(
          `INSERT INTO counterparties(type, name, vat_id, email, phone, address)
           VALUES (?,?,?,?,?,?)`,
          [type, name, vat_id || null, email || null, phone || null, address || null],
          function(err) {
            db.close();
            err ? reject(err) : resolve(this.lastID);
          }
        );
      }
    );
  });
}

// Pobierz wszystkie faktury sprzedażowe
function getAllSalesInvoices() {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT si.*, c.name as client_name
       FROM sales_invoices si
       LEFT JOIN counterparties c ON si.counterparty_id = c.id
       ORDER BY si.issue_date DESC`,
      [],
      (err, rows) => { db.close(); err ? reject(err) : resolve(rows); }
    );
  });
}

// Pobierz wszystkie faktury kosztowe
function getAllPurchaseInvoices() {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT pi.*, c.name as supplier_name
       FROM purchase_invoices pi
       LEFT JOIN counterparties c ON pi.counterparty_id = c.id
       ORDER BY pi.issue_date DESC`,
      [],
      (err, rows) => { db.close(); err ? reject(err) : resolve(rows); }
    );
  });
}

// Dodaj fakturę sprzedażową
function addSalesInvoice({ number, counterparty_id, issue_date, due_date, link_url, status, note, items }) {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.run(
      `INSERT INTO sales_invoices(number, counterparty_id, issue_date, due_date, link_url, status, note)
       VALUES (?,?,?,?,?,?,?)`,
      [number, counterparty_id, issue_date, due_date || null, link_url || null, status || 'issued', note || null],
      function(err) {
        if (err) { db.close(); return reject(err); }
        const invoiceId = this.lastID;

        // Dodaj pozycje
        if (items && items.length > 0) {
          const stmt = db.prepare(`INSERT INTO sales_items(invoice_id, name, qty, net_unit, vat_rate) VALUES (?,?,?,?,?)`);
          items.forEach(item => {
            stmt.run([invoiceId, item.name, item.qty, item.net_unit, item.vat_rate]);
          });
          stmt.finalize();
        }

        db.close();
        resolve(invoiceId);
      }
    );
  });
}

// Dodaj fakturę kosztową
function addPurchaseInvoice({ number, counterparty_id, issue_date, due_date, link_url, deductible_vat, deductible_percent, status, category, note, items }) {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.run(
      `INSERT INTO purchase_invoices(number, counterparty_id, issue_date, due_date, link_url, deductible_vat, deductible_percent, status, category, note)
       VALUES (?,?,?,?,?,?,?,?,?,?)`,
      [number, counterparty_id, issue_date, due_date || null, link_url || null, deductible_vat || 'full', deductible_percent || 100, status || 'received', category || null, note || null],
      function(err) {
        if (err) { db.close(); return reject(err); }
        const invoiceId = this.lastID;

        // Dodaj pozycje
        if (items && items.length > 0) {
          const stmt = db.prepare(`INSERT INTO purchase_items(invoice_id, name, qty, net_unit, vat_rate) VALUES (?,?,?,?,?)`);
          items.forEach(item => {
            stmt.run([invoiceId, item.name, item.qty, item.net_unit, item.vat_rate]);
          });
          stmt.finalize();
        }

        db.close();
        resolve(invoiceId);
      }
    );
  });
}

// Pobierz ustawienia
function getSettings() {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.all(`SELECT key, value FROM settings`, [], (err, rows) => {
      db.close();
      if (err) return reject(err);
      const settings = {};
      rows.forEach(r => { settings[r.key] = r.value; });
      resolve(settings);
    });
  });
}

// Zaktualizuj ustawienie
function updateSetting(key, value) {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.run(
      `INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)`,
      [key, value],
      (err) => { db.close(); err ? reject(err) : resolve(); }
    );
  });
}

module.exports = {
  searchCounterparties,
  addCounterparty,
  getAllSalesInvoices,
  getAllPurchaseInvoices,
  addSalesInvoice,
  addPurchaseInvoice,
  getSettings,
  updateSetting
};
