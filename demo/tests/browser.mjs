import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.resolve(process.env.DEMO_QA_OUTPUT || path.join(root, 'build/demo-qa'));
const localBrowsers = path.join(root, 'build/demo-qa/browsers');
if (!process.env.PLAYWRIGHT_BROWSERS_PATH && existsSync(localBrowsers)) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = localBrowsers;
}
const { chromium, firefox, webkit } = await import('playwright');
const engines = { chromium, firefox, webkit };
const selected = (process.env.DEMO_BROWSERS || 'chromium,firefox,webkit').split(',');
const widths = (process.env.DEMO_WIDTHS || '1440,1280,768,390,320').split(',').map(Number);
const url = process.env.DEMO_URL || 'http://127.0.0.1:8765/demo/';
const axeSource = await readFile(require.resolve('axe-core/axe.min.js'), 'utf8');
const boundFiles = ['index.html', 'styles.css', 'app.mjs', 'math.mjs', 'favicon.svg', 'package.json', 'package-lock.json', 'tests/browser.mjs'];
async function sourceHashes() {
  return Object.fromEntries(await Promise.all(boundFiles.map(async (name) => [
    name, createHash('sha256').update(await readFile(path.join(root, 'demo', name))).digest('hex'),
  ])));
}
const report = {
  url,
  startedUtc: new Date().toISOString(),
  node: process.version,
  playwright: require('playwright/package.json').version,
  axe: require('axe-core/package.json').version,
  sourceSha256: await sourceHashes(),
  results: [],
  failures: [],
  limits: 'Finite browser and automated accessibility checks; screenshots require separate visual inspection. Touch is emulated, not physical-device testing.',
};
await mkdir(output, { recursive: true });

async function stable(page) {
  await page.waitForSelector('body[data-ready="true"]');
  await page.evaluate(async () => {
    await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
}

async function screenshot(page, name, fullPage = false) {
  await stable(page);
  await page.screenshot({ path: path.join(output, `${name}.png`), fullPage, animations: 'disabled' });
}

async function noOverflow(page) {
  const geometry = await page.evaluate(() => ({
    viewport: innerWidth,
    document: document.documentElement.scrollWidth,
    body: document.body.scrollWidth,
    offenders: [...document.body.querySelectorAll('*')].filter((element) => {
      const bounds = element.getBoundingClientRect();
      return bounds.width > 0 && bounds.height > 0 && (bounds.right > innerWidth + 1 || bounds.left < -1);
    }).slice(0, 12).map((element) => `${element.tagName.toLowerCase()}#${element.id}.${element.className?.baseVal ?? element.className}`),
  }));
  assert(geometry.document <= geometry.viewport + 1 && geometry.body <= geometry.viewport + 1,
    `Horizontal overflow: ${JSON.stringify(geometry)}`);
  return geometry;
}

async function chartLabelsFit(page) {
  const labels = await page.locator('#signal-chart').evaluate((svg) => {
    const bounds = svg.viewBox.baseVal;
    return [...svg.querySelectorAll('text')].map((element) => {
      const box = element.getBBox();
      return { text: element.textContent, x: box.x, y: box.y, right: box.x + box.width,
        bottom: box.y + box.height, width: bounds.width, height: bounds.height };
    });
  });
  const clipped = labels.filter((label) => label.x < -0.5 || label.y < -0.5
    || label.right > label.width + 0.5 || label.bottom > label.height + 0.5);
  assert.deepEqual(clipped, [], 'Chart labels should fit within their SVG viewBox');
  return { labels: labels.length, minimumX: Math.min(...labels.map(({ x }) => x)) };
}

async function controlsNotClipped(page) {
  const clipped = await page.evaluate(() => {
    const failures = [];
    for (const element of document.querySelectorAll('button,input,select,summary')) {
      const box = element.getBoundingClientRect();
      if (box.width === 0 || box.height === 0) continue;
      for (let parent = element.parentElement; parent; parent = parent.parentElement) {
        const style = getComputedStyle(parent);
        const bounds = parent.getBoundingClientRect();
        const horizontal = ['hidden', 'clip'].includes(style.overflowX)
          && (box.left < bounds.left - 1 || box.right > bounds.right + 1);
        const vertical = ['hidden', 'clip'].includes(style.overflowY)
          && (box.top < bounds.top - 1 || box.bottom > bounds.bottom + 1);
        if (horizontal || vertical) {
          failures.push({ control: element.id || element.tagName, container: parent.id || parent.className,
            controlRight: box.right, containerRight: bounds.right, horizontal, vertical });
        }
      }
    }
    return failures;
  });
  assert.deepEqual(clipped, [], 'Interactive controls should not be clipped by their containers');
}

async function accessibility(page, name) {
  await page.addScriptTag({ content: axeSource });
  const result = await page.evaluate(async () => {
    const audit = await window.axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
    });
    return {
      violations: audit.violations.map(({ id, impact, description, helpUrl, nodes }) => ({
        id, impact, description, helpUrl,
        nodes: nodes.map(({ target, failureSummary }) => ({ target, failureSummary })),
      })),
      incomplete: audit.incomplete.map(({ id, nodes }) => ({ id, targets: nodes.map(({ target }) => target) })),
      passes: audit.passes.length,
    };
  });
  await writeFile(path.join(output, `${name}-axe.json`), JSON.stringify(result, null, 2));
  assert.equal(result.violations.length, 0, `Accessibility violations: ${JSON.stringify(result.violations)}`);
  return result;
}

