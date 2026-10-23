import { rational, fmt, decimal, add, sub, div, compare, bernoulli, matchingLaw, factorialCumulants, recoverBernoulli } from './math.mjs';

const $ = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const defaults = { source: 'bernoulli', background: 50, degree: 3, strength: 50, exact: false, revealed: false, mean: '4/5', k2: '-9/100' };
let state = { ...defaults };
let lastRecovery = null;
let recoveryComputed = true;
let recoveryFeedbackTimer;
const sources = {
  bernoulli: { name: 'Bernoulli', law: bernoulli('3/10') },
  'three-count': { name: 'Three-count source', law: ['1/2', '1/4', '0', '1/4'].map(rational) },
  matching: { name: 'Generalized matching law', law: matchingLaw(3, '1/2') },
};
const escape = text => String(text).replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
const trimDecimal = text => text.replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');
function display(value, digits = 6) {
  if (state.exact) return fmt(value);
  const text = trimDecimal(decimal(value, digits));
  return `${compare(value, rational(text)) === 0 ? '' : '≈ '}${text}`;
}
const toNumber = value => Number(decimal(value, 15)); // Display geometry only; no sign decisions.
const background = () => rational(`${state.background}/100`);
const strength = () => rational(`${state.strength}/100`);
function node(tag, attributes = {}, text = '') {
  const element = document.createElementNS(NS, tag);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, String(value)));
  if (text) element.textContent = text;
  return element;
}

function restoreUrl() {
  const params = new URL(location.href).searchParams;
  if (Object.hasOwn(sources, params.get('source'))) state.source = params.get('source');
  for (const [key, low, high, step] of [['background', 0, 300, 5], ['degree', 1, 8, 1], ['strength', 10, 90, 10]]) {
    const text = params.get(key);
    if (text !== null && /^\d{1,3}$/.test(text)) {
      const value = Number(text);
      if (value >= low && value <= high && value % step === 0) state[key] = value;
    }
  }
  state.exact = params.get('exact') === '1';
  state.revealed = params.get('revealed') === '1';
  for (const key of ['mean', 'k2']) {
    if (params.has(key) && params.get(key).length <= 64) state[key] = params.get(key);
  }
}
function syncUrl() {
  const url = new URL(location.href);
  url.search = '';
  Object.entries(state).forEach(([key, value]) => {
    if (value !== defaults[key]) url.searchParams.set(key, typeof value === 'boolean' ? (value ? '1' : '0') : String(value));
  });
  history.replaceState(null, '', url);
}
function controls() {
  $('source-select').value = state.source;
  $('background').value = String(state.background);
  $('degree').value = String(state.degree);
  $('strength').value = String(state.strength);
  $('mean-input').value = state.mean;
  $('k2-input').value = state.k2;
  $('exact-toggle').setAttribute('aria-pressed', String(state.exact));
  $('exact-toggle').textContent = state.exact ? 'Show decimals' : 'Show fractions';
}

