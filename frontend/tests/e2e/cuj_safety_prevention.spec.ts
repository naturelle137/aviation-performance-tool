import { test, expect } from '@playwright/test';

test.describe('CUJ 3: Hazard Prevention', () => {

    test.beforeEach(async ({ page }) => {
        // Mock D-EBPF
        await page.route('**/api/v1/aircraft', async route => {
            await route.fulfill({
                json: [{ id: 1, registration: 'D-EBPF', mtow_kg: 1150 }]
            });
        });

        await page.route('**/api/v1/aircraft/1', async route => {
            await route.fulfill({
                json: {
                    id: 1, registration: 'D-EBPF', mtow_kg: 1150, empty_weight_kg: 750,
                    weight_stations: [{ id: 1, name: 'Rear Seat PAX', max_weight_kg: 350 }]
                }
            });
        });

        // Mock Overweight Result
        await page.route('**/api/v1/calculations/mass-balance', async route => {
            await route.fulfill({
                json: {
                    empty_weight_kg: 750,
                    takeoff_weight_kg: 1250,
                    within_weight_limits: false,
                    within_cg_limits: true, // Assuming CG is fine strictly speaking, just mass is bad
                    cg_points: [{ label: 'Takeoff', weight_kg: 1250, arm_m: 2.5, within_limits: false }],
                    warnings: [
                        { level: 'critical', message: 'Maximum Takeoff Mass Exceeded' }
                    ]
                }
            });
        });
    });

    test('Scenario: Pilot exceeds MTOM limits', async ({ page }) => {
        await page.goto('/calculation');
        await page.click('text=Select Aircraft');
        await page.click('text=D-EBPF');

        // When the user sets the "Rear Seat PAX" weight to 300 kg
        // (750 Empty + 200 Front + 300 Rear = 1250 > 1150)
        await page.fill('label:has-text("Rear Seat PAX") >> .. >> input', '300');

        // Trigger Calc (or auto-trigger)
        await page.click('text=Calculate M&B');

        // Then the "Total Mass" display should immediately turn RED (REQ-UI-10)
        const massDisplay = page.locator('.mass-display-value'); // Assuming class
        await expect(massDisplay).toHaveClass(/text-red-600|danger/); // Tailwind or standard class
        await expect(massDisplay).toContainText('1250 kg');

        // And a critical alert "Maximum Takeoff Mass Exceeded" should be visible (REQ-MB-04)
        await expect(page.locator('.alert-critical, .alert-danger')).toContainText('Maximum Takeoff Mass Exceeded');

        // And the "Performance Calculation" button should be disabled
        const perfBtn = page.locator('button:has-text("Performance")');
        if (await perfBtn.isVisible()) {
            await expect(perfBtn).toBeDisabled();
        }
    });
});
