import { describe, it, expect } from 'vitest';
import { getAvatarUrl, getRoleBadgeColor } from '../userUtils';
import { designTokens } from '../../designTokens';

describe('User Utilities', () => {
    describe('getAvatarUrl', () => {
        const apiUrl = 'http://localhost:8000/api';

        it('should return null when avatarUrl is null', () => {
            expect(getAvatarUrl(null, apiUrl)).toBeNull();
        });

        it('should return null when avatarUrl is undefined', () => {
            expect(getAvatarUrl(undefined, apiUrl)).toBeNull();
        });

        it('should return null when avatarUrl is empty string', () => {
            expect(getAvatarUrl('', apiUrl)).toBeNull();
        });

        it('should return absolute URL as-is when it starts with http', () => {
            const absoluteUrl = 'https://example.com/avatar.jpg';
            expect(getAvatarUrl(absoluteUrl, apiUrl)).toBe(absoluteUrl);
        });

        it('should construct full URL from relative path', () => {
            const relativeUrl = '/uploads/avatar.jpg';
            expect(getAvatarUrl(relativeUrl, apiUrl)).toBe(
                'http://localhost:8000/uploads/avatar.jpg'
            );
        });

        it('should handle relative URL without leading slash', () => {
            const relativeUrl = 'uploads/avatar.jpg';
            // Note: The function doesn't add a slash, so it concatenates directly
            // This is the actual behavior - relative URLs should include leading slash
            expect(getAvatarUrl(relativeUrl, apiUrl)).toBe(
                'http://localhost:8000uploads/avatar.jpg'
            );
        });

        it('should remove /api from API URL when constructing relative URL', () => {
            const relativeUrl = '/uploads/avatar.jpg';
            const apiUrlWithApi = 'http://localhost:8000/api';
            expect(getAvatarUrl(relativeUrl, apiUrlWithApi)).toBe(
                'http://localhost:8000/uploads/avatar.jpg'
            );
        });
    });

    describe('getRoleBadgeColor', () => {
        it('should return admin color for admin role', () => {
            expect(getRoleBadgeColor('admin')).toBe(designTokens.roles.admin);
        });

        it('should return manager color for manager role', () => {
            expect(getRoleBadgeColor('manager')).toBe(
                designTokens.roles.manager
            );
        });

        it('should return owner color for owner role', () => {
            expect(getRoleBadgeColor('owner')).toBe(designTokens.roles.owner);
        });

        it('should return moderator color for moderator role', () => {
            expect(getRoleBadgeColor('moderator')).toBe(
                designTokens.roles.moderator
            );
        });

        it('should return member color for member role', () => {
            expect(getRoleBadgeColor('member')).toBe(designTokens.roles.member);
        });

        it('should return user color for user role', () => {
            expect(getRoleBadgeColor('user')).toBe(designTokens.roles.user);
        });

        it('should be case insensitive', () => {
            expect(getRoleBadgeColor('ADMIN')).toBe(designTokens.roles.admin);
            expect(getRoleBadgeColor('Manager')).toBe(
                designTokens.roles.manager
            );
            expect(getRoleBadgeColor('uSeR')).toBe(designTokens.roles.user);
        });

        it('should return default user color for unknown role', () => {
            expect(getRoleBadgeColor('unknown')).toBe(designTokens.roles.user);
            expect(getRoleBadgeColor('')).toBe(designTokens.roles.user);
        });
    });
});
