import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const capturasDir = path.join(__dirname, 'Resultados', 'capturas', 'inicio-sesion');

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  expect: { timeout: 15_000 },
  outputDir: path.join(__dirname, 'test-results'),
  use: {
    baseURL: 'http://localhost:5002',
    trace: 'on-first-retry',
    screenshot: 'off',
    video: 'off',
  },
  projects: [
    {
      name: 'chrome',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        headless: false,
        launchOptions: {
          slowMo: 400,
        },
      },
    },
  ],
  globalSetup: undefined,
});

export { capturasDir };
