import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  rational, fmt, decimal, add, sub, mul, div, neg, pow, compare,
  matchingLaw, factorialCumulants, bernoulli, recoverBernoulli,
} from '../math.mjs';

const fixtures = JSON.parse(await readFile(new URL('./fixtures.json', import.meta.url), 'utf8'));

test('exact parsing, canonical signs, and arithmetic avoid decimal rounding', () => {
  assert.equal(fmt(rational('0.30')), '3/10');
  assert.equal(fmt(rational('-6/-8')), '3/4');
  assert.equal(fmt(rational('.125')), '1/8');
  assert.equal(fmt(rational('-0')), '0');
  assert.equal(fmt(add('0.1', '0.2')), '3/10');
  assert.equal(fmt(sub('1/3', '1/2')), '-1/6');
  assert.equal(fmt(mul('-2/3', '9/10')), '-3/5');
  assert.equal(fmt(div('3/7', '-2/5')), '-15/14');
  assert.equal(fmt(neg('-2/5')), '2/5');
  assert.equal(fmt(pow('-2/3', 3)), '-8/27');
  assert.equal(compare('9007199254740993/9007199254740992', 1), 1);
  assert.ok(Object.isFrozen(rational('1/3')));
});

test('decimal text is display-only and rounds signs and carry correctly', () => {
  assert.equal(decimal('1/8', 2), '0.13');
  assert.equal(decimal('-1/8', 2), '-0.13');
  assert.equal(decimal('999/1000', 2), '1.00');
  assert.equal(decimal('-1/1000', 2), '0.00');
  assert.equal(decimal('1/3', 6), '0.333333');
  assert.equal(decimal('3/2', 0), '2');
});

test('malformed or approximate inputs and resource limits fail explicitly', () => {
  for (const value of ['', 'NaN', 'Infinity', '1e-2', '1/0', '2//3', '1 2', '9'.repeat(129), true, null, 0.3, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1, { n: 1, d: 2 }]) {
    assert.throws(() => rational(value), String(value));
  }
  assert.throws(() => div(1, 0));
  assert.throws(() => decimal(1, 31));
  assert.throws(() => decimal(1, -1));
  assert.throws(() => pow(2, 101));
  for (const degree of [-1, 9, 1.5, '3', true]) assert.throws(() => matchingLaw(degree, '1/2'));
  for (const strength of ['-1/10', '11/10']) assert.throws(() => matchingLaw(3, strength));
  for (const law of [[], [0], ['1/2', '1/3'], [-1, 2], Array(10).fill('1/10')]) {
    assert.throws(() => factorialCumulants(law, 4));
  }
  assert.throws(() => factorialCumulants([1], 11));
  assert.throws(() => factorialCumulants([1], 1, '-1/100'));
  const sparseLaw = [1];
  sparseLaw.length = 2;
  assert.throws(() => factorialCumulants(sparseLaw, 2));
  assert.throws(() => bernoulli('1001/1000'));
});

test('every browser result matches the independently executed installed Python package', () => {
  assert.equal(fixtures.oracle, 'installed bounded_counts package');
  assert.equal(fixtures.cases.length, 327);
  for (const fixture of fixtures.cases) {
    if (fixture.family === 'matching') {
      assert.deepEqual(matchingLaw(fixture.degree, fixture.strength).map(fmt), fixture.law, fixture.name);
    }
    if (fixture.family === 'bernoulli') {
      assert.deepEqual(bernoulli(fixture.probability).map(fmt), fixture.law, fixture.name);
    }
    assert.deepEqual(
      factorialCumulants(fixture.law, fixture.order, fixture.background).map(fmt),
      fixture.cumulants,
      fixture.name,
    );
  }
});

test('zero, endpoint laws, and the exact sharpness demonstration retain their meaning', () => {
  assert.deepEqual(matchingLaw(0, '1/2').map(fmt), ['1']);
  assert.deepEqual(factorialCumulants([1], 0).map(fmt), ['0']);
  assert.deepEqual(factorialCumulants([1], 4, '3/2').map(fmt), ['0', '3/2', '0', '0', '0']);
  assert.deepEqual(factorialCumulants(bernoulli(1), 4).map(fmt), ['0', '1', '-1', '2', '-6']);
  const law = matchingLaw(3, '1/2');
  assert.deepEqual(law.map(fmt), ['29/48', '5/16', '1/16', '1/48']);
  assert.deepEqual(factorialCumulants(law, 4).map(fmt), ['0', '1/2', '0', '0', '-1/16']);
});

test('rational population inverses recover exact parameters including endpoints', () => {
  for (const fixture of fixtures.cases.filter(item => item.family === 'bernoulli')) {
    const result = recoverBernoulli(fixture.cumulants[1], fixture.cumulants[2]);
    assert.equal(result.feasible, true, fixture.name);
    assert.equal(fmt(result.p.exact), fixture.probability, fixture.name);
    assert.equal(fmt(result.b.exact), fixture.background, fixture.name);
  }
  const result = recoverBernoulli('4/5', '-9/100');
  assert.equal(result.p.expression, '3/10');
  assert.equal(result.b.expression, '1/2');
});

// Deliberately use raw cross-multiplication here, separate from the module's
// comparison and square-root code, to check the enclosure certificates.
function rawLessOrEqual(a, b) {
  return a.n * b.d <= b.n * a.d;
}

function rawSquare(a) {
  return { n: a.n * a.n, d: a.d * a.d };
}

test('irrational inverses provide rigorous outward rational enclosures', () => {
  for (const radicand of ['1/2', '2/3', '1/99991', '999999999999999999999999/1000000000000000000000000']) {
    const result = recoverBernoulli(1, neg(radicand));
    assert.equal(result.feasible, true);
    assert.equal(result.p.exact, null);
    assert.equal(result.b.exact, null);
    const square = rational(radicand);
    const [low, high] = result.p.enclosure;
    assert.ok(rawLessOrEqual(rawSquare(low), square));
    assert.ok(rawLessOrEqual(square, rawSquare(high)));
    assert.ok(rawLessOrEqual(low, high));
    assert.ok(rawLessOrEqual(sub(high, low), rational('1/1000000000000000000000000')));
    assert.equal(fmt(result.b.enclosure[0]), fmt(sub(1, high)));
    assert.equal(fmt(result.b.enclosure[1]), fmt(sub(1, low)));
  }
});

test('feasibility is decided exactly even when decimal displays coincide', () => {
  for (const [mean, second] of [[1, '1/100'], [2, '-1001/1000'], [-1, 0], ['1/2', '-1/2']]) {
    const result = recoverBernoulli(mean, second);
    assert.equal(result.feasible, false);
    assert.ok(result.reason.length > 0);
  }
  const belowRoot = '707106781186547524400844/1000000000000000000000000';
  const aboveRoot = '707106781186547524400845/1000000000000000000000000';
  assert.equal(decimal(belowRoot, 12), decimal(aboveRoot, 12));
  assert.equal(recoverBernoulli(belowRoot, '-1/2').feasible, false);
  assert.equal(recoverBernoulli(aboveRoot, '-1/2').feasible, true);
  assert.equal(recoverBernoulli('999999999999999999999999/1000000000000000000000000', -1).feasible, false);
  assert.equal(recoverBernoulli(1, -1).feasible, true);
});
