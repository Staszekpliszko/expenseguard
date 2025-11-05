// backend/database.js
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const DB_PATH = path.join(__dirname, '..', '..', 'db', 'app.db');
function getDb() { return new sqlite3.Database(DB_PATH); }
module.exports = { getDb, DB_PATH };