/** Rounded analytic probabilities for drawing only; the final bucket retains the tail. */
function plottedProbabilities(law, b) {
  const source = Array.from({ length: 14 }, (_, k) => k < law.length ? toNumber(law[k]) : 0);
  const rate = toNumber(b);
  const poisson = [Math.exp(-rate)];
  for (let k = 1; k < 13; k += 1) poisson.push(poisson[k - 1] * rate / k);
  const observed = Array.from({ length: 13 }, (_, k) => law.reduce((sum, mass, j) => sum + (j <= k ? toNumber(mass) * poisson[k - j] : 0), 0));
  observed.push(Math.max(0, 1 - observed.reduce((sum, value) => sum + value, 0)));
  return { source, observed };
}
function renderDistribution(law, b) {
  const values = plottedProbabilities(law, b);
  const svg = $('signal-chart');
  svg.replaceChildren(node('title', { id: 'signal-chart-title' }, 'Source and observed count probabilities'), node('desc', { id: 'signal-chart-desc' }, `The source has support zero through ${law.length - 1}. The observed law adds independent Poisson background with mean ${fmt(b)}. The last bucket collects counts 13 and above. A text table follows.`));
  const left = 80, right = 688, top = 35, bottom = 224;
  const peak = Math.max(...values.source, ...values.observed);
  const max = Math.min(1, Math.max(0.2, Math.ceil(peak * 5) / 5));
  for (let tick = 0; tick <= 4; tick += 1) {
    const p = max * tick / 4, y = bottom - (bottom - top) * tick / 4;
    svg.append(node('line', { x1: left, x2: right, y1: y, y2: y, stroke: '#dde3db', 'stroke-width': 1 }));
    svg.append(node('text', { x: left - 9, y: y + 3, 'text-anchor': 'end', class: 'svg-axis' }, `${Math.round(p * 100)}%`));
  }
  const width = (right - left) / 14;
  values.source.forEach((p, k) => {
    const x = left + width * (k + 0.5);
    for (const [value, fill, dx] of [[p, '#176b60', -11], [values.observed[k], '#ae452a', 1]]) {
      const height = value / max * (bottom - top);
      const rect = node('rect', { x: x + dx, y: bottom - height, width: 10, height, rx: 1.5, fill, class: 'chart-bar' });
      rect.append(node('title', {}, `${dx < 0 ? 'Source' : 'Observed'} count ${k === 13 ? '13+' : k}: approximately ${value.toFixed(6)}`));
      svg.append(rect);
    }
    svg.append(node('text', { x, y: bottom + 20, 'text-anchor': 'middle', class: 'svg-axis' }, k === 13 ? '13+' : String(k)));
  });
  return values;
}
function renderSignal() {
  const { law } = sources[state.source];
  const b = background();
  const cumulants = factorialCumulants(law, 4, b);
  const original = factorialCumulants(law, 4);
  $('background-output').value = state.exact ? fmt(b) : decimal(b, 2);
  $('background').setAttribute('aria-valuetext', `${fmt(b)} expected background counts per window`);
  for (let order = 1; order <= 3; order += 1) $('signal-k' + order).textContent = display(cumulants[order]);
  const plotted = renderDistribution(law, b);
  $('signal-values').innerHTML = `<p>Source masses for counts 0 through ${law.length - 1}: <strong>${law.map(fmt).join(', ')}</strong>. The observed count is unbounded when b &gt; 0.</p><table><caption>Exact factorial cumulants of the full laws</caption><thead><tr><th scope="col">Order</th><th scope="col">Source X</th><th scope="col">Observed Y</th></tr></thead><tbody>${cumulants.slice(1).map((q, i) => `<tr><th scope="row">${i + 1}</th><td>${fmt(original[i + 1])}</td><td>${fmt(q)}</td></tr>`).join('')}</tbody></table><table><caption>Plotted probabilities (rounded to six places)</caption><thead><tr><th scope="col">Count</th><th scope="col">Source X</th><th scope="col">Observed Y</th></tr></thead><tbody>${plotted.source.map((p, k) => `<tr><th scope="row">${k === 13 ? '13+' : k}</th><td>${p.toFixed(6)}</td><td>${plotted.observed[k].toFixed(6)}</td></tr>`).join('')}</tbody></table><p>Cumulants are computed with exact rational arithmetic from the full model, independently of the rounded plot and its tail bucket.</p>`;
}

