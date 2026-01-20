/**
 * @type {import('@stryker-mutator/api/core').PartialStrykerOptions}
 */
export default {
    packageManager: 'npm',
    reporters: ['html', 'clear-text', 'progress'],
    testRunner: 'vitest',
    coverageAnalysis: 'perTest',

    vitest: {
        configFile: 'vitest.config.ts',
    },

    mutate: [
        'src/**/*.ts',
        'src/**/*.vue',
        '!src/**/*.d.ts',
        '!src/main.ts',
        '!src/router/**',
        '!src/types/**',
    ],

    thresholds: {
        high: 80,
        low: 60,
        break: 50,
    },

    timeoutMS: 60000,
    concurrency: 4,

    ignorePatterns: [
        'node_modules',
        'dist',
        'coverage',
    ],
}
