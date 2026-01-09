import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { getItem, setItem, removeItem } from '../storage';

// Mock dependencies
jest.mock('react-native', () => ({
    Platform: {
        OS: 'ios',
    },
}));

jest.mock('expo-secure-store', () => ({
    getItemAsync: jest.fn<() => Promise<string | null>>(),
    setItemAsync: jest.fn<() => Promise<void>>(),
    deleteItemAsync: jest.fn<() => Promise<void>>(),
}));

// Mock localStorage for web platform
const mockLocalStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
};

// Make localStorage available globally for web tests
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(global as any).localStorage = mockLocalStorage;

describe('storage', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Reset to native platform by default
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (Platform as any).OS = 'ios';
    });

    describe('getItem', () => {
        describe('native platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'ios';
            });

            it('should return value from SecureStore', async () => {
                (
                    SecureStore.getItemAsync as jest.MockedFunction<
                        typeof SecureStore.getItemAsync
                    >
                ).mockResolvedValue('stored-value');
                const result = await getItem('test-key');
                expect(result).toBe('stored-value');
                expect(SecureStore.getItemAsync).toHaveBeenCalledWith(
                    'test-key'
                );
            });

            it('should return null when SecureStore returns null', async () => {
                (
                    SecureStore.getItemAsync as jest.MockedFunction<
                        typeof SecureStore.getItemAsync
                    >
                ).mockResolvedValue(null);
                const result = await getItem('test-key');
                expect(result).toBeNull();
            });

            it('should return null and log error when SecureStore throws', async () => {
                const consoleErrorSpy = jest
                    .spyOn(console, 'error')
                    .mockImplementation(() => {});
                (
                    SecureStore.getItemAsync as jest.MockedFunction<
                        typeof SecureStore.getItemAsync
                    >
                ).mockRejectedValue(new Error('Storage error'));
                const result = await getItem('test-key');
                expect(result).toBeNull();
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    'Error getting item from storage:',
                    expect.any(Error)
                );
                consoleErrorSpy.mockRestore();
            });
        });

        describe('web platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'web';
            });

            it('should return value from localStorage', async () => {
                mockLocalStorage.getItem.mockReturnValue('stored-value');
                const result = await getItem('test-key');
                expect(result).toBe('stored-value');
                expect(mockLocalStorage.getItem).toHaveBeenCalledWith(
                    'test-key'
                );
            });

            it('should return null when localStorage returns null', async () => {
                mockLocalStorage.getItem.mockReturnValue(null);
                const result = await getItem('test-key');
                expect(result).toBeNull();
            });

            it('should return null and log error when localStorage throws', async () => {
                const consoleErrorSpy = jest
                    .spyOn(console, 'error')
                    .mockImplementation(() => {});
                mockLocalStorage.getItem.mockImplementation(() => {
                    throw new Error('localStorage error');
                });
                const result = await getItem('test-key');
                expect(result).toBeNull();
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    'Error getting item from storage:',
                    expect.any(Error)
                );
                consoleErrorSpy.mockRestore();
            });
        });
    });

    describe('setItem', () => {
        describe('native platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'ios';
            });

            it('should set value in SecureStore', async () => {
                (
                    SecureStore.setItemAsync as jest.MockedFunction<
                        typeof SecureStore.setItemAsync
                    >
                ).mockResolvedValue(undefined);
                await setItem('test-key', 'test-value');
                expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
                    'test-key',
                    'test-value'
                );
            });

            it('should throw error when SecureStore throws', async () => {
                const error = new Error('Storage error');
                (
                    SecureStore.setItemAsync as jest.MockedFunction<
                        typeof SecureStore.setItemAsync
                    >
                ).mockRejectedValue(error);
                const consoleErrorSpy = jest
                    .spyOn(console, 'error')
                    .mockImplementation(() => {});
                await expect(setItem('test-key', 'test-value')).rejects.toThrow(
                    'Storage error'
                );
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    'Error setting item in storage:',
                    error
                );
                consoleErrorSpy.mockRestore();
            });
        });

        describe('web platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'web';
            });

            it('should set value in localStorage', async () => {
                mockLocalStorage.setItem.mockImplementation(() => {});
                await setItem('test-key', 'test-value');
                expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                    'test-key',
                    'test-value'
                );
            });

            it('should throw error when localStorage throws', async () => {
                const error = new Error('localStorage error');
                mockLocalStorage.setItem.mockImplementation(() => {
                    throw error;
                });
                const consoleErrorSpy = jest
                    .spyOn(console, 'error')
                    .mockImplementation(() => {});
                await expect(setItem('test-key', 'test-value')).rejects.toThrow(
                    'localStorage error'
                );
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    'Error setting item in storage:',
                    error
                );
                consoleErrorSpy.mockRestore();
            });
        });
    });

    describe('removeItem', () => {
        describe('native platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'ios';
            });

            it('should remove item from SecureStore', async () => {
                (
                    SecureStore.deleteItemAsync as jest.MockedFunction<
                        typeof SecureStore.deleteItemAsync
                    >
                ).mockResolvedValue(undefined);
                await removeItem('test-key');
                expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith(
                    'test-key'
                );
            });

            it('should log warning but not throw when SecureStore throws', async () => {
                const consoleWarnSpy = jest
                    .spyOn(console, 'warn')
                    .mockImplementation(() => {});
                (
                    SecureStore.deleteItemAsync as jest.MockedFunction<
                        typeof SecureStore.deleteItemAsync
                    >
                ).mockRejectedValue(new Error('Storage error'));
                await removeItem('test-key');
                expect(consoleWarnSpy).toHaveBeenCalledWith(
                    'Error removing item from storage:',
                    expect.any(Error)
                );
                consoleWarnSpy.mockRestore();
            });
        });

        describe('web platform', () => {
            beforeEach(() => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (Platform as any).OS = 'web';
            });

            it('should remove item from localStorage', async () => {
                mockLocalStorage.removeItem.mockImplementation(() => {});
                await removeItem('test-key');
                expect(mockLocalStorage.removeItem).toHaveBeenCalledWith(
                    'test-key'
                );
            });

            it('should log warning but not throw when localStorage throws', async () => {
                const consoleWarnSpy = jest
                    .spyOn(console, 'warn')
                    .mockImplementation(() => {});
                mockLocalStorage.removeItem.mockImplementation(() => {
                    throw new Error('localStorage error');
                });
                await removeItem('test-key');
                expect(consoleWarnSpy).toHaveBeenCalledWith(
                    'Error removing item from storage:',
                    expect.any(Error)
                );
                consoleWarnSpy.mockRestore();
            });
        });
    });
});
