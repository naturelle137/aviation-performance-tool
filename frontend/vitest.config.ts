import { fileURLToPath } from 'node:url'
import { configDefaults, defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
    viteConfig,
    defineConfig({
        test: {
            environment: 'jsdom',
            exclude: [...configDefaults.exclude, 'tests/e2e/**'],
            root: fileURLToPath(new URL('./', import.meta.url)),
            globals: true,
            coverage: {
                provider: 'v8',
                reporter: ['text', 'json', 'html'],
                exclude: [
                    'node_modules/',
                    'tests/',
                    '**/*.d.ts',
                    '**/*.config.*',
                    '**/types/**',
                ],
                thresholds: {
                    lines: 75,
                    functions: 75,
                    branches: 70,
                    statements: 75,
                }
            }
        }
    })
)
