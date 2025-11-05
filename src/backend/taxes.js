// backend/taxes.js
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const DB_PATH = path.join(__dirname, '..', '..', 'db', 'app.db');

function getDb() { return new sqlite3.Database(DB_PATH); }

function monthRange(year, month) {
  // month: 1-12
  const from = new Date(Date.UTC(year, month - 1, 1));
  const to = new Date(Date.UTC(year, month, 1));
  const fmt = (d)=> d.toISOString().slice(0,10);
  return { from: fmt(from), to: fmt(to) };
}

// pomocniczo: suma po pozycji FV = qty * net_unit; VAT = suma * (vat_rate/100)
function _sumInvoiceItems(db, table, invoiceId) {
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT qty, net_unit, vat_rate FROM ${table} WHERE invoice_id=?`,
      [invoiceId],
      (err, rows) => {
        if (err) return reject(err);
        let net = 0, vat = 0;
        rows.forEach(r => {
          const lineNet = r.qty * r.net_unit;
          net += lineNet;
          vat += lineNet * (r.vat_rate/100);
        });
        resolve({ net, vat });
      }
    );
  });
}

async function salesTotalsForMonth(year, month) {
  const db = getDb();
  const { from, to } = monthRange(year, month);
  const invoices = await new Promise((resolve, reject) => {
    db.all(
      `SELECT id FROM sales_invoices WHERE issue_date >= ? AND issue_date < ?`,
      [from, to],
      (err, rows) => err ? reject(err) : resolve(rows)
    );
  });

  let net = 0, vat = 0;
  for (const inv of invoices) {
    const s = await _sumInvoiceItems(db, 'sales_items', inv.id);
    net += s.net;
    vat += s.vat;
  }
  db.close();
  return { net, vat };
}

async function purchaseTotalsForMonth(year, month) {
  const db = getDb();
  const { from, to } = monthRange(year, month);
  const invoices = await new Promise((resolve, reject) => {
    db.all(
      `SELECT id, deductible_vat, deductible_percent FROM purchase_invoices WHERE issue_date >= ? AND issue_date < ?`,
      [from, to],
      (err, rows) => err ? reject(err) : resolve(rows)
    );
  });

  let net = 0, vat = 0;
  for (const inv of invoices) {
    const s = await _sumInvoiceItems(db, 'purchase_items', inv.id);
    net += s.net;
    let vatAdd = s.vat;
    // odliczalność VAT
    // 'none' -> 0; 'full' -> 100%; 'partial' -> procent
    // zakładamy, że s.vat już policzony z pozycji
    // przy partial zastosuj procent odliczenia
    if (inv.deductible_vat === 'none') vatAdd = 0;
    else if (inv.deductible_vat === 'partial') {
      const pct = (inv.deductible_percent ?? 100) / 100;
      vatAdd = s.vat * pct;
    }
    vat += vatAdd;
  }
  db.close();
  return { net, vat };
}

async function monthlySummary(year, month) {
  const sales = await salesTotalsForMonth(year, month);
  const purchases = await purchaseTotalsForMonth(year, month);

  // VAT
  const vat_due = Math.max(0, sales.vat - purchases.vat);
  // podstawa podatku dochodowego (bardzo uproszczona)
  const base_cit = Math.max(0, sales.net - purchases.net);

  // pobierz ustawienia CIT i ZUS
  const db = getDb();
  const getSetting = (k) => new Promise((resolve) => {
    db.get(`SELECT value FROM settings WHERE key=?`, [k], (e,row)=>{
      if (e || !row) return resolve(null);
      resolve(row.value);
    });
  });

  const citRate = parseFloat(await getSetting('cit_rate') || '0.19'); // np. 0.19
  const zusMonthly = parseFloat(await getSetting('zus_monthly') || '0');

  const cit = base_cit * citRate;

  // "Na rękę" – orientacyjnie
  // przychód_brutto = net + VAT należny (sprzedaż)
  const revenue_gross = sales.net + sales.vat;
  const take_home = revenue_gross - vat_due - cit - zusMonthly;

  db.close();
  return {
    month: `${year}-${String(month).padStart(2,'0')}`,
    sales_net: sales.net, sales_vat: sales.vat,
    purchase_net: purchases.net, purchase_vat: purchases.vat,
    vat_due, cit, zus: zusMonthly, take_home
  };
}

module.exports = { monthlySummary };
