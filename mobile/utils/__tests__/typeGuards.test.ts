import { describe, it, expect } from '@jest/globals';
import { toBoolean, toNumber } from '../typeGuards';

describe('typeGuards', () => {
    describe('toBoolean', () => {
        it('should return boolean as-is', () => {
            expect(toBoolean(true)).toBe(true);
            expect(toBoolean(false)).toBe(false);
        });

        it('should convert string "true" to true', () => {
            expect(toBoolean('true')).toBe(true);
            expect(toBoolean('TRUE')).toBe(true);
            expect(toBoolean('True')).toBe(true);
            expect(toBoolean('  true  ')).toBe(true);
        });

        it('should convert string "1" to true', () => {
            expect(toBoolean('1')).toBe(true);
        });

        it('should convert string "false" to false', () => {
            expect(toBoolean('false')).toBe(false);
            expect(toBoolean('FALSE')).toBe(false);
            expect(toBoolean('False')).toBe(false);
            expect(toBoolean('  false  ')).toBe(false);
        });

        it('should convert string "0" to false', () => {
            expect(toBoolean('0')).toBe(false);
        });

        it('should convert empty string to false', () => {
            expect(toBoolean('')).toBe(false);
        });

        it('should convert non-zero numbers to true', () => {
            expect(toBoolean(1)).toBe(true);
            expect(toBoolean(-1)).toBe(true);
            expect(toBoolean(42)).toBe(true);
        });

        it('should convert zero to false', () => {
            expect(toBoolean(0)).toBe(false);
        });

        it('should convert NaN to false', () => {
            expect(toBoolean(NaN)).toBe(false);
        });

        it('should convert null to false', () => {
            expect(toBoolean(null)).toBe(false);
        });

        it('should convert undefined to false', () => {
            expect(toBoolean(undefined)).toBe(false);
        });

        it('should convert objects to true', () => {
            expect(toBoolean({})).toBe(true);
            expect(toBoolean([])).toBe(true);
        });
    });

    describe('toNumber', () => {
        it('should return number as-is', () => {
            expect(toNumber(42)).toBe(42);
            expect(toNumber(0)).toBe(0);
            expect(toNumber(-10)).toBe(-10);
        });

        it('should convert valid numeric strings to numbers', () => {
            expect(toNumber('42')).toBe(42);
            expect(toNumber('0')).toBe(0);
            expect(toNumber('-10')).toBe(-10);
            expect(toNumber('123')).toBe(123);
        });

        it('should return 0 for invalid numeric strings', () => {
            expect(toNumber('abc')).toBe(0);
            expect(toNumber('not a number')).toBe(0);
            // Note: parseInt('12.34.56') returns 12 (parses up to first non-digit)
            // This is expected behavior - the function uses parseInt
            expect(toNumber('12.34.56')).toBe(12);
        });

        it('should return 0 for NaN numbers', () => {
            expect(toNumber(NaN)).toBe(0);
        });

        it('should return 0 for null', () => {
            expect(toNumber(null)).toBe(0);
        });

        it('should return 0 for undefined', () => {
            expect(toNumber(undefined)).toBe(0);
        });

        it('should return 0 for objects', () => {
            expect(toNumber({})).toBe(0);
            expect(toNumber([])).toBe(0);
        });

        it('should parse only integer part of decimal strings', () => {
            expect(toNumber('12.34')).toBe(12);
            expect(toNumber('99.99')).toBe(99);
        });
    });
});