function miniChart(id, law, color) {
  const svg = $(id);
  svg.replaceChildren(node('title', {}, `${id === 'source-a-chart' ? 'Model A' : 'Model B'} source masses: ${law.map(fmt).join(', ')}`));
  const width = 240 / law.length;
  svg.append(node('line', { x1: 8, x2: 252, y1: 67, y2: 67, stroke: '#68887a', 'stroke-width': 1 }));
  law.forEach((mass, k) => {
    const height = toNumber(mass) * 58, x = 10 + width * k;
    svg.append(node('rect', { x: x + width * 0.16, y: 67 - height, width: width * 0.68, height, rx: 1, fill: color }));
    svg.append(node('text', { x: x + width * .5, y: 84, fill: '#c2d5cb', 'font-size': 10, 'text-anchor': 'middle', 'font-family': 'Arial,sans-serif' }, String(k)));
  });
}
function renderSharpness() {
  const h = strength(), degree = state.degree;
  const a = matchingLaw(degree, h), b = Array.from({ length: degree + 1 }, (_, i) => rational(i === 0 ? 1 : 0));
  const ka = factorialCumulants(a, degree + 1), kb = factorialCumulants(b, degree + 1, h);
  const equal = ka.map((value, order) => compare(value, kb[order]) === 0);
  if (!equal.slice(1, degree + 1).every(Boolean) || equal[degree + 1]) {
    throw new Error('The exact sharpness comparison failed its defining identities.');
  }
  const comparison = order => `<span class="equal-sign" aria-hidden="true">${equal[order] ? '=' : '≠'}</span> ${equal[order] ? 'Equal' : 'Different'}`;
  const fractionCell = value => fmt(value).replace('/', '/<wbr>');
  $('strength-output').value = fmt(h);
  $('strength').setAttribute('aria-valuetext', fmt(h));
  $('orders-caption').textContent = `Through order ${state.revealed ? degree + 1 : degree}`;
  miniChart('source-a-chart', a, '#92c7ad');
  miniChart('source-b-chart', b, '#f5b491');
  $('sharpness-rows').innerHTML = Array.from({ length: degree }, (_, i) => `<tr><td>κ<sub>${i + 1}</sub></td><td>${fractionCell(ka[i + 1])}</td><td>${fractionCell(kb[i + 1])}</td><td>${comparison(i + 1)}</td></tr>`).join('') + (state.revealed ? `<tr id="reveal-row" class="revealed-row"><td>κ<sub>${degree + 1}</sub></td><td>${fractionCell(ka[degree + 1])}</td><td>${fractionCell(kb[degree + 1])}</td><td>${comparison(degree + 1)}</td></tr>` : `<tr id="reveal-row" class="concealed-row"><td>κ<sub>${degree + 1}</sub></td><td aria-label="Not yet revealed">—</td><td aria-label="Not yet revealed">—</td><td>Reveal below</td></tr>`);
  $('reveal').setAttribute('aria-expanded', String(state.revealed));
  $('reveal').setAttribute('aria-controls', 'reveal-row');
  $('reveal').innerHTML = `${state.revealed ? 'Hide' : 'Reveal'} order ${degree + 1} <span aria-hidden="true">${state.revealed ? '−' : '↗'}</span>`;
  $('sharpness-result').textContent = state.revealed ? `Order ${degree + 1} separates the pair: ${fmt(ka[degree + 1])} versus 0. Lower orders were not enough.` : `${degree === 1 ? 'The means agree.' : `Orders 1 through ${degree} agree.`} These quantities do not distinguish the sources.`;
  $('sharpness-values').innerHTML = `<p>Exact source probabilities, indexed from count 0:</p><strong>Model A</strong><code>(${a.map(fmt).join(', ')})</code><strong>Model B</strong><code>(${b.map(fmt).join(', ')})</code><p>The observed mean is h = ${fmt(h)} in both models. ${degree === 1 ? 'For D = 1 there are no orders from 2 through D; the second factorial cumulant is the first higher-order quantity.' : `Orders 2 through ${degree} are zero in both models.`} The first difference is κ<sub>${degree + 1}</sub> = −h<sup>${degree + 1}</sup> versus zero.</p>`;
}

