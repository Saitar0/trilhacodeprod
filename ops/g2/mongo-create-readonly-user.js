// REVIEW ONLY — MongoDB staging-only read account, never run without explicit authorization.
// Run with mongosh authenticated as the staging MongoDB root administrator.
// Password is prompted locally and never logged or stored in this repository.
'use strict';
const databaseName = 'trilhacode_staging';
const accountName = 'trilhacode_g2_ro';
const database = db.getSiblingDB(databaseName);
if (db.getName() !== 'admin') {
  throw new Error('G2: authenticate with admin database; refusing operation');
}
if (database.getUser(accountName) !== null) {
  throw new Error('G2: user already exists; review manually rather than modify roles/password');
}
const password = passwordPrompt();
if (!password || password.length < 32) {
  throw new Error('G2: require a unique, random password of at least 32 characters');
}
database.createUser({
  user: accountName,
  pwd: password,
  roles: [{ role: 'read', db: databaseName }],
  mechanisms: ['SCRAM-SHA-256']
});
const created = database.getUser(accountName);
if (!created || created.roles.length !== 1 ||
    created.roles[0].role !== 'read' || created.roles[0].db !== databaseName) {
  throw new Error('G2: account verification failed; investigate access before further steps');
}
print('G2: dedicated staging read-only MongoDB user created and verified (no secret printed)');
