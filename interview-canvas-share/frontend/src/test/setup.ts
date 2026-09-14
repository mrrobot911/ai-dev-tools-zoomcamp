import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach } from 'vitest';
import { mockDB } from '../services/mock-db';
import { mockSync } from '../services/mock-sync';
import { resetServices } from '../services';

beforeEach(() => {
  mockDB.clear();
  mockSync.clearAll();
  resetServices();
});

afterEach(() => {
  mockDB.clear();
  mockSync.clearAll();
  resetServices();
});