async function value(page, selector) {
  return page.locator(selector).evaluate((element) => element.value ?? element.textContent.trim());
}

async function recover(page, mean, second) {
  await page.locator('#mean-input').fill(mean);
  await page.locator('#k2-input').fill(second);
  await page.locator('#recover-button').click();
  await stable(page);
  return page.locator('#recovery-result').innerText();
}

async function downloadRecord(page, name, touch) {
  const pending = page.waitForEvent('download');
  if (touch) await page.locator('#download-json').tap();
  else await page.locator('#download-json').click();
  const download = await pending;
  assert.match(download.suggestedFilename(), /\.json$/);
  const destination = path.join(output, `${name}-export.json`);
  await download.saveAs(destination);
  const text = await readFile(destination, 'utf8');
  const record = JSON.parse(text);
  assert.equal(record.schema_version, 1);
  assert.match(record.scope, /not measured data/);
  assert(text.length > 100, 'Export should include the calculation');
  return record;
}

async function interactions(page, name, touch, engine) {
  const click = async (selector) => touch ? page.locator(selector).tap() : page.locator(selector).click();
  await click('#reset-demo');
  assert.equal(await value(page, '#background'), '50');
  assert.equal(await value(page, '#degree'), '3');
  assert.equal(await value(page, '#strength'), '50');

  const initialOutput = await page.locator('#background-output').innerText();
  const initialHigher = await page.locator('#signal-k2, #signal-k3').allTextContents();
  await page.locator('#background').focus();
  // Enter through Tab navigation so every engine applies its keyboard-focus policy.
  await page.keyboard.press('Tab');
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('ArrowRight');
  await stable(page);
  assert.equal(await value(page, '#background'), '55', 'Range control should respond to keyboard');
  assert.notEqual(await page.locator('#background-output').innerText(), initialOutput);
  assert.deepEqual(await page.locator('#signal-k2, #signal-k3').allTextContents(), initialHigher,
    'The higher cumulants should remain unchanged when only background changes');
  const focus = await page.locator('#background').evaluate((element) => {
    const style = getComputedStyle(element);
    return { focused: document.activeElement === element, visible: style.outlineStyle !== 'none' || style.boxShadow !== 'none' };
  });
  assert(focus.focused && focus.visible, `Keyboard focus must be visible: ${JSON.stringify(focus)}`);
  await screenshot(page, `${name}-keyboard-focus`);
  if (touch) {
    const slider = await page.locator('#background').boundingBox();
    await page.touchscreen.tap(slider.x + slider.width * 0.75, slider.y + slider.height / 2);
    await stable(page);
    assert.notEqual(await value(page, '#background'), '55', 'Touch should change the range control');
  }

  await page.locator('#source-select').selectOption('three-count');
  await page.locator('#source-select').selectOption('matching');
  assert.match((await page.locator('#signal-k2').innerText()).trim(), /^0(?:\.0+)?$/,
    'The matching-law second cumulant is exactly zero');
  await page.locator('#source-select').selectOption('bernoulli');
  await click('#exact-toggle');
  assert.equal(await page.locator('#exact-toggle').getAttribute('aria-pressed'), 'true');
  await controlsNotClipped(page);
  await click('#exact-toggle');
  assert.equal(await page.locator('#exact-toggle').getAttribute('aria-pressed'), 'false');

  await page.locator('#signal-table summary').click();
  assert.equal(await page.locator('#signal-table').getAttribute('open'), '');
  await accessibility(page, `${name}-expanded-table`);
  await page.locator('#signal-table summary').click();

  await page.locator('#degree').selectOption('8');
  await page.locator('#strength').focus();
  await page.keyboard.press('End');
  assert.equal(await value(page, '#strength'), '90');
  await click('#reveal');
  assert.equal(await page.locator('#reveal').getAttribute('aria-expanded'), 'true');
  const tableGeometry = await page.locator('#sharpness-table').evaluate((table) => ({
    viewport: table.parentElement.clientWidth,
    content: table.parentElement.scrollWidth,
  }));
  assert(tableGeometry.content <= tableGeometry.viewport + 1,
    `Sharpness table must fit its container: ${JSON.stringify(tableGeometry)}`);
  await page.locator('#sharpness').scrollIntoViewIfNeeded();
  await noOverflow(page);
  await screenshot(page, `${name}-sharpness-revealed`);

  await click('#preset-default');
  assert.equal(await value(page, '#mean-input'), '4/5');
  assert.equal(await value(page, '#k2-input'), '-9/100');
  const defaultP = await value(page, '#recovered-p');
  const defaultB = await value(page, '#recovered-b');
  assert.match(defaultP, /3\/10|0\.3/);
  assert.match(defaultB, /1\/2|0\.5/);

  await page.locator('#mean-input').fill('2');
  assert.match(await page.locator('#recovery-result').innerText(), /Inputs changed/i);
  assert.equal(await value(page, '#recovered-p'), 'Unavailable');
  const pendingRecord = await downloadRecord(page, `${name}-pending`, touch);
  assert.equal(pendingRecord.recovery.status, 'inputs_changed_not_calculated');
  assert.equal(pendingRecord.recovery.p, undefined, 'Pending export must not retain old parameters');

  for (const malformed of ['', '1/0', '1e-3']) {
    assert.match(await recover(page, malformed, '-9/100'), /valid exact inputs/i);
    assert.equal(await page.locator('#mean-input').getAttribute('aria-invalid'), 'true');
  }

  const invalidMean = await recover(page, '1/10', '-9/100');
  assert.match(invalidMean, /negative|incompatible|nonnegative|no admissible|outside|cannot|invalid/i);
  if (await page.locator('#recovered-b').count()) {
    assert.notEqual(await value(page, '#recovered-b'), defaultB, 'Invalid input must clear stale background output');
  }
  if (await page.locator('#recovered-p').count()) {
    assert.notEqual(await value(page, '#recovered-p'), defaultP, 'Invalid input must clear stale source output');
  }
  await screenshot(page, `${name}-invalid-recovery`);
  await accessibility(page, `${name}-invalid-recovery`);

  const invalidSign = await recover(page, '4/5', '1/100');
  assert.match(invalidSign, /positive|incompatible|nonpositive|no admissible|outside|cannot|invalid/i);
  const irrational = await recover(page, '1', '-1/2');
  const irrationalP = await value(page, '#recovered-p');
  assert.match(`${irrational} ${irrationalP}`, /√|sqrt|radical/i);
  assert.match(`${irrational} ${irrationalP}`, /0\.707/);
  await page.locator('#recovery').scrollIntoViewIfNeeded();
  await screenshot(page, `${name}-irrational-recovery`);
  await noOverflow(page);

  await click('#preset-boundary');
  await click('#preset-invalid');
  await click('#reset-demo');
  assert.equal(await value(page, '#degree'), '3');
  assert.equal(await value(page, '#strength'), '50');
  assert.equal(await value(page, '#background'), '50');
  assert.equal(await value(page, '#mean-input'), '4/5');

  await page.locator('#background').focus();
  await page.keyboard.press('End');
  await stable(page);
  const sharedUrl = page.url();
  assert(new URL(sharedUrl).search.length > 0, 'Control changes should be encoded in the URL');
  await page.reload();
  await stable(page);
  assert.equal(await value(page, '#background'), '300', 'Shared URL should restore selected controls');

  const exported = await downloadRecord(page, name, touch);
  assert.equal(exported.signal.background, '3');
  assert.deepEqual(exported.signal.probabilities, ['7/10', '3/10']);
  assert.deepEqual(exported.signal.observed_factorial_cumulants_1_to_4.slice(0, 2), ['33/10', '-9/100']);
  assert.equal(exported.recovery.status, 'compatible');
  assert.equal(exported.recovery.p.exact_rational, '3/10');
  assert.equal(exported.recovery.b.exact_rational, '1/2');

  await click('#copy-link');
  if (engine === 'chromium') {
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), page.url(), 'Copy link should write the current share URL');
  }
  assert.match(await page.locator('#export-status').innerText(), /Link copied|Copy the address/i);
  await click('#reset-demo');

  const hostile = new URL(url);
  const payload = '<img src=x onerror=window.demoInjected=1>';
  for (const [key, text] of Object.entries({ source: '__proto__', background: '999', degree: '0', strength: '-1', mean: payload, k2: '-9/100' })) {
    hostile.searchParams.set(key, text);
  }
  await page.goto(hostile.toString(), { waitUntil: 'networkidle' });
  await stable(page);
  assert.equal(await value(page, '#source-select'), 'bernoulli');
  assert.equal(await value(page, '#background'), '50');
  assert.equal(await value(page, '#degree'), '3');
  assert.equal(await value(page, '#strength'), '50');
  assert.equal(await value(page, '#mean-input'), payload);
  assert.match(await page.locator('#recovery-result').innerText(), /valid exact inputs/i);
  assert.equal(await page.evaluate(() => window.demoInjected), undefined);
  assert.equal(await page.locator('img[onerror]').count(), 0);
  await click('#reset-demo');
  return { keyboard: true, touch, controls: true, invalidStates: true, pendingExport: true, irrational: true, sharedUrl: true, clipboardReadback: engine === 'chromium', download: true, malformedUrl: true, htmlInputInert: true, tableGeometry };
}

