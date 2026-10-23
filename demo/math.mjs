/** Exact arithmetic for the synthetic population examples.
 *
 * This module illustrates the stated bounded-count model. It is not a
 * general-D inverse solver or a formally verified implementation. Decimal
 * conversions are for display; every feasibility decision uses rationals.
 */

const MAX_TEXT_LENGTH = 128;
const MAX_DEGREE = 8;
const MAX_ORDER = 10;
const ZERO = Object.freeze({ n: 0n, d: 1n });
const ONE = Object.freeze({ n: 1n, d: 1n });

function abs(n) {
  return n < 0n ? -n : n;
}

function gcd(a, b) {
  a = abs(a);
  b = abs(b);
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

function make(n, d = 1n) {
  if (d === 0n) throw new RangeError('A rational denominator cannot be zero.');
  if (n === 0n) return ZERO;
  if (d < 0n) [n, d] = [-n, -d];
  const common = gcd(n, d);
  return Object.freeze({ n: n / common, d: d / common });
}

/** Parse an exact integer, finite decimal, or fraction; never accept floats. */
export function rational(value) {
  if (typeof value === 'bigint') return make(value);
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) {
      throw new TypeError('Use an exact decimal or fraction string, not a floating-point number.');
    }
    return make(BigInt(value));
  }
  if (value !== null && typeof value === 'object') {
    if (typeof value.n === 'bigint' && typeof value.d === 'bigint') {
      return make(value.n, value.d);
    }
    throw new TypeError('A rational value requires BigInt numerator and denominator.');
  }
  if (typeof value !== 'string') throw new TypeError('Expected an exact rational value.');
  const text = value.trim();
  if (text.length === 0 || text.length > MAX_TEXT_LENGTH) {
    throw new RangeError(`An exact input must contain 1 to ${MAX_TEXT_LENGTH} characters.`);
  }
  if (/^[+-]?\d+\/[+-]?\d+$/.test(text)) {
    const [numerator, denominator] = text.split('/');
    return make(BigInt(numerator), BigInt(denominator));
  }
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(text)) {
    throw new TypeError('Use an integer, finite decimal, or fraction such as 3/10.');
  }
  const sign = text.startsWith('-') ? -1n : 1n;
  const unsigned = text.replace(/^[+-]/, '');
  const [whole, fractional = ''] = unsigned.split('.');
  return make(sign * BigInt(`${whole || '0'}${fractional}`), 10n ** BigInt(fractional.length));
}

export function fmt(value) {
  const q = rational(value);
  return q.d === 1n ? String(q.n) : `${q.n}/${q.d}`;
}

export function add(left, right) {
  const a = rational(left), b = rational(right);
  return make(a.n * b.d + b.n * a.d, a.d * b.d);
}

export function neg(value) {
  const q = rational(value);
  return make(-q.n, q.d);
}

export function sub(left, right) {
  return add(left, neg(right));
}

export function mul(left, right) {
  const a = rational(left), b = rational(right);
  return make(a.n * b.n, a.d * b.d);
}

export function div(left, right) {
  const a = rational(left), b = rational(right);
  if (b.n === 0n) throw new RangeError('Division by zero is undefined.');
  return make(a.n * b.d, a.d * b.n);
}

export function compare(left, right) {
  const a = rational(left), b = rational(right);
  const difference = a.n * b.d - b.n * a.d;
  return difference < 0n ? -1 : difference > 0n ? 1 : 0;
}

function boundedInteger(value, maximum, name) {
  if (!Number.isSafeInteger(value) || value < 0 || value > maximum) {
    throw new RangeError(`${name} must be an integer from 0 to ${maximum}.`);
  }
  return value;
}

export function pow(value, exponent) {
  boundedInteger(exponent, 100, 'Exponent');
  const q = rational(value);
  return make(q.n ** BigInt(exponent), q.d ** BigInt(exponent));
}

/** Rounded decimal text only. Ties round away from zero. */
export function decimal(value, digits = 6) {
  boundedInteger(digits, 30, 'Decimal places');
  const q = rational(value);
  const scale = 10n ** BigInt(digits);
  const scaled = abs(q.n) * scale;
  let rounded = scaled / q.d;
  if (2n * (scaled % q.d) >= q.d) rounded += 1n;
  const sign = q.n < 0n && rounded !== 0n ? '-' : '';
  if (digits === 0) return `${sign}${rounded}`;
  const text = rounded.toString().padStart(digits + 1, '0');
  return `${sign}${text.slice(0, -digits)}.${text.slice(-digits)}`;
}

function probability(value, name = 'Probability') {
  const q = rational(value);
  if (compare(q, ZERO) < 0 || compare(q, ONE) > 0) {
    throw new RangeError(`${name} must lie in [0, 1].`);
  }
  return q;
}

function factorial(n) {
  let result = 1n;
  for (let i = 2; i <= n; i += 1) result *= BigInt(i);
  return result;
}

