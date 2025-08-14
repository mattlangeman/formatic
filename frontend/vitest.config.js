import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/tests/setup.js'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'src/tests/',
          '*.config.js',
          'src/main.js',
          'src/plugins/',
        ],
        thresholds: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      },
      include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
      exclude: ['node_modules', 'dist', '.idea', '.git', '.cache', 'e2e']
    },
  })
)