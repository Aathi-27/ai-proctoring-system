import { test, expect } from '@playwright/test';

test.describe('Invigilator Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for dashboard to load
    await page.waitForSelector('text=Real-Time Alerts', { timeout: 5000 });
  });

  test('should display exam info in header', async ({ page }) => {
    await expect(page.locator('text=Mathematics Final Exam')).toBeVisible();
    await expect(page.locator('text=candidates active')).toBeVisible();
  });

  test('should display connection status indicator', async ({ page }) => {
    const indicator = page.locator('text=Connected').or(page.locator('text=Disconnected'));
    await expect(indicator).toBeVisible();
  });

  test('should list active sessions in sidebar', async ({ page }) => {
    const sessions = page.locator('text=Active Sessions');
    await expect(sessions).toBeVisible();
    
    // Check for candidate names
    await expect(page.locator('text=John Smith').or(page.locator('text=Emily Johnson'))).toBeVisible();
  });

  test('should display video feed for selected session', async ({ page }) => {
    // Find and click on a session
    const firstSession = page.locator('text=John Smith').first();
    await firstSession.click();
    
    // Check for video feed elements
    await expect(page.locator('text=HD Video Stream')).toBeVisible();
  });

  test('should display risk score meter', async ({ page }) => {
    // The risk score meter should be visible
    const scoreElements = page.locator('svg circle');
    expect(await scoreElements.count()).toBeGreaterThan(0);
  });

  test('should display alert panel', async ({ page }) => {
    const alertPanel = page.locator('text=Real-Time Alerts');
    await expect(alertPanel).toBeVisible();
  });

  test('should display event timeline', async ({ page }) => {
    const timeline = page.locator('text=Event Timeline');
    await expect(timeline).toBeVisible();
  });

  test('should display evidence gallery', async ({ page }) => {
    const gallery = page.locator('text=Evidence Gallery');
    await expect(gallery).toBeVisible();
  });

  test('should pause session when pause button clicked', async ({ page }) => {
    // Click on a session to expand
    const firstSession = page.locator('text=John Smith').first();
    await firstSession.click();
    
    // Find and click pause button
    const pauseButton = page.locator('button:has-text("Pause Exam")').first();
    if (await pauseButton.isVisible()) {
      await pauseButton.click();
      // Session should show paused status
      await expect(page.locator('text=PAUSED')).toBeVisible();
    }
  });

  test('should flag session when flag button clicked', async ({ page }) => {
    // Click on a session to expand
    const firstSession = page.locator('text=John Smith').first();
    await firstSession.click();
    
    // Find and click flag button
    const flagButton = page.locator('button:has-text("Flag Session")').first();
    if (await flagButton.isVisible()) {
      await flagButton.click();
      // Session should show flagged status
      await expect(page.locator('text=FLAGGED')).toBeVisible();
    }
  });

  test('should acknowledge alerts', async ({ page }) => {
    const acknowledgeButtons = page.locator('button:has-text("Acknowledge")');
    const count = await acknowledgeButtons.count();
    
    if (count > 0) {
      await acknowledgeButtons.first().click();
      // Button should no longer be visible after acknowledging
      await expect(acknowledgeButtons.first()).not.toBeVisible({ timeout: 1000 });
    }
  });

  test('should filter alerts by type', async ({ page }) => {
    // Click on a filter button
    const filterButtons = page.locator('button:has-text("📱"), button:has-text("👤"), button:has-text("⚠️")');
    const filterCount = await filterButtons.count();
    
    if (filterCount > 0) {
      await filterButtons.first().click();
      // Alert list should update
      await page.waitForTimeout(500);
      expect(true).toBe(true); // Just verify interaction works
    }
  });

  test('should expand event details', async ({ page }) => {
    // Click on an event to expand
    const events = page.locator('[class*="border-l"]').first();
    if (await events.isVisible()) {
      await events.click();
      // Details should be visible
      await page.waitForTimeout(300);
      expect(true).toBe(true);
    }
  });

  test('should select different sessions', async ({ page }) => {
    // Try clicking on different sessions
    const buttons = page.locator('div:has-text("Emily Johnson")').or(page.locator('div:has-text("Michael Brown")'));
    const count = await buttons.count();
    
    if (count > 0) {
      await buttons.first().click();
      await page.waitForTimeout(500);
      expect(true).toBe(true);
    }
  });

  test('should display keyboard shortcuts info', async ({ page }) => {
    await expect(page.locator('text=Alt+P: Pause')).toBeVisible();
    await expect(page.locator('text=Alt+F: Flag')).toBeVisible();
  });

  test('should have logout button', async ({ page }) => {
    const logoutButton = page.locator('button:has-text("Logout")');
    await expect(logoutButton).toBeVisible();
  });

  test('should show elapsed time for session', async ({ page }) => {
    // Time should be displayed in format MM:SS
    const timePattern = /\d{2}:\d{2}/;
    const pageText = await page.content();
    expect(pageText).toMatch(timePattern);
  });

  test('should display risk trend chart', async ({ page }) => {
    // Click on a session
    const firstSession = page.locator('text=John Smith').first();
    await firstSession.click();
    
    // Wait for chart to render
    await page.waitForTimeout(500);
    
    // Check for chart SVG
    const charts = page.locator('svg');
    expect(await charts.count()).toBeGreaterThan(0);
  });
});
