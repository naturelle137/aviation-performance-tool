import { test, expect } from '@playwright/test';

test('complete calculation flow', async ({ page }) => {
    // Mock API responses
    await page.route('**/api/v1/aircraft', async route => {
        await route.fulfill({
            json: [{
                id: 1,
                registration: 'D-TEST',
                aircraft_type: 'DA40',
                manufacturer: 'Diamond',
                mtow_kg: 1150
            }]
        });
    });

    await page.route('**/api/v1/aircraft/1', async route => {
        await route.fulfill({
            json: {
                id: 1,
                registration: 'D-TEST',
                aircraft_type: 'DA40',
                manufacturer: 'Diamond',
                empty_weight_kg: 800,
                empty_arm_m: 2.4,
                mtow_kg: 1150,
                fuel_capacity_l: 150,
                weight_stations: [
                    { id: 1, name: 'Pilot', arm_m: 2.3, default_weight_kg: 80, sort_order: 1 }
                ],
                cg_envelopes: [{
                    category: 'normal',
                    polygon_points: [{ weight_kg: 800, arm_m: 2.3 }, { weight_kg: 1150, arm_m: 2.3 }, { weight_kg: 1150, arm_m: 2.6 }]
                }]
            }
        });
    });

    await page.route('**/api/v1/calculations/mass-balance', async route => {
        await route.fulfill({
            json: {
                empty_weight_kg: 800,
                takeoff_weight_kg: 950,
                landing_weight_kg: 920,
                within_weight_limits: true,
                within_cg_limits: true,
                cg_points: [
                    { label: 'Takeoff', weight_kg: 950, arm_m: 2.35, within_limits: true }
                ],
                warnings: []
            }
        });
    });

    // 1. Navigate to Calculation Page
    await page.goto('/calculation');

    // 2. Select Aircraft
    await page.click('text=Select Aircraft');
    await page.click('text=D-TEST');

    // 3. Verify Weight Inputs appeared
    await expect(page.locator('label:has-text("Pilot")')).toBeVisible();

    // 4. Trigger Calculation
    await page.click('text=Calculate M&B');

    // 5. Verify Results
    await expect(page.locator('text=Mass & Balance Results')).toBeVisible();
    await expect(page.locator('text=Takeoff Weight')).toBeVisible();
    await expect(page.locator('text=950 kg')).toBeVisible();

    // 6. Verify Chart is rendered (canvas or wrapper present)
    await expect(page.locator('.chart-wrapper canvas')).toBeVisible();
});
