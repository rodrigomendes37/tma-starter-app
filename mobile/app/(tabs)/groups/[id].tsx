import { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import {
    Card,
    Text,
    ActivityIndicator,
    Snackbar,
    Appbar,
    Avatar,
    useTheme,
} from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useLocalSearchParams, useRouter } from 'expo-router';
import ProtectedRoute from '../../../components/ProtectedRoute';
import InfoBadge from '../../../components/InfoBadge';
import { getGroupDetail } from '../../../services/groups';
import { GroupDetail } from '../../../types';
import { designTokens } from '../../../theme';

export default function GroupDetailScreen() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const router = useRouter();
    const theme = useTheme();
    const groupId = parseInt(id || '0', 10);
    const [avatarErrors, setAvatarErrors] = useState<Set<number>>(new Set());

    const {
        data: group,
        isLoading,
        error,
        refetch,
        isRefetching,
    } = useQuery<GroupDetail>({
        queryKey: ['groupDetail', groupId],
        queryFn: () => getGroupDetail(groupId),
        enabled: Boolean(groupId && groupId > 0),
    });

    function getRoleBadgeColor(role: string | null | undefined): string {
        if (!role) return theme.colors.surfaceVariant;
        switch (role.toLowerCase()) {
            case 'admin':
                return designTokens.roles.admin;
            case 'manager':
                return designTokens.roles.manager;
            case 'owner':
                return designTokens.roles.owner;
            case 'moderator':
                return designTokens.roles.moderator;
            case 'member':
            case 'user':
            default:
                return designTokens.roles.member;
        }
    }

    function getRoleBadgeTextColor(role: string | null | undefined): string {
        if (!role) return theme.colors.onSurface;
        // All role badges use white text for better contrast
        return designTokens.roles.textOnColored;
    }

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
                    <Appbar.BackAction onPress={() => router.back()} />
                    <Appbar.Content
                        title={group?.name || 'Group'}
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
                            Error loading group. Please try again.
                        </Snackbar>
                    )}

                    {group && (
                        <>
                            {/* Group Info Card */}
                            <Card style={styles.card} mode="elevated">
                                <Card.Content style={styles.cardContent}>
                                    <View style={styles.groupHeader}>
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
                                                size={32}
                                                color={theme.colors.primary}
                                            />
                                        </View>
                                        <View style={styles.groupInfo}>
                                            <Text
                                                variant="headlineSmall"
                                                style={styles.groupName}
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
                                    {group.description && (
                                        <Text
                                            variant="bodyLarge"
                                            style={styles.description}
                                        >
                                            {group.description}
                                        </Text>
                                    )}
                                </Card.Content>
                            </Card>

                            {/* Members Section */}
                            <View style={styles.section}>
                                <Text
                                    variant="titleLarge"
                                    style={styles.sectionTitle}
                                >
                                    Members
                                </Text>

                                {group.members && group.members.length === 0 ? (
                                    <Card
                                        style={styles.emptyCard}
                                        mode="outlined"
                                    >
                                        <Card.Content
                                            style={styles.emptyContent}
                                        >
                                            <MaterialCommunityIcons
                                                name="account-off-outline"
                                                size={48}
                                                color={
                                                    theme.colors
                                                        .onSurfaceVariant
                                                }
                                                style={styles.emptyIcon}
                                            />
                                            <Text
                                                variant="bodyMedium"
                                                style={styles.emptyText}
                                            >
                                                No members in this group yet.
                                            </Text>
                                        </Card.Content>
                                    </Card>
                                ) : (
                                    <View style={styles.membersList}>
                                        {group.members?.map((member) => (
                                            <Card
                                                key={member.user_id}
                                                style={styles.memberCard}
                                                mode="elevated"
                                            >
                                                <Card.Content
                                                    style={
                                                        styles.memberCardContent
                                                    }
                                                >
                                                    <View
                                                        style={styles.memberRow}
                                                    >
                                                        {/* Avatar */}
                                                        <View
                                                            style={
                                                                styles.avatarContainer
                                                            }
                                                        >
                                                            {member.avatar_url &&
                                                            !avatarErrors.has(
                                                                member.user_id
                                                            ) ? (
                                                                <Avatar.Image
                                                                    size={64}
                                                                    source={{
                                                                        uri: member.avatar_url,
                                                                        cache: 'force-cache',
                                                                    }}
                                                                    onError={(
                                                                        error
                                                                    ) => {
                                                                        if (
                                                                            __DEV__
                                                                        ) {
                                                                            console.log(
                                                                                `Avatar load error for user ${member.user_id}:`,
                                                                                member.avatar_url,
                                                                                error
                                                                            );
                                                                        }
                                                                        setAvatarErrors(
                                                                            (
                                                                                prev
                                                                            ) =>
                                                                                new Set(
                                                                                    prev
                                                                                ).add(
                                                                                    member.user_id
                                                                                )
                                                                        );
                                                                    }}
                                                                    onLoadStart={() => {
                                                                        if (
                                                                            __DEV__
                                                                        ) {
                                                                            console.log(
                                                                                `Loading avatar for user ${member.user_id}:`,
                                                                                member.avatar_url
                                                                            );
                                                                        }
                                                                    }}
                                                                    onLoad={() => {
                                                                        if (
                                                                            __DEV__
                                                                        ) {
                                                                            console.log(
                                                                                `Avatar loaded successfully for user ${member.user_id}`
                                                                            );
                                                                        }
                                                                    }}
                                                                />
                                                            ) : (
                                                                <Avatar.Text
                                                                    size={64}
                                                                    label={
                                                                        member.first_name &&
                                                                        member.last_name
                                                                            ? `${member.first_name[0]}${member.last_name[0]}`
                                                                            : member.username[0].toUpperCase()
                                                                    }
                                                                />
                                                            )}
                                                        </View>

                                                        {/* Member Info */}
                                                        <View
                                                            style={
                                                                styles.memberInfo
                                                            }
                                                        >
                                                            <Text
                                                                variant="titleMedium"
                                                                style={
                                                                    styles.memberName
                                                                }
                                                            >
                                                                {member.first_name &&
                                                                member.last_name
                                                                    ? `${member.first_name} ${member.last_name}`
                                                                    : member.username}
                                                            </Text>
                                                            <Text
                                                                variant="bodySmall"
                                                                style={
                                                                    styles.memberEmail
                                                                }
                                                            >
                                                                {member.email}
                                                            </Text>
                                                            {member.user_role && (
                                                                <View
                                                                    style={[
                                                                        styles.roleBadge,
                                                                        {
                                                                            backgroundColor:
                                                                                getRoleBadgeColor(
                                                                                    member.user_role
                                                                                ),
                                                                        },
                                                                    ]}
                                                                >
                                                                    <Text
                                                                        style={[
                                                                            styles.roleBadgeText,
                                                                            {
                                                                                color: getRoleBadgeTextColor(
                                                                                    member.user_role
                                                                                ),
                                                                            },
                                                                        ]}
                                                                    >
                                                                        {member.user_role
                                                                            .charAt(
                                                                                0
                                                                            )
                                                                            .toUpperCase() +
                                                                            member.user_role.slice(
                                                                                1
                                                                            )}
                                                                    </Text>
                                                                </View>
                                                            )}
                                                        </View>
                                                    </View>
                                                </Card.Content>
                                            </Card>
                                        ))}
                                    </View>
                                )}
                            </View>
                        </>
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
        marginBottom: designTokens.spacing.xxl,
        borderRadius: designTokens.borderRadius.lg,
    },
    cardContent: {
        padding: designTokens.spacing.xl,
    },
    groupHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: designTokens.spacing.md,
    },
    iconContainer: {
        width: 64,
        height: 64,
        borderRadius: 32,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: designTokens.spacing.lg,
    },
    groupInfo: {
        flex: 1,
    },
    groupName: {
        fontWeight: '600',
        marginBottom: designTokens.spacing.sm,
    },
    description: {
        marginTop: designTokens.spacing.sm,
        opacity: 0.7,
        lineHeight: 22,
    },
    section: {
        marginTop: designTokens.spacing.sm,
    },
    sectionTitle: {
        fontWeight: '600',
        marginBottom: designTokens.spacing.lg,
    },
    membersList: {
        gap: designTokens.spacing.md,
    },
    memberCard: {
        borderRadius: designTokens.borderRadius.md,
        marginBottom: designTokens.spacing.md,
    },
    memberCardContent: {
        padding: designTokens.spacing.lg,
    },
    memberRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    avatarContainer: {
        marginRight: designTokens.spacing.lg,
    },
    memberInfo: {
        flex: 1,
    },
    memberName: {
        fontWeight: '600',
        marginBottom: designTokens.spacing.xs,
    },
    memberEmail: {
        opacity: 0.7,
        marginBottom: designTokens.spacing.sm,
    },
    roleBadge: {
        alignSelf: 'flex-start',
        paddingHorizontal: 10,
        paddingTop: 1,
        paddingBottom: designTokens.spacing.xs,
        minWidth: 60,
        justifyContent: 'center',
        alignItems: 'center',
    },
    roleBadgeText: {
        fontSize: 12,
        fontWeight: '600',
        includeFontPadding: false,
        lineHeight: 16,
    },
    emptyCard: {
        marginTop: designTokens.spacing.lg,
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
    emptyText: {
        textAlign: 'center',
        opacity: 0.7,
    },
    snackbar: {
        marginBottom: designTokens.spacing.lg,
    },
});
