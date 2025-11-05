// backend/gus.js - Integracja z API GUS (REGON)
const soap = require('soap');

const GUS_WSDL_URL = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc?wsdl';
const GUS_WSDL_TEST_URL = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc?wsdl';

// Test API key dla środowiska testowego (można użyć 'abcde12345abcde12345')
// W produkcji trzeba uzyskać prawdziwy klucz z GUS
const TEST_API_KEY = 'abcde12345abcde12345';

/**
 * Wyszukaj firmę po NIP w bazie GUS
 * @param {string} nip - NIP firmy (bez kresek)
 * @param {boolean} useTestEnv - Czy używać środowiska testowego
 * @returns {Promise<Object|null>} - Dane firmy lub null jeśli nie znaleziono
 */
async function searchByNip(nip, useTestEnv = false) {
  try {
    // Usuń wszystkie znaki niebędące cyframi z NIP
    const cleanNip = nip.replace(/\D/g, '');

    if (cleanNip.length !== 10) {
      throw new Error('NIP musi mieć 10 cyfr');
    }

    const wsdlUrl = useTestEnv ? GUS_WSDL_TEST_URL : GUS_WSDL_URL;
    const apiKey = TEST_API_KEY; // W przyszłości można dodać konfigurację w settings

    // Utwórz klienta SOAP
    const client = await soap.createClientAsync(wsdlUrl);

    // Zaloguj się do API
    const loginResult = await client.ZalogujAsync({
      pKluczUzytkownika: apiKey
    });

    const sessionId = loginResult[0].ZalogujResult;

    if (!sessionId) {
      throw new Error('Nie udało się zalogować do API GUS');
    }

    // Ustaw nagłówek z identyfikatorem sesji
    client.addSoapHeader({
      'ns3:sid': sessionId
    }, 'sid', 'ns3', 'http://www.w3.org/2005/08/addressing');

    // Wyszukaj po NIP
    const searchResult = await client.DaneSzukajPodmiotyAsync({
      pParametryWyszukiwania: `<root><Nip>${cleanNip}</Nip></root>`
    });

    const xmlResult = searchResult[0].DaneSzukajPodmiotyResult;

    // Wyloguj się
    await client.WylogujAsync({
      pIdentyfikatorSesji: sessionId
    });

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
