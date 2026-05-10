// Node-based test runner for the MDRS calculator
// Usage:  node tests/run-tests.js
// Exit code: 0 if all pass, 1 if any fail

'use strict';

const path = require('path');
const fs = require('fs');

const calc = require('../calculator.js');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'test-cases.json'), 'utf-8'));

function approxEq(a, b, eps = 0.001) {
  return Math.abs(a - b) <= eps;
}

let passed = 0;
let failed = 0;
const failures = [];

for (const test of data.tests) {
  const r = calc.score(test.inputs);
  const e = test.expected;

  const checks = [
    ['composite', approxEq(r.composite, e.composite), r.composite, e.composite],
    ['baseTier', r.baseTier === e.baseTier, r.baseTier, e.baseTier],
    ['floorActive', r.floorActive === e.floorActive, r.floorActive, e.floorActive],
    ['promoterActive', r.promoterActive === e.promoterActive, r.promoterActive, e.promoterActive],
    ['finalTier', r.finalTier === e.finalTier, r.finalTier, e.finalTier],
  ];

  if (e.afterFloor) {
    checks.push(['afterFloor', r.afterFloor === e.afterFloor, r.afterFloor, e.afterFloor]);
  }

  const allOk = checks.every(c => c[1]);

  if (allOk) {
    passed++;
    console.log(`  PASS  ${test.name}`);
  } else {
    failed++;
    console.log(`  FAIL  ${test.name}`);
    for (const [field, ok, actual, expected] of checks) {
      if (!ok) {
        console.log(`        ${field}: expected ${expected}, got ${actual}`);
      }
    }
    failures.push(test.name);
  }
}

console.log('');
console.log(`${passed + failed} test(s); ${passed} passed; ${failed} failed.`);

if (failed > 0) {
  console.log('');
  console.log('Failed tests:');
  failures.forEach(f => console.log('  - ' + f));
  process.exit(1);
}
