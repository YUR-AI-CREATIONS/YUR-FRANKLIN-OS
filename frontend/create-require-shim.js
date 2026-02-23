const { createRequire } = require('module');
if (typeof global.createRequire !== 'function') {
  global.createRequire = createRequire;
}
