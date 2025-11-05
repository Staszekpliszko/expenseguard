// backend/gus.js - Integracja z API GUS (REGON)
const https = require('https');
const { parseString } = require('xml2js');

const GUS_API_URL = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc';
const GUS_TEST_API_URL = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc';

// Test API key dla środowiska testowego
const TEST_API_KEY = 'abcde12345abcde12345';

/**
 * Wykonaj zapytanie SOAP do API GUS
 */
function soapRequest(url, action, body, sid = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);

    const headers = {
      'Content-Type': 'application/soap+xml; charset=utf-8',
      'SOAPAction': action,
      'Content-Length': Buffer.byteLength(body)
    };

    if (sid) {
      headers['sid'] = sid;
    }

    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname,
      method: 'POST',
      headers: headers
    };

    console.log('=== GUS API Request ===');
    console.log('URL:', url);
    console.log('Action:', action);
    console.log('Headers:', headers);
    console.log('Body:', body);

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        console.log('=== GUS API Response ===');
        console.log('Status:', res.statusCode);
        console.log('Headers:', res.headers);
        console.log('Body (first 500 chars):', data.substring(0, 500));

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 200)}`));
        }
      });
    });

    req.on('error', (error) => {
      console.error('=== GUS API Error ===');
      console.error(error);
      reject(error);
    });

    req.write(body);
    req.end();
  });
}

/**
 * Zaloguj się do API GUS
 */
async function login(apiUrl, apiKey) {
  const soapEnvelope = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:To>${apiUrl}</wsa:To>
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj</wsa:Action>
  </soap:Header>
  <soap:Body>
    <ns:Zaloguj>
      <ns:pKluczUzytkownika>${apiKey}</ns:pKluczUzytkownika>
    </ns:Zaloguj>
  </soap:Body>
</soap:Envelope>`;

  const response = await soapRequest(apiUrl, 'http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj', soapEnvelope);

  // Sprawdź czy odpowiedź to XML
  if (!response.trim().startsWith('<?xml') && !response.trim().startsWith('<')) {
    throw new Error(`Odpowiedź nie jest XML-em: ${response.substring(0, 100)}`);
  }

  return new Promise((resolve, reject) => {
    parseString(response, (err, result) => {
      if (err) {
        console.error('Błąd parsowania XML:', err);
        console.error('Odpowiedź:', response.substring(0, 500));
        reject(new Error(`Błąd parsowania XML: ${err.message}`));
        return;
      }

      try {
        console.log('Parsed result:', JSON.stringify(result, null, 2));
        const sid = result['s:Envelope']['s:Body'][0]['ZalogujResponse'][0]['ZalogujResult'][0];
        console.log('Session ID:', sid);
        resolve(sid);
      } catch (e) {
        console.error('Błąd wyciągania SID:', e);
        console.error('Parsed result:', JSON.stringify(result, null, 2));
        reject(new Error('Nie udało się wyciągnąć SID z odpowiedzi'));
      }
    });
  });
}

/**
 * Wyszukaj podmiot po NIP
 */
async function searchByNipSoap(apiUrl, sid, nip) {
  const soapEnvelope = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07" xmlns:dat="http://CIS/BIR/PUBL/2014/07/DataContract">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:To>${apiUrl}</wsa:To>
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty</wsa:Action>
  </soap:Header>
  <soap:Body>
    <ns:DaneSzukajPodmioty>
      <ns:pParametryWyszukiwania>
        <dat:Nip>${nip}</dat:Nip>
      </ns:pParametryWyszukiwania>
    </ns:DaneSzukajPodmioty>
  </soap:Body>
</soap:Envelope>`;

  const response = await soapRequest(apiUrl, 'http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty', soapEnvelope, sid);

  // Sprawdź czy odpowiedź to XML
  if (!response.trim().startsWith('<?xml') && !response.trim().startsWith('<')) {
    throw new Error(`Odpowiedź nie jest XML-em: ${response.substring(0, 100)}`);
  }

  return new Promise((resolve, reject) => {
    parseString(response, (err, result) => {
      if (err) {
        console.error('Błąd parsowania XML (search):', err);
        console.error('Odpowiedź:', response.substring(0, 500));
        reject(new Error(`Błąd parsowania XML: ${err.message}`));
        return;
      }

      try {
        console.log('Parsed search result:', JSON.stringify(result, null, 2));
        const xmlData = result['s:Envelope']['s:Body'][0]['DaneSzukajPodmiotyResponse'][0]['DaneSzukajPodmiotyResult'][0];
        console.log('XML Data:', xmlData);
        resolve(xmlData);
      } catch (e) {
        console.error('Błąd wyciągania danych:', e);
        console.error('Parsed result:', JSON.stringify(result, null, 2));
        reject(new Error('Nie udało się wyciągnąć danych z odpowiedzi'));
      }
    });
  });
}

/**
 * Wyloguj się z API GUS
 */
async function logout(apiUrl, sid) {
  const soapEnvelope = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:To>${apiUrl}</wsa:To>
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Wyloguj</wsa:Action>
  </soap:Header>
  <soap:Body>
    <ns:Wyloguj>
      <ns:pIdentyfikatorSesji>${sid}</ns:pIdentyfikatorSesji>
    </ns:Wyloguj>
  </soap:Body>
</soap:Envelope>`;

  try {
    await soapRequest(apiUrl, 'http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Wyloguj', soapEnvelope, sid);
    return true;
  } catch (error) {
    console.error('Błąd podczas wylogowania:', error);
    return false;
  }
}

