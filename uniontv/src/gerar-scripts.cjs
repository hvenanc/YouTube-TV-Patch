/* Regenerate all four fixed-size blocks; never minify across their boundaries.
 * NODE_PATH=MINIFIER/node_modules node fontes/gerar-scripts.cjs ORIGINAL_LIBCOBALT_SO OUTPUT
 * Dependencies: terser@5.44.0 (includes acorn).
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const acorn = require('acorn');
const terser = require('terser');
const bounds = [[0, 305], [305, 594], [594, 10851], [10851, 22137]];
const options = {ecma: 2017, compress: {passes: 2}, mangle: true, format: {ascii_only: true}};

function shareStrings(src) {
  const ast = acorn.parse(src, {ecmaVersion: 'latest'}), literals = [];
  function walk(node, parent) {
    if (!node || typeof node !== 'object') return;
    if (node.type === 'Literal' && typeof node.value === 'string' && node.value.length >= 13 &&
        !(parent.type === 'Property' && parent.key === node && !parent.computed)) literals.push(node);
    for (const key in node) {
      const value = node[key];
      if (Array.isArray(value)) value.forEach(child => walk(child, node));
      else if (value && typeof value === 'object') walk(value, node);
    }
  }
  walk(ast, null);
  const groups = new Map(), declarations = [], edits = [];
  for (const node of literals) {
    if (!groups.has(node.value)) groups.set(node.value, []);
    groups.get(node.value).push(node);
  }
  for (const [value, nodes] of groups) {
    if (nodes.length < 2 || value.length * (nodes.length - 1) < 25) continue;
    const name = '__utvConst' + declarations.length;
    if (src.includes(name)) throw Error('Generated identifier collision');
    declarations.push(name + '=' + JSON.stringify(value));
    for (const node of nodes) edits.push({...node, name});
  }
  let result = src;
  for (const edit of edits.sort((a, b) => b.start - a.start)) {
    result = result.slice(0, edit.start) + edit.name + result.slice(edit.end);
  }
  return declarations.length ? '(function(){"use strict";var ' + declarations.join(',') + ';' + result + '}).call(this);' : result;
}

(async () => {
  const library = fs.readFileSync(process.argv[2]);
  const raw = library.subarray(0x853944, 0x853944 + 22137);
  if (crypto.createHash('sha256').update(raw).digest('hex') !== '9ce14385832aabc7fd36569d89ceeef0e2dc589c8136386396fa6ba580a09300') throw Error('Unexpected original scripts');
  const output = [];
  for (let index = 0; index < bounds.length; index++) {
    const [start, end] = bounds[index], src = raw.subarray(start, end).toString('ascii');
    if (!src.startsWith("'use strict';") || !src.endsWith('\n')) throw Error('Invalid block boundary');
    if (index < 2) { output.push(src); continue; }
    const original = await terser.minify(shareStrings(src), options);
    const hook = await terser.minify(fs.readFileSync(path.join(__dirname, index === 2 ? 'parse.js' : 'stringify.js'), 'utf8'), options);
    const modified = original.code + ';' + hook.code;
    if (Buffer.byteLength(modified, 'ascii') > end - start) throw Error('Block exceeds original size: ' + index);
    // Validate each unit independently, as the native loader does.
    acorn.parse(modified, {ecmaVersion: 'latest'});
    output.push(modified.padEnd(end - start, ' '));
    console.log('Block', index, 'used', modified.length, 'of', end - start, 'bytes');
  }
  const result = Buffer.from(output.join(''), 'ascii');
  if (result.length !== raw.length) throw Error('Changed total size');
  fs.writeFileSync(process.argv[3], result);
})().catch(error => { console.error(error); process.exitCode = 1; });
