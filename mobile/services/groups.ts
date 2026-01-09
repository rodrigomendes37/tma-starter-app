import apiClient from './api';
import { Group, GroupDetail } from '../types';

export async function getUserGroups(): Promise<Group[]> {
    const response = await apiClient.get<Group[]>('/api/groups');
    return response.data;
}

export async function getGroupDetail(groupId: number): Promise<GroupDetail> {
    const response = await apiClient.get<GroupDetail>(`/api/groups/${groupId}`);
    return response.data;
}
