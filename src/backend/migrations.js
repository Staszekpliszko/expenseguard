// backend/migrations.js
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const DB_PATH = path.join(__dirname, '..', '..', 'db', 'app.db');

function runMigrations() {
  console.log('Initializing database at:', DB_PATH);

  const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
      console.error('Failed to open database:', err);
      throw err;
    }
    console.log('Database connection established');
  });

  db.serialize(() => {
    // Klienci / Dostawcy (jedna tabela "counterparties" z typem)
    db.run(`
      CREATE TABLE IF NOT EXISTS counterparties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('client','supplier')),
        name TEXT NOT NULL,
        vat_id TEXT,           -- NIP
        email TEXT,
        phone TEXT,
        address TEXT,
        UNIQUE(type, name)
      );
    `);

    // Faktury sprzedaży
    db.run(`
      CREATE TABLE IF NOT EXISTS sales_invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL,
        counterparty_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,      -- YYYY-MM-DD
        due_date TEXT,
        link_url TEXT,                 -- link do inFakt/pliku
        status TEXT NOT NULL DEFAULT 'issued' CHECK(status IN ('issued','paid','overdue')),
        note TEXT,
        FOREIGN KEY(counterparty_id) REFERENCES counterparties(id),
        UNIQUE(number)
      );
    `);

    // Pozycje na FV sprzedaży
    db.run(`
      CREATE TABLE IF NOT EXISTS sales_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        qty REAL NOT NULL,
        net_unit REAL NOT NULL,        -- cena netto za szt.
        vat_rate REAL NOT NULL,        -- np. 23, 8, 0, 10 (z Ustawień)
        FOREIGN KEY(invoice_id) REFERENCES sales_invoices(id)
      );
    `);

    // Faktury kosztowe
    db.run(`
      CREATE TABLE IF NOT EXISTS purchase_invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL,
        counterparty_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT,
        link_url TEXT,
        deductible_vat TEXT NOT NULL DEFAULT 'full' CHECK(deductible_vat IN ('full','none','partial')),
        deductible_percent REAL DEFAULT 100,  -- jeśli partial, np. 50
        status TEXT NOT NULL DEFAULT 'received' CHECK(status IN ('received','paid','overdue')),
        category TEXT,                 -- ustawienia -> kategorie kosztów
        note TEXT,
        FOREIGN KEY(counterparty_id) REFERENCES counterparties(id)
      );
    `);

    // Pozycje na FV kosztowych
    db.run(`
      CREATE TABLE IF NOT EXISTS purchase_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        qty REAL NOT NULL,
        net_unit REAL NOT NULL,
        vat_rate REAL NOT NULL,
        FOREIGN KEY(invoice_id) REFERENCES purchase_invoices(id)
      );
    `);

    // Ustawienia aplikacji (klucz-wartość)
    db.run(`
      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
      );
    `);

    // Płatności (opcjonalnie – dla rozliczania statusów)
    db.run(`
      CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_type TEXT NOT NULL CHECK(doc_type IN ('sale','purchase')),
        doc_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        amount REAL NOT NULL
      );
    `);

    // Indeksy przyspieszające
    db.run(`CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_invoices(issue_date);`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_purchase_date ON purchase_invoices(issue_date);`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_counterparty ON counterparties(name);`);

    // Domyślne ustawienia
    db.run(`INSERT OR IGNORE INTO settings(key,value) VALUES
      ('default_vat_rates','[23,8,5,0,10]'),
      ('cit_rate','0.19'),
      ('zus_monthly','1600'),
      ('default_payment_terms_days','14')
    ;`);
  });

  db.close((err) => {
    if (err) {
      console.error('Failed to close database:', err);
    } else {
      console.log('Database migrations completed successfully');
    }
  });
}

module.exports = { runMigrations };
