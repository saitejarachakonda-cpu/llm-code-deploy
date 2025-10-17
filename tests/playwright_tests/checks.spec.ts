import { test, expect } from '@playwright/test';

const PAGES_URL = process.env.PAGES_URL || 'http://localhost:5500';

test('page shows solved text within 15s', async ({ page }) => {
  await page.goto(PAGES_URL + '?url=https://example.com/sample.png', { waitUntil: 'load' });
  await expect(page.locator('#solution')).toHaveText(/SOLVED:/, { timeout: 15000 });
});
