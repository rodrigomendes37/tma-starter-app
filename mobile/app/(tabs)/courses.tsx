import React from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Card, Text, ActivityIndicator, Snackbar, Appbar, useTheme } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import ProtectedRoute from '../../components/ProtectedRoute';
import InfoBadge from '../../components/InfoBadge';
import { getUserCourses } from '../../services/courses';
import { Course } from '../../types';
import { API_URL } from '../../services/api';
import { designTokens } from '../../theme';

export default function CoursesScreen() {
    const router = useRouter();
    const theme = useTheme();
    const {
        data: courses,
        isLoading,
        error,
        refetch,
        isRefetching,
    } = useQuery<Course[]>({
        queryKey: ['userCourses'],
        queryFn: getUserCourses,
    });

    if (isLoading) {
        return (
            <View style={[styles.center, { backgroundColor: theme.colors.background }]}>
                <ActivityIndicator size="large" color={theme.colors.primary} />
            </View>
        );
    }

    return (
        <ProtectedRoute>
            <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
                <Appbar.Header elevated>
                    <Appbar.Content title="My Courses" titleStyle={styles.headerTitle} />
                </Appbar.Header>

                <ScrollView
                    style={styles.scrollView}
                    contentContainerStyle={styles.scrollContent}
                    refreshControl={
                        <RefreshControl refreshing={isRefetching} onRefresh={() => refetch()} />
                    }
                >
                    {courses && courses.length === 0 ? (
                        <Card style={styles.emptyCard} mode="outlined">
                            <Card.Content style={styles.emptyContent}>
                                <MaterialCommunityIcons 
                                    name="book-open-variant-outline" 
                                    size={64} 
                                    color={theme.colors.onSurfaceVariant} 
                                    style={styles.emptyIcon}
                                />
                                <Text variant="titleLarge" style={styles.emptyTitle}>
                                    No Courses Yet
                                </Text>
                                <Text variant="bodyMedium" style={styles.emptyText}>
                                    No courses have been assigned to your groups yet.
                                </Text>
                            </Card.Content>
                        </Card>
                    ) : (
                        courses?.map((course) => (
                            <Card
                                key={course.id}
                                style={styles.card}
                                mode="elevated"
                                onPress={() => router.push(`/(tabs)/courses/${course.id}`)}
                            >
                                {course.file_url && (
                                    <Card.Cover
                                        source={{ 
                                            uri: course.file_url.startsWith('http') 
                                                ? course.file_url 
                                                : `${API_URL}${course.file_url}` 
                                        }}
                                        style={styles.cardCover}
                                    />
                                )}
                                <Card.Content style={styles.cardContent}>
                                    <View style={styles.cardHeader}>
                                        <View style={styles.cardTitleContainer}>
                                            <Text variant="titleLarge" style={styles.cardTitle}>
                                                {course.title}
                                            </Text>
                                            {course.module_count !== undefined && (
                                                <InfoBadge
                                                    icon="book-open-variant"
                                                    text={`${course.module_count} ${course.module_count === 1 ? 'module' : 'modules'}`}
                                                />
                                            )}
                                        </View>
                                        <MaterialCommunityIcons 
                                            name="chevron-right" 
                                            size={24} 
                                            color={theme.colors.onSurfaceVariant} 
                                        />
                                    </View>
                                    {course.description && (
                                        <Text variant="bodyMedium" style={styles.description} numberOfLines={2}>
                                            {course.description}
                                        </Text>
                                    )}
                                </Card.Content>
                            </Card>
                        ))
                    )}
                </ScrollView>
                
                {error && (
                    <Snackbar 
                        visible={Boolean(error)} 
                        onDismiss={() => {}} 
                        duration={4000}
                        style={styles.snackbar}
                    >
                        Error loading courses. Please try again.
                    </Snackbar>
                )}
            </View>
        </ProtectedRoute>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        padding: designTokens.spacing.xl,
        paddingBottom: designTokens.spacing.xxxl,
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    headerTitle: {
        fontWeight: '600',
        fontSize: 20,
    },
    card: {
        marginBottom: designTokens.spacing.lg,
        borderRadius: designTokens.borderRadius.lg,
        overflow: 'hidden',
    },
    cardCover: {
        height: 160,
        borderRadius: 0,
        borderTopLeftRadius: designTokens.borderRadius.lg,
        borderTopRightRadius: designTokens.borderRadius.lg,
    },
    cardContent: {
        padding: designTokens.spacing.xl,
    },
    cardHeader: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: designTokens.spacing.md,
    },
    cardTitleContainer: {
        flex: 1,
    },
    cardTitle: {
        fontWeight: '600',
        marginBottom: designTokens.spacing.sm,
    },
    description: {
        marginTop: designTokens.spacing.xs,
        opacity: 0.7,
        lineHeight: 20,
    },
    emptyCard: {
        marginTop: designTokens.spacing.xxxl,
        borderRadius: designTokens.borderRadius.lg,
    },
    emptyContent: {
        padding: designTokens.spacing.xxxl,
        alignItems: 'center',
    },
    emptyIcon: {
        marginBottom: designTokens.spacing.lg,
        opacity: 0.5,
    },
    emptyTitle: {
        marginBottom: designTokens.spacing.sm,
        fontWeight: '600',
    },
    emptyText: {
        textAlign: 'center',
        opacity: 0.7,
    },
    snackbar: {
        marginBottom: designTokens.spacing.lg,
        zIndex: 9999,
        elevation: 9999,
    },
});

