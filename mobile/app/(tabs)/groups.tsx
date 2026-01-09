import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import {
    Card,
    Text,
    ActivityIndicator,
    Snackbar,
    Appbar,
    useTheme,
} from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import ProtectedRoute from '../../components/ProtectedRoute';
import InfoBadge from '../../components/InfoBadge';
import { getUserGroups } from '../../services/groups';
import { Group } from '../../types';
import { designTokens } from '../../theme';

export default function GroupsScreen() {
    const router = useRouter();
    const theme = useTheme();
    const {
        data: groups,
        isLoading,
        error,
        refetch,
        isRefetching,
    } = useQuery<Group[]>({
        queryKey: ['userGroups'],
        queryFn: getUserGroups,
    });

    if (isLoading) {
        return (
            <View
                style={[
                    styles.center,
                    { backgroundColor: theme.colors.background },
                ]}
            >
                <ActivityIndicator size="large" color={theme.colors.primary} />
            </View>
        );
    }

    return (
        <ProtectedRoute>
            <View
                style={[
                    styles.container,
                    { backgroundColor: theme.colors.background },
                ]}
            >
                <Appbar.Header elevated>
                    <Appbar.Content
                        title="My Groups"
                        titleStyle={styles.headerTitle}
                    />
                </Appbar.Header>

                <ScrollView
                    style={styles.scrollView}
                    contentContainerStyle={styles.scrollContent}
                    refreshControl={
                        <RefreshControl
                            refreshing={isRefetching}
                            onRefresh={() => refetch()}
                        />
                    }
                >
                    {error && (
                        <Snackbar
                            visible={Boolean(error)}
                            onDismiss={() => {}}
                            duration={4000}
                            style={styles.snackbar}
                        >
                            Error loading groups. Please try again.
                        </Snackbar>
                    )}

                    {groups && groups.length === 0 ? (
                        <Card style={styles.emptyCard} mode="outlined">
                            <Card.Content style={styles.emptyContent}>
                                <MaterialCommunityIcons
                                    name="account-group-outline"
                                    size={64}
                                    color={theme.colors.onSurfaceVariant}
                                    style={styles.emptyIcon}
                                />
                                <Text
                                    variant="titleLarge"
                                    style={styles.emptyTitle}
                                >
                                    No Groups Yet
                                </Text>
                                <Text
                                    variant="bodyMedium"
                                    style={styles.emptyText}
                                >
                                    You are not a member of any groups yet.
                                </Text>
                            </Card.Content>
                        </Card>
                    ) : (
                        groups?.map((group) => (
                            <Card
                                key={group.id}
                                style={styles.card}
                                mode="elevated"
                                onPress={() =>
                                    router.push(`/(tabs)/groups/${group.id}`)
                                }
                            >
                                <Card.Content style={styles.cardContent}>
                                    <View style={styles.cardHeader}>
                                        <View style={styles.cardHeaderLeft}>
                                            <View
                                                style={[
                                                    styles.iconContainer,
                                                    {
                                                        backgroundColor:
                                                            theme.colors
                                                                .primaryContainer,
                                                    },
                                                ]}
                                            >
                                                <MaterialCommunityIcons
                                                    name="account-group"
                                                    size={24}
                                                    color={theme.colors.primary}
                                                />
                                            </View>
                                            <View
                                                style={
                                                    styles.cardTitleContainer
                                                }
                                            >
                                                <Text
                                                    variant="titleLarge"
                                                    style={styles.cardTitle}
                                                >
                                                    {group.name}
                                                </Text>
                                                {group.member_count !==
                                                    undefined && (
                                                    <InfoBadge
                                                        icon="account"
                                                        text={`${group.member_count} ${group.member_count === 1 ? 'member' : 'members'}`}
                                                    />
                                                )}
                                            </View>
                                        </View>
                                        <MaterialCommunityIcons
                                            name="chevron-right"
                                            size={24}
                                            color={
                                                theme.colors.onSurfaceVariant
                                            }
                                        />
                                    </View>
                                    {group.description && (
                                        <Text
                                            variant="bodyMedium"
                                            style={styles.description}
                                        >
                                            {group.description}
                                        </Text>
                                    )}
                                </Card.Content>
                            </Card>
                        ))
                    )}
                </ScrollView>
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
    },
    cardContent: {
        padding: designTokens.spacing.xl,
    },
    cardHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: designTokens.spacing.md,
    },
    cardHeaderLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    iconContainer: {
        width: 48,
        height: 48,
        borderRadius: designTokens.borderRadius.xl,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: designTokens.spacing.md,
    },
    cardTitleContainer: {
        flex: 1,
    },
    cardTitle: {
        fontWeight: '600',
        marginBottom: designTokens.spacing.xs,
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
    },
});
