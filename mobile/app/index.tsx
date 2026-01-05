import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import { View, ActivityIndicator } from 'react-native';
import { designTokens } from '../theme';

export default function Index() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (loading) {
            return;
        }

        // If user is authenticated, redirect to home tab
        if (user) {
            router.replace('/(tabs)/home');
        } else {
            // If not authenticated, show home screen
            router.replace('/(auth)/home');
        }
    }, [user, loading, router]);

    // Show loading indicator while checking auth
    return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
            <ActivityIndicator size="large" color={designTokens.app.primary} />
        </View>
    );
}