async function checkCase(browser, engine, width) {
  const name = `${engine}-${width}`;
  const context = await browser.newContext({
    viewport: { width, height: width < 500 ? 844 : 1000 },
    deviceScaleFactor: 1,
    hasTouch: width < 500,
    isMobile: engine !== 'firefox' && width < 500,
    reducedMotion: 'reduce',
    acceptDownloads: true,
    permissions: engine === 'chromium' ? ['clipboard-read', 'clipboard-write'] : [],
  });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  const unexpectedRequests = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('dialog', async (dialog) => { errors.push(`Unexpected dialog: ${dialog.message()}`); await dialog.dismiss(); });
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('requestfailed', (request) => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
  page.on('request', (request) => {
    if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(url).origin) {
      unexpectedRequests.push(request.url());
    }
  });
  try {
    const response = await page.goto(url, { waitUntil: 'networkidle' });
    assert.equal(response.status(), 200);
    await stable(page);
    assert.equal(await page.locator('h1').count(), 1);
    assert.equal(await page.locator('main').count(), 1);
    assert.match(await page.locator('body').innerText(), /synthetic|population|illustrative/i);
    const geometry = await noOverflow(page);
    const chartGeometry = await chartLabelsFit(page);
    await controlsNotClipped(page);
    const reducedMotion = await page.evaluate(() => ({
      enabled: matchMedia('(prefers-reduced-motion: reduce)').matches,
      activeAnimations: document.getAnimations().filter((animation) => animation.playState === 'running').length,
    }));
    assert(reducedMotion.enabled);
    assert.equal(reducedMotion.activeAnimations, 0, 'Reduced-motion preference should avoid ongoing animation');
    await screenshot(page, `${name}-full`, true);
    await screenshot(page, `${name}-top`);
    await page.locator('#signal .distribution-figure').screenshot({
      path: path.join(output, `${name}-signal-chart.png`), animations: 'disabled',
    });
    for (const section of ['signal', 'sharpness', 'recovery']) {
      await page.locator(`#${section}`).evaluate((element) => element.scrollIntoView({ block: 'start', behavior: 'instant' }));
      await screenshot(page, `${name}-${section}`);
    }
    const axe = await accessibility(page, name);
    let interaction = null;
    if (width === 1440 || width <= 390) {
      interaction = await interactions(page, name, width <= 390, engine);
    }
    assert.deepEqual(errors, [], 'Browser console and network requests should have no errors');
    assert.deepEqual(unexpectedRequests, [], 'The static demo should not contact external services');
    report.results.push({ engine, browser: browser.version(), width, geometry, chartGeometry, reducedMotion, accessibilityPasses: axe.passes, interaction, status: 'PASS' });
    console.log(`PASS ${name}`);
  } catch (error) {
    await page.screenshot({ path: path.join(output, `${name}-failure.png`), fullPage: true, animations: 'disabled' }).catch(() => {});
    const failure = { engine, width, error: error.stack, browserErrors: errors, unexpectedRequests };
    report.failures.push(failure);
    console.error(`FAIL ${name}: ${error.message}`);
  } finally {
    await context.close();
    await writeFile(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
  }
}

async function checkWithoutJavaScript(browser, engine) {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'networkidle' });
    assert.match(await page.locator('noscript').innerText(), /requires JavaScript/i);
    assert.match(await page.locator('noscript a').getAttribute('href'), /theorem\.md/);
    await noOverflow(page);
    await page.screenshot({ path: path.join(output, `${engine}-390-no-javascript.png`), animations: 'disabled' });
    report.results.push({ engine, javascript: false, width: 390, status: 'PASS' });
    console.log(`PASS ${engine} without JavaScript`);
  } catch (error) {
    report.failures.push({ engine, javascript: false, error: error.stack });
    console.error(`FAIL ${engine} without JavaScript: ${error.message}`);
  } finally {
    await context.close();
  }
}

for (const engine of selected) {
  assert(engines[engine], `Unknown browser engine: ${engine}`);
  let browser;
  try {
    browser = await engines[engine].launch({ headless: true });
    for (const width of widths) await checkCase(browser, engine, width);
    await checkWithoutJavaScript(browser, engine);
  } catch (error) {
    report.failures.push({ engine, error: error.stack });
    console.error(`FAIL ${engine}: ${error.message}`);
  } finally {
    if (browser) await browser.close();
  }
}
report.finishedUtc = new Date().toISOString();
try {
  assert.deepEqual(await sourceHashes(), report.sourceSha256, 'Demo sources changed during browser verification');
} catch (error) {
  report.failures.push({ error: error.message });
}
report.status = report.failures.length ? 'FAIL' : 'PASS';
await writeFile(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
console.log(`${report.status}: ${report.results.length} browser/viewport cases; ${report.failures.length} failures. Artifacts: ${output}`);
if (report.failures.length) process.exitCode = 1;
