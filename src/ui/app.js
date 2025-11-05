const { useState, useEffect } = React;

// Modal do dodawania nowego klienta/dostawcy
function AddCounterpartyModal({ type, onClose, onAdded }) {
  const [name, setName] = useState('');
  const [vatId, setVatId] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [isSearchingGus, setIsSearchingGus] = useState(false);

  const handleSearchGus = async () => {
    if (!vatId) {
      alert('Wprowadź NIP przed wyszukiwaniem');
      return;
    }

    setIsSearchingGus(true);
    try {
      const result = await window.api.searchGus(vatId, true); // true = środowisko testowe

      if (result) {
        setName(result.name);
        setAddress(result.address);
        alert('Znaleziono firmę w bazie GUS!');
      } else {
        alert('Nie znaleziono firmy o podanym NIP w bazie GUS');
      }
    } catch (error) {
      console.error('Błąd wyszukiwania GUS:', error);
      alert('Błąd podczas wyszukiwania w GUS: ' + error.message);
    } finally {
      setIsSearchingGus(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name) {
      alert('Nazwa jest wymagana');
      return;
    }
    try {
      const id = await window.api.addCounterparty({
        type,
        name,
        vat_id: vatId || null,
        email: email || null,
        phone: phone || null,
        address: address || null
      });
      alert('Dodano pomyślnie!');
      onAdded({ id, name, vat_id: vatId });
      onClose();
    } catch (error) {
      console.error('Błąd dodawania klienta:', error);
      alert('Błąd podczas dodawania: ' + error.message);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999
    }}>
      <div style={{
        background: 'white',
        padding: '30px',
        borderRadius: '8px',
        width: '500px',
        maxWidth: '90%'
      }}>
        <h3 style={{ marginBottom: '20px' }}>
          Dodaj {type === 'client' ? 'klienta' : 'dostawcę'}
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Nazwa *</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">NIP</label>
            <div className="flex" style={{ gap: '5px' }}>
              <input
                type="text"
                className="form-input"
                value={vatId}
                onChange={e => setVatId(e.target.value)}
                style={{ flex: 1 }}
              />
              <button
                type="button"
                className="btn btn-secondary btn-small"
                onClick={handleSearchGus}
                disabled={isSearchingGus}
                style={{ padding: '10px 15px', whiteSpace: 'nowrap' }}
              >
                {isSearchingGus ? 'Szukam...' : 'Wyszukaj w GUS'}
              </button>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Telefon</label>
            <input
              type="text"
              className="form-input"
              value={phone}
              onChange={e => setPhone(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Adres</label>
            <textarea
              className="form-input"
              value={address}
              onChange={e => setAddress(e.target.value)}
              rows="2"
            />
          </div>
          <div className="flex flex-end" style={{ gap: '10px', marginTop: '20px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Anuluj
            </button>
            <button type="submit" className="btn btn-primary">
              Dodaj
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Komponent autouzupełniania klientów/dostawców
function ClientAutocomplete({ type, onSelect, placeholder }) {
  const [query, setQuery] = useState('');
  const [list, setList] = useState([]);
  const [showList, setShowList] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!query) {
      setList([]);
      return;
    }
    (async () => {
      const rows = await window.api.searchCounterparties(type, query);
      setList(rows);
      setShowList(true);
    })();
  }, [query, type]);

  return (
    <div>
      <div className="flex" style={{ gap: '5px' }}>
        <div className="autocomplete-container" style={{ flex: 1 }}>
          <input
            className="form-input"
            placeholder={placeholder}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onFocus={() => query && setShowList(true)}
          />
          {showList && list.length > 0 && (
            <div className="autocomplete-list">
              {list.map(r => (
                <div
                  key={r.id}
                  className="autocomplete-item"
                  onClick={() => {
                    onSelect(r);
                    setQuery(r.name);
                    setShowList(false);
                  }}
                >
                  {r.name} {r.vat_id ? `• NIP: ${r.vat_id}` : ''}
                </div>
              ))}
            </div>
          )}
        </div>
        <button
          type="button"
          className="btn btn-secondary btn-small"
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 15px' }}
        >
          + Nowy
        </button>
      </div>
      {showModal && (
        <AddCounterpartyModal
          type={type}
          onClose={() => setShowModal(false)}
          onAdded={(c) => {
            onSelect(c);
            setQuery(c.name);
          }}
        />
      )}
    </div>
  );
}

// Komponent zakładki: Podatki
function TaxesMonthly() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [result, setResult] = useState(null);

  const load = async () => {
    const r = await window.api.monthlySummary(year, month);
    setResult(r);
  };

  return (
    <div>
      <h2 className="section-title">Podsumowanie podatkowe</h2>
      <div className="card">
        <div className="flex">
          <div className="form-group">
            <label className="form-label">Rok</label>
            <input
              type="number"
              className="form-input"
              style={{ width: '120px' }}
              value={year}
              onChange={e => setYear(parseInt(e.target.value || '0'))}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Miesiąc</label>
            <input
              type="number"
              className="form-input"
              style={{ width: '100px' }}
              value={month}
              onChange={e => setMonth(parseInt(e.target.value || '0'))}
              min="1"
              max="12"
            />
          </div>
          <div className="form-group" style={{ alignSelf: 'flex-end' }}>
            <button className="btn btn-primary" onClick={load}>Przelicz</button>
          </div>
        </div>
      </div>

      {result && (
        <div className="grid grid-2">
          <div className="card">
            <h3 style={{ marginBottom: '15px', fontSize: '18px' }}>Przychody</h3>
            <div style={{ marginBottom: '10px' }}>Przychód netto: <strong>{result.sales_net.toFixed(2)} PLN</strong></div>
            <div style={{ marginBottom: '10px' }}>VAT należny: <strong>{result.sales_vat.toFixed(2)} PLN</strong></div>
            <div style={{ marginBottom: '10px' }}>Koszty netto: <strong>{result.purchase_net.toFixed(2)} PLN</strong></div>
            <div>VAT naliczony: <strong>{result.purchase_vat.toFixed(2)} PLN</strong></div>
          </div>
          <div className="card">
            <h3 style={{ marginBottom: '15px', fontSize: '18px' }}>Do zapłaty</h3>
            <div style={{ marginBottom: '10px' }}>VAT do zapłaty: <strong style={{ color: '#dc2626' }}>{result.vat_due.toFixed(2)} PLN</strong></div>
            <div style={{ marginBottom: '10px' }}>CIT/PIT: <strong style={{ color: '#dc2626' }}>{result.cit.toFixed(2)} PLN</strong></div>
            <div style={{ marginBottom: '15px' }}>ZUS: <strong style={{ color: '#dc2626' }}>{result.zus.toFixed(2)} PLN</strong></div>
            <div style={{ fontSize: '20px', marginTop: '20px', paddingTop: '20px', borderTop: '2px solid #e5e7eb' }}>
              Na rękę: <strong style={{ color: '#16a34a' }}>{result.take_home.toFixed(2)} PLN</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Komponent zakładki: Faktury Sprzedaży (Przychód)
function SalesInvoices() {
  const [invoices, setInvoices] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const loadInvoices = async () => {
    const data = await window.api.getAllSalesInvoices();
    setInvoices(data);
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  return (
    <div>
      <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2 className="section-title">Faktury sprzedaży</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Anuluj' : 'Dodaj fakturę'}
        </button>
      </div>

      {showForm && <SalesInvoiceForm onSaved={() => { setShowForm(false); loadInvoices(); }} />}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Numer</th>
              <th>Klient</th>
              <th>Data wystawienia</th>
              <th>Termin płatności</th>
              <th>Status</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map(inv => (
              <tr key={inv.id}>
                <td>{inv.number}</td>
                <td>{inv.client_name}</td>
                <td>{inv.issue_date}</td>
                <td>{inv.due_date || '-'}</td>
                <td>
                  <span className={`status-badge status-${inv.status}`}>
                    {inv.status === 'issued' ? 'Wystawiona' : inv.status === 'paid' ? 'Opłacona' : 'Przeterminowana'}
                  </span>
                </td>
                <td>{inv.link_url ? <a href={inv.link_url} target="_blank">Otwórz</a> : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Formularz dodawania faktury sprzedażowej
function SalesInvoiceForm({ onSaved }) {
  const [number, setNumber] = useState('');
  const [clientId, setClientId] = useState(null);
  const [issueDate, setIssueDate] = useState(new Date().toISOString().slice(0, 10));
  const [dueDate, setDueDate] = useState('');
  const [linkUrl, setLinkUrl] = useState('');
  const [status, setStatus] = useState('issued');
  const [note, setNote] = useState('');
  const [items, setItems] = useState([{ name: '', qty: 1, net_unit: 0, vat_rate: 23 }]);

  const addItem = () => {
    setItems([...items, { name: '', qty: 1, net_unit: 0, vat_rate: 23 }]);
  };

  const updateItem = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = value;
    setItems(updated);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!clientId) {
      alert('Wybierz klienta');
      return;
    }
    await window.api.addSalesInvoice({
      number,
      counterparty_id: clientId,
      issue_date: issueDate,
      due_date: dueDate || null,
      link_url: linkUrl || null,
      status,
      note: note || null,
      items: items.filter(i => i.name && i.qty > 0)
    });
    alert('Faktura dodana!');
    onSaved();
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '15px', fontSize: '18px' }}>Nowa faktura sprzedaży</h3>
      <div className="grid grid-2">
        <div className="form-group">
          <label className="form-label">Numer faktury *</label>
          <input
            type="text"
            className="form-input"
            value={number}
            onChange={e => setNumber(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Klient *</label>
          <ClientAutocomplete
            type="client"
            placeholder="Wyszukaj klienta..."
            onSelect={c => setClientId(c.id)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Data wystawienia *</label>
          <input
            type="date"
            className="form-input"
            value={issueDate}
            onChange={e => setIssueDate(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Termin płatności</label>
          <input
            type="date"
            className="form-input"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Link (inFakt/plik)</label>
          <input
            type="text"
            className="form-input"
            value={linkUrl}
            onChange={e => setLinkUrl(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Status</label>
          <select className="form-input" value={status} onChange={e => setStatus(e.target.value)}>
            <option value="issued">Wystawiona</option>
            <option value="paid">Opłacona</option>
            <option value="overdue">Przeterminowana</option>
          </select>
        </div>
      </div>
      <div className="form-group">
        <label className="form-label">Notatka</label>
        <textarea className="form-input" value={note} onChange={e => setNote(e.target.value)} rows="2"></textarea>
      </div>

      <h4 style={{ marginTop: '20px', marginBottom: '10px' }}>Pozycje</h4>
      <table className="table items-table">
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Ilość</th>
            <th>Cena netto</th>
            <th>Stawka VAT (%)</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i}>
              <td>
                <input
                  type="text"
                  className="form-input"
                  value={item.name}
                  onChange={e => updateItem(i, 'name', e.target.value)}
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.qty}
                  onChange={e => updateItem(i, 'qty', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.net_unit}
                  onChange={e => updateItem(i, 'net_unit', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.vat_rate}
                  onChange={e => updateItem(i, 'vat_rate', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <button type="button" className="btn btn-secondary btn-small" onClick={() => removeItem(i)}>Usuń</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="btn btn-secondary btn-small" onClick={addItem} style={{ marginTop: '10px' }}>
        Dodaj pozycję
      </button>

      <div className="flex flex-end mt-4">
        <button type="submit" className="btn btn-primary">Zapisz fakturę</button>
      </div>
    </form>
  );
}

// Komponent zakładki: Faktury Kosztowe
function PurchaseInvoices() {
  const [invoices, setInvoices] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const loadInvoices = async () => {
    const data = await window.api.getAllPurchaseInvoices();
    setInvoices(data);
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  return (
    <div>
      <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2 className="section-title">Faktury kosztowe</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Anuluj' : 'Dodaj fakturę'}
        </button>
      </div>

      {showForm && <PurchaseInvoiceForm onSaved={() => { setShowForm(false); loadInvoices(); }} />}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Numer</th>
              <th>Dostawca</th>
              <th>Data wystawienia</th>
              <th>Kategoria</th>
              <th>Odliczalność VAT</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map(inv => (
              <tr key={inv.id}>
                <td>{inv.number}</td>
                <td>{inv.supplier_name}</td>
                <td>{inv.issue_date}</td>
                <td>{inv.category || '-'}</td>
                <td>
                  {inv.deductible_vat === 'full' ? 'Pełna' : inv.deductible_vat === 'none' ? 'Brak' : `${inv.deductible_percent}%`}
                </td>
                <td>
                  <span className={`status-badge status-${inv.status === 'received' ? 'issued' : inv.status}`}>
                    {inv.status === 'received' ? 'Otrzymana' : inv.status === 'paid' ? 'Opłacona' : 'Przeterminowana'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Formularz dodawania faktury kosztowej
function PurchaseInvoiceForm({ onSaved }) {
  const [number, setNumber] = useState('');
  const [supplierId, setSupplierId] = useState(null);
  const [issueDate, setIssueDate] = useState(new Date().toISOString().slice(0, 10));
  const [dueDate, setDueDate] = useState('');
  const [linkUrl, setLinkUrl] = useState('');
  const [deductibleVat, setDeductibleVat] = useState('full');
  const [deductiblePercent, setDeductiblePercent] = useState(100);
  const [status, setStatus] = useState('received');
  const [category, setCategory] = useState('');
  const [note, setNote] = useState('');
  const [items, setItems] = useState([{ name: '', qty: 1, net_unit: 0, vat_rate: 23 }]);

  const addItem = () => {
    setItems([...items, { name: '', qty: 1, net_unit: 0, vat_rate: 23 }]);
  };

  const updateItem = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = value;
    setItems(updated);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!supplierId) {
      alert('Wybierz dostawcę');
      return;
    }
    await window.api.addPurchaseInvoice({
      number,
      counterparty_id: supplierId,
      issue_date: issueDate,
      due_date: dueDate || null,
      link_url: linkUrl || null,
      deductible_vat: deductibleVat,
      deductible_percent: deductiblePercent,
      status,
      category: category || null,
      note: note || null,
      items: items.filter(i => i.name && i.qty > 0)
    });
    alert('Faktura dodana!');
    onSaved();
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '15px', fontSize: '18px' }}>Nowa faktura kosztowa</h3>
      <div className="grid grid-2">
        <div className="form-group">
          <label className="form-label">Numer faktury *</label>
          <input
            type="text"
            className="form-input"
            value={number}
            onChange={e => setNumber(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Dostawca *</label>
          <ClientAutocomplete
            type="supplier"
            placeholder="Wyszukaj dostawcę..."
            onSelect={c => setSupplierId(c.id)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Data wystawienia *</label>
          <input
            type="date"
            className="form-input"
            value={issueDate}
            onChange={e => setIssueDate(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Termin płatności</label>
          <input
            type="date"
            className="form-input"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Kategoria</label>
          <input
            type="text"
            className="form-input"
            value={category}
            onChange={e => setCategory(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Status</label>
          <select className="form-input" value={status} onChange={e => setStatus(e.target.value)}>
            <option value="received">Otrzymana</option>
            <option value="paid">Opłacona</option>
            <option value="overdue">Przeterminowana</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Odliczalność VAT</label>
          <select className="form-input" value={deductibleVat} onChange={e => setDeductibleVat(e.target.value)}>
            <option value="full">Pełna (100%)</option>
            <option value="partial">Częściowa</option>
            <option value="none">Brak</option>
          </select>
        </div>
        {deductibleVat === 'partial' && (
          <div className="form-group">
            <label className="form-label">Procent odliczenia (%)</label>
            <input
              type="number"
              className="form-input"
              value={deductiblePercent}
              onChange={e => setDeductiblePercent(parseFloat(e.target.value))}
              min="0"
              max="100"
            />
          </div>
        )}
        <div className="form-group">
          <label className="form-label">Link (inFakt/plik)</label>
          <input
            type="text"
            className="form-input"
            value={linkUrl}
            onChange={e => setLinkUrl(e.target.value)}
          />
        </div>
      </div>
      <div className="form-group">
        <label className="form-label">Notatka</label>
        <textarea className="form-input" value={note} onChange={e => setNote(e.target.value)} rows="2"></textarea>
      </div>

      <h4 style={{ marginTop: '20px', marginBottom: '10px' }}>Pozycje</h4>
      <table className="table items-table">
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Ilość</th>
            <th>Cena netto</th>
            <th>Stawka VAT (%)</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i}>
              <td>
                <input
                  type="text"
                  className="form-input"
                  value={item.name}
                  onChange={e => updateItem(i, 'name', e.target.value)}
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.qty}
                  onChange={e => updateItem(i, 'qty', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.net_unit}
                  onChange={e => updateItem(i, 'net_unit', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <input
                  type="number"
                  className="form-input"
                  value={item.vat_rate}
                  onChange={e => updateItem(i, 'vat_rate', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </td>
              <td>
                <button type="button" className="btn btn-secondary btn-small" onClick={() => removeItem(i)}>Usuń</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="btn btn-secondary btn-small" onClick={addItem} style={{ marginTop: '10px' }}>
        Dodaj pozycję
      </button>

      <div className="flex flex-end mt-4">
        <button type="submit" className="btn btn-primary">Zapisz fakturę</button>
      </div>
    </form>
  );
}

// Komponent zakładki: Ustawienia
function Settings() {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const s = await window.api.getSettings();
      setSettings(s);
      setLoading(false);
    })();
  }, []);

  const updateSetting = async (key, value) => {
    await window.api.updateSetting(key, value);
    setSettings({ ...settings, [key]: value });
    alert('Ustawienie zapisane');
  };

  if (loading) return <div>Ładowanie...</div>;

  return (
    <div>
      <h2 className="section-title">Ustawienia</h2>
      <div className="card">
        <div className="form-group">
          <label className="form-label">Domyślne stawki VAT (JSON array, np. [23,8,5,0])</label>
          <input
            type="text"
            className="form-input"
            value={settings.default_vat_rates || ''}
            onChange={e => setSettings({ ...settings, default_vat_rates: e.target.value })}
          />
          <button
            className="btn btn-primary btn-small"
            style={{ marginTop: '10px' }}
            onClick={() => updateSetting('default_vat_rates', settings.default_vat_rates)}
          >
            Zapisz
          </button>
        </div>

        <div className="form-group">
          <label className="form-label">Stawka CIT/PIT (np. 0.19 dla 19%)</label>
          <input
            type="text"
            className="form-input"
            value={settings.cit_rate || ''}
            onChange={e => setSettings({ ...settings, cit_rate: e.target.value })}
          />
          <button
            className="btn btn-primary btn-small"
            style={{ marginTop: '10px' }}
            onClick={() => updateSetting('cit_rate', settings.cit_rate)}
          >
            Zapisz
          </button>
        </div>

        <div className="form-group">
          <label className="form-label">ZUS miesięczny (PLN)</label>
          <input
            type="text"
            className="form-input"
            value={settings.zus_monthly || ''}
            onChange={e => setSettings({ ...settings, zus_monthly: e.target.value })}
          />
          <button
            className="btn btn-primary btn-small"
            style={{ marginTop: '10px' }}
            onClick={() => updateSetting('zus_monthly', settings.zus_monthly)}
          >
            Zapisz
          </button>
        </div>

        <div className="form-group">
          <label className="form-label">Domyślny termin płatności (dni)</label>
          <input
            type="text"
            className="form-input"
            value={settings.default_payment_terms_days || ''}
            onChange={e => setSettings({ ...settings, default_payment_terms_days: e.target.value })}
          />
          <button
            className="btn btn-primary btn-small"
            style={{ marginTop: '10px' }}
            onClick={() => updateSetting('default_payment_terms_days', settings.default_payment_terms_days)}
          >
            Zapisz
          </button>
        </div>
      </div>
    </div>
  );
}

// Główna aplikacja
function App() {
  const [activeTab, setActiveTab] = useState('taxes');

  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>ExpenseGuard</h1>
        <div
          className={`nav-item ${activeTab === 'taxes' ? 'active' : ''}`}
          onClick={() => setActiveTab('taxes')}
        >
          Podatki
        </div>
        <div
          className={`nav-item ${activeTab === 'sales' ? 'active' : ''}`}
          onClick={() => setActiveTab('sales')}
        >
          Faktury - Przychód
        </div>
        <div
          className={`nav-item ${activeTab === 'purchase' ? 'active' : ''}`}
          onClick={() => setActiveTab('purchase')}
        >
          Faktury - Kosztowe
        </div>
        <div
          className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Ustawienia
        </div>
      </div>
      <div className="main-content">
        {activeTab === 'taxes' && <TaxesMonthly />}
        {activeTab === 'sales' && <SalesInvoices />}
        {activeTab === 'purchase' && <PurchaseInvoices />}
        {activeTab === 'settings' && <Settings />}
      </div>
    </div>
  );
}

// Renderuj aplikację
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