/**
 * Wyszukaj firmę po NIP w bazie GUS
 * @param {string} nip - NIP firmy (bez kresek)
 * @param {boolean} useTestEnv - Czy używać środowiska testowego
 * @returns {Promise<Object|null>} - Dane firmy lub null jeśli nie znaleziono
 */
async function searchByNip(nip, useTestEnv = false) {
  let sid = null;

  try {
    // Usuń wszystkie znaki niebędące cyframi z NIP
    const cleanNip = nip.replace(/\D/g, '');

    if (cleanNip.length !== 10) {
      throw new Error('NIP musi mieć 10 cyfr');
    }

    const apiUrl = useTestEnv ? GUS_TEST_API_URL : GUS_API_URL;
    const apiKey = TEST_API_KEY;

    // Zaloguj się
    sid = await login(apiUrl, apiKey);

    if (!sid) {
      throw new Error('Nie udało się zalogować do API GUS');
    }

    // Wyszukaj po NIP
    const xmlResult = await searchByNipSoap(apiUrl, sid, cleanNip);

    // Wyloguj się
    await logout(apiUrl, sid);

    if (!xmlResult || xmlResult.trim() === '') {
      return null;
    }

    // Parsuj XML do obiektu
    const data = parseGusXml(xmlResult);

    if (!data || data.length === 0) {
      return null;
    }

    // Zwróć pierwszy wynik
    const company = data[0];

    return {
      name: company.Nazwa || '',
      nip: company.Nip || cleanNip,
      regon: company.Regon || '',
      address: formatAddress(company),
      type: company.Typ || ''
    };

  } catch (error) {
    // Wyloguj się w razie błędu
    if (sid) {
      const apiUrl = useTestEnv ? GUS_TEST_API_URL : GUS_API_URL;
      await logout(apiUrl, sid);
    }

    console.error('Błąd podczas wyszukiwania w GUS:', error);
    throw error;
  }
}

/**
 * Prosty parser XML dla odpowiedzi GUS
 * @param {string} xml - XML z odpowiedzią GUS
 * @returns {Array<Object>} - Tablica obiektów z danymi firm
 */
function parseGusXml(xml) {
  try {
    const results = [];

    // Regex do wyciągania danych z XML (prosty parser)
    const dataRegex = /<dane>([\s\S]*?)<\/dane>/gi;
    const matches = xml.matchAll(dataRegex);

    for (const match of matches) {
      const dataXml = match[1];
      const company = {};

      // Wyciągnij poszczególne pola
      const fields = {
        'Regon': /<Regon>(.*?)<\/Regon>/i,
        'Nip': /<Nip>(.*?)<\/Nip>/i,
        'Nazwa': /<Nazwa>(.*?)<\/Nazwa>/i,
        'Wojewodztwo': /<Wojewodztwo>(.*?)<\/Wojewodztwo>/i,
        'Powiat': /<Powiat>(.*?)<\/Powiat>/i,
        'Gmina': /<Gmina>(.*?)<\/Gmina>/i,
        'Miejscowosc': /<Miejscowosc>(.*?)<\/Miejscowosc>/i,
        'KodPocztowy': /<KodPocztowy>(.*?)<\/KodPocztowy>/i,
        'Ulica': /<Ulica>(.*?)<\/Ulica>/i,
        'NrNieruchomosci': /<NrNieruchomosci>(.*?)<\/NrNieruchomosci>/i,
        'NrLokalu': /<NrLokalu>(.*?)<\/NrLokalu>/i,
        'Typ': /<Typ>(.*?)<\/Typ>/i
      };

      for (const [key, regex] of Object.entries(fields)) {
        const fieldMatch = dataXml.match(regex);
        if (fieldMatch) {
          company[key] = fieldMatch[1];
        }
      }

      results.push(company);
    }

    return results;
  } catch (error) {
    console.error('Błąd parsowania XML:', error);
    return [];
  }
}

/**
 * Formatuj adres z danych GUS
 * @param {Object} company - Dane firmy z GUS
 * @returns {string} - Sformatowany adres
 */
function formatAddress(company) {
  const parts = [];

  if (company.Ulica) {
    parts.push(company.Ulica);
  }

  if (company.NrNieruchomosci) {
    parts.push(company.NrNieruchomosci);
    if (company.NrLokalu) {
      parts[parts.length - 1] += `/${company.NrLokalu}`;
    }
  }

  const street = parts.join(' ');

  const cityParts = [];
  if (company.KodPocztowy) {
    cityParts.push(company.KodPocztowy);
  }
  if (company.Miejscowosc) {
    cityParts.push(company.Miejscowosc);
  }

  const city = cityParts.join(' ');

  if (street && city) {
    return `${street}, ${city}`;
  } else if (city) {
    return city;
  } else if (street) {
    return street;
  }

  return '';
}

module.exports = {
  searchByNip
};
