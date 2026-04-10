/**
 * Render slides.html to PDF using Puppeteer.
 * Each slide is 1280x720px, rendered as a separate page.
 */

const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  const htmlPath = path.resolve(__dirname, '..', 'output', 'slides.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0', timeout: 30000 });
  await page.evaluateHandle('document.fonts.ready');

  const outputPath = path.resolve(__dirname, '..', 'output', 'revolut_gp_analysis.pdf');
  await page.pdf({
    path: outputPath,
    width: '1280px',
    height: '720px',
    printBackground: true,
    preferCSSPageSize: false,
    margin: { top: 0, right: 0, bottom: 0, left: 0 }
  });

  console.log(`PDF: ${outputPath}`);
  await browser.close();
})();
