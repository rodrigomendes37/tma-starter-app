import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from '../contexts/AuthContext';
import { ErrorBoundary } from '../components/ErrorBoundary';
import appTheme from '../theme';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
        },
    },
});

// Enable better error logging and debugging
if (__DEV__) {
    // Log all unhandled errors
    const originalError = console.error;
    console.error = (...args: unknown[]) => {
        originalError.apply(console, args);
        // Log full error details
        if (args[0] instanceof Error) {
            console.error('Error name:', args[0].name);
            console.error('Error message:', args[0].message);
            console.error('Error stack:', args[0].stack);
        }
    };

    // Log unhandled promise rejections
    if (typeof global !== 'undefined') {
        type UnhandledRejectionHandler =
            | ((event: PromiseRejectionEvent) => void)
            | null;
        const originalUnhandledRejection = (
            global as {
                onunhandledrejection?: UnhandledRejectionHandler;
            }
        ).onunhandledrejection;
        (
            global as {
                onunhandledrejection?: UnhandledRejectionHandler;
            }
        ).onunhandledrejection = (event: PromiseRejectionEvent) => {
            console.error('Unhandled Promise Rejection:', event.reason);
            if (event.reason instanceof Error) {
                console.error('Stack:', event.reason.stack);
            }
            if (originalUnhandledRejection) {
                originalUnhandledRejection(event);
            }
        };
    }
}

export default function RootLayout() {
    return (
        <SafeAreaProvider>
            <ErrorBoundary>
                <PaperProvider theme={appTheme}>
                    <QueryClientProvider client={queryClient}>
                        <AuthProvider>
                            <Stack
                                screenOptions={{ headerShown: Boolean(false) }}
                            >
                                <Stack.Screen name="index" />
                                <Stack.Screen name="(auth)/home" />
                                <Stack.Screen name="(auth)/login" />
                                <Stack.Screen name="(tabs)" />
                            </Stack>
                        </AuthProvider>
                    </QueryClientProvider>
                </PaperProvider>
            </ErrorBoundary>
        </SafeAreaProvider>
    );
}
