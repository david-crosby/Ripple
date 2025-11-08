import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

/**
 * Extend Vitest's expect with jest-dom matchers
 * This allows us to use matchers like toBeInTheDocument(), toHaveClass(), etc.
 */
expect.extend(matchers);

/**
 * Clean up after each test
 * Unmounts React components and clears the DOM
 */
afterEach(() => {
  cleanup();
});
