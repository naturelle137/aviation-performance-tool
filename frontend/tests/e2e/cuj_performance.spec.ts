import { test, expect } from '@playwright/test';

test.describe('CUJ 2: Performance under Extreme Conditions', () => {

    test.beforeEach(async ({ page }) => {
        // Mock Airport LFLJ
        await page.route('**/api/v1/airports/LFLJ', async route => {
            await route.fulfill({
                json: {
                    icao: 'LFLJ',
                    name: 'Courchevel',
                    elevation_ft: 6588,
                    runways: [{ ident: '22', surface: 'asphalt', tora_m: 525 }]
                }
            });
        });

        // Mock Performance Calculation (Response with Warnings)
        await page.route('**/api/v1/calculations/performance', async route => {
            // Check if extrapolation accepted in request? 
            // For now, return the warning response first.
            const request = route.request();
            const postData = request.postDataJSON();

            if (postData.confirm_extrapolation === true) {
                // Return success with penalty
                await route.fulfill({
                    json: {
                        todr_m: 850,
                        warnings: [],
                        notes: ["Extrapolation penalty applied (20%)"]
                    }
                });
            } else {
                // Return Warning/Error requiring confirmation
                await route.fulfill({
                    status: 400, // Or 200 with specific warning flag needing UI interaction
                    json: {
                        detail: "Extrapolation required",
                        requires_confirmation: true,
                        warnings: [
                            { code: "HighDensityAltitude", message: "High Density Altitude: 9000ft" },
                            { code: "Extrapolation", message: "Outside POH Standard Range" }
                        ]
                    }
                });
            }
        });
    });

    test('Scenario: Pilot plans takeoff at high altitude and temperature', async ({ page }) => {
        await page.goto('/performance'); // Assuming route

        // Given the user has selected airport "LFLJ" (Courchevel)
        await page.fill('input[placeholder="Airport ICAO"]', 'LFLJ');
        // Wait for lookup
        await expect(page.locator('text=Courchevel')).toBeVisible();

        // And the user enters the following environmental conditions: 30C, 1013hPa
        await page.fill('label:has-text("Temperature") >> .. >> input', '30');
        await page.fill('label:has-text("QNH") >> .. >> input', '1013');

        // Trigger Calculation
        await page.click('text=Calculate Performance');

        // Then the system should display a "High Density Altitude" warning (REQ-PF-05)
        await expect(page.locator('text=High Density Altitude')).toBeVisible();

        // And the user should see a mandatory confirmation dialog
        const dialog = page.locator('.confirmation-dialog');
        await expect(dialog).toBeVisible();
        await expect(dialog).toContainText('Pilot-in-Command acknowledges extrapolated data');

        // When the user confirms the dialog
        await dialog.locator('button:has-text("Confirm")').click();

        // Then the "Takeoff Distance Required" should be calculated
        await expect(page.locator('text=Takeoff Distance')).toBeVisible();
        await expect(page.locator('text=850 m')).toBeVisible();
        await expect(page.locator('text=Extrapolation penalty applied')).toBeVisible();
    });
});
