const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { CloudKMSClient } = require('@google-cloud/kms');

// Initialize KMS Client
// No need to initialize admin again if it's already done in index.js, but this makes the function self-contained.
if (admin.apps.length === 0) {
  admin.initializeApp();
}

const kmsClient = new CloudKMSClient();

// --- Configuration --- 
const projectId = 'us-oil-solutions-app';
const locationId = 'global';
const keyRingId = 'api-key-ring';
const keyId = 'uso-api-key-ring';
// ------------------

const kmsKeyName = kmsClient.cryptoKeyPath(projectId, locationId, keyRingId, keyId);

// A simple in-memory cache for decrypted keys to reduce KMS calls and improve performance.
const keyCache = new Map();
const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

/**
 * Decrypts a base64-encoded ciphertext using Cloud KMS.
 * @param {string} ciphertext The base64-encoded encrypted key.
 * @returns {Promise<string>} The plaintext decrypted key.
 */
async function decryptApiKey(ciphertext) {
  try {
    const [result] = await kmsClient.decrypt({
      name: kmsKeyName,
      ciphertext: Buffer.from(ciphertext, 'base64'),
    });
    return result.plaintext.toString();
  } catch (error) {
    console.error('KMS Decryption failed:', error);
    throw new Error('Failed to decrypt API key.');
  }
}

/**
 * Securely retrieves and decrypts an API key from Firestore.
 * Uses an in-memory cache to avoid excessive KMS decryption calls.
 * @param {string} service The service identifier (e.g., 'usda').
 * @param {string} environment The environment (e.g., 'production').
 * @returns {Promise<string>} The decrypted API key.
 */
async function getApiKey(service, environment = 'production') {
  const cacheKey = `${service}_${environment}`;

  // 1. Check cache first
  if (keyCache.has(cacheKey)) {
    const cached = keyCache.get(cacheKey);
    if (Date.now() - cached.timestamp < CACHE_TIMEOUT_MS) {
      return cached.key;
    }
  }

  // 2. If not in cache or expired, fetch from Firestore
  const db = admin.firestore();
  const snapshot = await db
    .collection('api_keys')
    .where('service', '==', service)
    .where('environment', '==', environment)
    .where('status', '==', 'active')
    .orderBy('addedDate', 'desc') // Get the most recently added key
    .limit(1)
    .get();

  if (snapshot.empty) {
    throw new Error(`No active API key found for service: ${service} in environment: ${environment}`);
  }

  const keyDoc = snapshot.docs[0];
  const { encryptedKey } = keyDoc.data();

  // 3. Decrypt the key
  const decryptedKey = await decryptApiKey(encryptedKey);

  // 4. Cache the decrypted key
  keyCache.set(cacheKey, {
    key: decryptedKey,
    timestamp: Date.now(),
  });

  // 5. Asynchronously update usage stats (don't block the return)
  keyDoc.ref.update({
    lastUsed: admin.firestore.FieldValue.serverTimestamp(),
    usageCount: admin.firestore.FieldValue.increment(1),
  }).catch(err => console.error("Failed to update key usage stats:", err));

  return decryptedKey;
}

/**
 * Example HttpsCallable function to fetch data from the USDA NASS API.
 */
exports.fetchNassData = functions.https.onCall(async (data, context) => {
  // We could add role-based access checks here if needed
  // if (!context.auth) { ... }
  
  try {
    const apiKey = await getApiKey('usda', 'production');

    // Use a dynamic import for 'node-fetch' which is an ES module
    const fetch = (await import('node-fetch')).default;

    // Parameters from the client, with defaults
    const year = data.year || '2024';
    const commodity = data.commodity || 'SOYBEANS';

    const params = new URLSearchParams({
        key: apiKey,
        source_desc: 'SURVEY',
        sector_desc: 'CROPS',
        group_desc: 'FIELD CROPS',
        commodity_desc: commodity,
        short_desc: `${commodity} - PROGRESS, PLANTED`,
        agg_level_desc: 'NATIONAL',
        year: year,
        format: 'JSON'
    });

    const response = await fetch(`https://quickstats.nass.usda.gov/api/api_GET/?${params.toString()}`);
    if (!response.ok) {
      throw new functions.https.HttpsError('third-party-unavailable', `NASS API returned status ${response.status}`);
    }

    const resultData = await response.json();
    return resultData.data || [];

  } catch (error) {
    console.error("Error fetching NASS data:", error);
    if (error instanceof functions.https.HttpsError) {
      throw error; // Re-throw HttpsError
    }
    throw new functions.https.HttpsError('internal', 'An unexpected error occurred while fetching NASS data.', error.message);
  }
});