function descriptorDisplay(descriptor) {
  if (descriptor.exact !== null) return display(descriptor.exact);
  return `≈ ${trimDecimal(decimal(div(add(descriptor.enclosure[0], descriptor.enclosure[1]), 2), 6))}`;
}
function expression(descriptor) { return descriptor.expression.replaceAll('sqrt', '√'); }
function emptyOutputs() { return '<output id="recovered-p" hidden>Unavailable</output><output id="recovered-b" hidden>Unavailable</output>'; }
function renderRecovery() {
  const container = $('recovery-result');
  $('mean-input').removeAttribute('aria-invalid');
  $('k2-input').removeAttribute('aria-invalid');
  if (!recoveryComputed) {
    container.className = 'recovery-result pending';
    container.innerHTML = `<p>Inputs changed. Select “Recover the parameters” to calculate this pair.</p>${emptyOutputs()}`;
    return;
  }
  let result;
  try {
    result = recoverBernoulli(state.mean, state.k2);
    lastRecovery = result;
  } catch (error) {
    lastRecovery = { feasible: false, inputError: true, reason: error.message };
    container.className = 'recovery-result invalid';
    container.innerHTML = `<div class="result-heading"><span class="status-dot"></span>Enter valid exact inputs</div><p>${escape(error.message)}</p>${emptyOutputs()}`;
    for (const [id, value] of [['mean-input', state.mean], ['k2-input', state.k2]]) {
      try { rational(value); } catch { $(id).setAttribute('aria-invalid', 'true'); }
    }
    return;
  }
  if (!result.feasible) {
    container.className = 'recovery-result invalid';
    container.innerHTML = `<div class="result-heading"><span class="status-dot"></span>Outside this Bernoulli–Poisson model</div><p>${escape(result.reason)} No admissible parameter pair is returned.</p>${emptyOutputs()}`;
    return;
  }
  container.className = 'recovery-result';
  const exact = result.p.exact !== null;
  container.innerHTML = `<div class="result-heading"><span class="status-dot"></span>Unique parameters under the stated model</div><div class="result-values"><div><span class="result-label">Source count probability <b>p</b></span><output id="recovered-p">${escape(descriptorDisplay(result.p))}</output><span class="exact-expression">Exact: ${escape(expression(result.p))}</span></div><div><span class="result-label">Mean background count <b>b</b></span><output id="recovered-b">${escape(descriptorDisplay(result.b))}</output><span class="exact-expression">Exact: ${escape(expression(result.b))}</span></div></div><p class="result-equation">${exact ? `Check: p + b = ${fmt(rational(state.mean))} and −p² = ${fmt(rational(state.k2))}. Both reproduce the inputs exactly.` : `The radical expressions are exact. Decimal displays are rounded; feasibility is decided using rational comparisons, with outward rational bounds on each square root.`}</p>`;
}
function renderAll() {
  controls();
  renderSignal();
  renderSharpness();
  renderRecovery();
}
function resetRecoveryFeedback(message = 'Example result shown below. Recover to check these inputs.') {
  clearTimeout(recoveryFeedbackTimer);
  $('recover-button').innerHTML = 'Recover the parameters <span aria-hidden="true">→</span>';
  $('recovery-feedback').textContent = message;
}
function submitRecovery() {
  // Read the fields at submission too: autofill and browser restoration need not
  // dispatch the input events that maintain the pending state.
  state.mean = $('mean-input').value;
  state.k2 = $('k2-input').value;
  recoveryComputed = true;
  renderRecovery();
  syncUrl();
  resetRecoveryFeedback(lastRecovery.feasible
    ? 'Calculation complete. Recovered parameters are shown below.'
    : 'Inputs checked. See the explanation below.');
  $('recover-button').innerHTML = `${lastRecovery.feasible ? 'Parameters recovered' : 'Inputs checked'} <span aria-hidden="true">✓</span>`;
  recoveryFeedbackTimer = setTimeout(() => {
    $('recover-button').innerHTML = 'Recover the parameters <span aria-hidden="true">→</span>';
  }, 2000);
  $('recovery-result').scrollIntoView({ block: 'nearest', behavior: 'instant' });
}
function serializeDescriptor(descriptor) {
  return { exact_rational: descriptor.exact === null ? null : fmt(descriptor.exact), exact_expression: descriptor.expression, outward_rational_enclosure: descriptor.enclosure.map(fmt) };
}
function calculationRecord() {
  const { law, name } = sources[state.source], h = strength();
  const a = matchingLaw(state.degree, h), b = Array.from({ length: state.degree + 1 }, (_, i) => rational(i === 0 ? 1 : 0));
  return {
    schema_version: 1,
    title: 'Bounded Counts — exact population calculations',
    scope: 'Illustrative model calculations, not measured data, physical validation or a general-D reconstruction solver.',
    assumptions: ['Known nonnegative integer source support bound.', 'Source and fixed-rate Poisson background are independent.', 'Inputs are exact population quantities, not sample estimates.'],
    settings: { ...state },
    signal: { source: name, support_bound: law.length - 1, probabilities: law.map(fmt), background: fmt(background()), source_factorial_cumulants_1_to_4: factorialCumulants(law, 4).slice(1).map(fmt), observed_factorial_cumulants_1_to_4: factorialCumulants(law, 4, background()).slice(1).map(fmt) },
    sharpness: { support_bound: state.degree, strength: fmt(h), model_a: { probabilities: a.map(fmt), background: '0', observed_factorial_cumulants: factorialCumulants(a, state.degree + 1).slice(1).map(fmt) }, model_b: { probabilities: b.map(fmt), background: fmt(h), observed_factorial_cumulants: factorialCumulants(b, state.degree + 1, h).slice(1).map(fmt) }, family_reference: 'https://arxiv.org/abs/1411.1165' },
    recovery: { observed_mean_input: state.mean, second_factorial_cumulant_input: state.k2, model: 'Bernoulli source plus independent fixed-rate Poisson background', ...(!recoveryComputed ? { status: 'inputs_changed_not_calculated' } : lastRecovery.feasible ? { status: 'compatible', p: serializeDescriptor(lastRecovery.p), b: serializeDescriptor(lastRecovery.b) } : { status: lastRecovery.inputError ? 'invalid_input' : 'incompatible', reason: lastRecovery.reason }) },
    implementation: 'BigInt rational calculations; square-root enclosures. Plot probabilities use rounded floating-point evaluations and are not used for identification decisions.',
    proof: 'https://github.com/thequantumfalcon/bounded-count-identifiability/blob/main/docs/theorem.md',
    process_disclosure: 'https://github.com/thequantumfalcon/bounded-count-identifiability/blob/main/PROVENANCE.md',
    sharing_url: location.href,
  };
}