function choose(n, k) {
  return factorial(n) / (factorial(k) * factorial(n - k));
}

export function bernoulli(value) {
  const p = probability(value);
  return [sub(ONE, p), p];
}

/** Established generalized matching family, including its endpoint laws. */
export function matchingLaw(degree, strength) {
  boundedInteger(degree, MAX_DEGREE, 'Degree');
  const h = probability(strength, 'Strength');
  return Array.from({ length: degree + 1 }, (_, j) => {
    let alternatingSum = ZERO;
    for (let i = 0; i <= degree - j; i += 1) {
      alternatingSum = add(alternatingSum, div(pow(neg(h), i), factorial(i)));
    }
    return mul(div(pow(h, j), factorial(j)), alternatingSum);
  });
}

/** Return [kappa_0=0, ..., kappa_order] after independent fixed Poisson addition. */
export function factorialCumulants(values, order, background = ZERO) {
  boundedInteger(order, MAX_ORDER, 'Order');
  if (!Array.isArray(values) || values.length < 1 || values.length > MAX_DEGREE + 1) {
    throw new RangeError(`A law must contain 1 to ${MAX_DEGREE + 1} masses.`);
  }
  for (let index = 0; index < values.length; index += 1) {
    if (!Object.hasOwn(values, index)) throw new TypeError('Every mass must be supplied explicitly.');
  }
  const law = values.map(value => probability(value, 'Mass'));
  if (compare(law.reduce(add, ZERO), ONE) !== 0) {
    throw new RangeError('The masses must sum exactly to one.');
  }
  const b = rational(background);
  if (compare(b, ZERO) < 0) throw new RangeError('The background rate must be nonnegative.');
  const sourceMoments = Array.from({ length: order + 1 }, (_, r) => {
    return law.reduce((total, mass, x) => {
      if (x < r) return total;
      return add(total, mul(mass, factorial(x) / factorial(x - r)));
    }, ZERO);
  });
  const moments = sourceMoments.map((_, r) => {
    let total = ZERO;
    for (let k = 0; k <= r; k += 1) {
      total = add(total, mul(mul(choose(r, k), sourceMoments[k]), pow(b, r - k)));
    }
    return total;
  });
  const cumulants = [ZERO];
  for (let n = 1; n <= order; n += 1) {
    let correction = ZERO;
    for (let j = 1; j < n; j += 1) {
      correction = add(correction, mul(mul(choose(n - 1, j - 1), cumulants[j]), moments[n - j]));
    }
    cumulants.push(sub(moments[n], correction));
  }
  return cumulants;
}

function integerSqrt(value) {
  if (value < 0n) throw new RangeError('A real square root requires a nonnegative argument.');
  if (value < 2n) return value;
  let x = 1n << BigInt(Math.ceil(value.toString(2).length / 2));
  while (true) {
    const next = (x + value / x) / 2n;
    if (next >= x) return x;
    x = next;
  }
}

function sqrtDescriptor(value) {
  const rootNumerator = integerSqrt(value.n);
  const rootDenominator = integerSqrt(value.d);
  if (rootNumerator ** 2n === value.n && rootDenominator ** 2n === value.d) {
    const exact = make(rootNumerator, rootDenominator);
    return { exact, expression: fmt(exact), enclosure: [exact, exact] };
  }
  const scale = 10n ** 24n;
  const floor = integerSqrt(value.n * scale * scale / value.d);
  return {
    exact: null,
    expression: `sqrt(${fmt(value)})`,
    enclosure: [make(floor, scale), make(floor + 1n, scale)],
  };
}

/** Exact population inverse for D=1 with p in [0,1] and fixed b >= 0.
 * Compatibility with these two statistics does not validate the model.
 */
export function recoverBernoulli(meanValue, secondCumulantValue) {
  const mean = rational(meanValue);
  const second = rational(secondCumulantValue);
  if (compare(second, ZERO) > 0) {
    return { feasible: false, reason: 'A Bernoulli source requires the second factorial cumulant to be at most zero.' };
  }
  const square = neg(second);
  if (compare(square, ONE) > 0) {
    return { feasible: false, reason: 'These cumulants would require a source probability greater than one.' };
  }
  if (compare(mean, ZERO) < 0 || compare(mul(mean, mean), square) < 0) {
    return { feasible: false, reason: 'These cumulants would require a negative Poisson background rate.' };
  }
  const p = sqrtDescriptor(square);
  let b;
  if (p.exact !== null) {
    const exact = sub(mean, p.exact);
    b = { exact, expression: fmt(exact), enclosure: [exact, exact] };
  } else {
    const lower = sub(mean, p.enclosure[1]);
    b = {
      exact: null,
      expression: `${fmt(mean)} - ${p.expression}`,
      enclosure: [compare(lower, ZERO) < 0 ? ZERO : lower, sub(mean, p.enclosure[0])],
    };
  }
  return { feasible: true, p, b };
}
