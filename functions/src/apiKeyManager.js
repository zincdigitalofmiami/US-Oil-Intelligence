const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { CloudKMSClient } = require('@google-cloud/kms');

// Initialize Firebase Admin SDK and KMS Client
admin.initializeApp();
const kmsClient = new CloudKMSClient();

// --- Configuration --- 
const projectId = 'us-oil-solutions-app';
const locationId = 'global'; // As seen in the screenshot
const keyRingId = 'api-key-ring';
const keyId = 'uso-api-key-ring';
// ------------------

const kmsKeyName = kmsClient.cryptoKeyPath(projectId, locationId, keyRingId, keyId);

/**
 * Encrypts the given plaintext API key using Cloud KMS.
 * @param {string} plaintext The API key to encrypt.
 * @returns {Promise<string>} The base64-encoded encrypted key.
 */
async function encryptApiKey(plaintext) {
  try {
    const [result] = await kmsClient.encrypt({
      name: kmsKeyName,
      plaintext: Buffer.from(plaintext),
    });
    return result.ciphertext.toString('base64');
  } catch (error) {
    console.error('KMS Encryption failed:', error);
    throw new functions.https.HttpsError('internal', 'Failed to encrypt the API key.');
  }
}

/**
 * An HttpsCallable function to securely add a new API key.
 * It encrypts the key and stores it in Firestore.
 */
exports.addApiKey = functions.https.onCall(async (data, context) => {
  // 1. Authentication & Authorization Check
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'The function must be called while authenticated.');
  }

  const userDoc = await admin.firestore().collection('users').doc(context.auth.uid).get();
  const userRoles = userDoc.data().roles || [];

  if (!userRoles.includes('admin')) {
    throw new functions.https.HttpsError('permission-denied', 'The caller does not have permission to execute this action.');
  }

  // 2. Data Validation
  const { name, service, apiKey, environment } = data;
  if (!name || !service || !apiKey || !environment) {
    throw new functions.https.HttpsError('invalid-argument', 'The function must be called with arguments: "name", "service", "apiKey", "environment".');
  }

  // 3. Encrypt the API Key
  const encryptedKey = await encryptApiKey(apiKey);

  const db = admin.firestore();
  const batch = db.batch();

  // 4. Store in Firestore
  const keyDocRef = db.collection('api_keys').doc();
  batch.set(keyDocRef, {
    name,
    service,
    encryptedKey, // Store the encrypted key
    environment,
    status: 'active',
    addedBy: context.auth.uid,
    addedDate: admin.firestore.FieldValue.serverTimestamp(),
    lastUsed: null,
    usageCount: 0,
  });

  // 5. Create an Audit Log Entry
  const auditLogRef = db.collection('api_key_audit_log').doc();
  batch.set(auditLogRef, {
    action: 'key_added',
    keyId: keyDocRef.id,
    performedBy: context.auth.uid,
    timestamp: admin.firestore.FieldValue.serverTimestamp(),
    result: 'success',
    ipAddress: context.rawRequest.ip, // Best-effort IP logging
    details: { name, service, environment }
  });

  // 6. Commit the batch
  await batch.commit();

  return { success: true, keyId: keyDocRef.id };
});