$('source-select').addEventListener('change', event => { state.source = event.target.value; renderSignal(); syncUrl(); });
$('background').addEventListener('input', event => { state.background = Number(event.target.value); renderSignal(); syncUrl(); });
$('exact-toggle').addEventListener('click', () => { state.exact = !state.exact; controls(); renderSignal(); renderRecovery(); syncUrl(); });
for (const id of ['degree', 'strength']) $(id).addEventListener(id === 'strength' ? 'input' : 'change', event => { state[id] = Number(event.target.value); state.revealed = false; renderSharpness(); syncUrl(); });
$('reveal').addEventListener('click', () => { state.revealed = !state.revealed; renderSharpness(); syncUrl(); });
for (const [id, key] of [['mean-input', 'mean'], ['k2-input', 'k2']]) $(id).addEventListener('input', event => { state[key] = event.target.value; recoveryComputed = false; lastRecovery = null; resetRecoveryFeedback('Ready to calculate the changed inputs.'); renderRecovery(); syncUrl(); });
$('recover').addEventListener('submit', event => { event.preventDefault(); submitRecovery(); });
for (const [id, mean, k2] of [['preset-default', '4/5', '-9/100'], ['preset-boundary', '1', '-1'], ['preset-invalid', '1/10', '-9/100']]) $(id).addEventListener('click', () => { state.mean = mean; state.k2 = k2; controls(); submitRecovery(); });
$('reset-demo').addEventListener('click', () => { state = { ...defaults }; recoveryComputed = true; resetRecoveryFeedback(); renderAll(); syncUrl(); $('export-status').textContent = 'Default examples restored.'; });
$('download-json').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(calculationRecord(), null, 2) + '\n'], { type: 'application/json' }));
  const a = document.createElement('a');
  a.href = url; a.download = 'bounded-count-calculation.json'; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('export-status').textContent = 'Exact values and assumptions downloaded.';
});
$('copy-link').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(location.href); $('export-status').textContent = 'Link copied with these settings.'; }
  catch { $('export-status').textContent = 'Copy the address from your browser to share these settings.'; }
});
window.addEventListener('popstate', () => { state = { ...defaults }; restoreUrl(); recoveryComputed = true; resetRecoveryFeedback('Select Recover to check the restored inputs.'); renderAll(); });

try {
  restoreUrl(); renderAll();
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      document.querySelectorAll('.site-header nav a').forEach(a => { if (a.hash === `#${entry.target.id}`) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    }
  }, { rootMargin: '-15% 0px -55% 0px', threshold: 0 });
  document.querySelectorAll('[data-panel]').forEach(section => observer.observe(section));
  document.body.dataset.ready = 'true';
} catch (error) {
  const note = document.createElement('p'); note.className = 'loading-error'; note.setAttribute('role', 'alert');
  note.textContent = 'The demonstration could not initialize. Please reload, or use the linked written proof and Python example.';
  $('main').prepend(note);
  console.error(error);
}
