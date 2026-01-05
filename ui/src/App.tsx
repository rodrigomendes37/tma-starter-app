import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { SidebarProvider } from './contexts/SidebarContext.tsx';
import ProtectedRoute from './components/auth/ProtectedRoute.tsx';
import Layout from './components/layout/Layout.tsx';
// Auth pages
import LoginPage from './pages/auth/LoginPage.tsx';

// Course pages
import CoursesPage from './pages/courses/CoursesPage.tsx';
import CourseDetailPage from './pages/courses/CourseDetailPage.tsx';

// User pages
import UsersPage from './pages/users/UsersPage.tsx';
import CreateUserPage from './pages/users/CreateUserPage.tsx';
import EditUserPage from './pages/users/EditUserPage.tsx';

// Group pages
import GroupsPage from './pages/groups/GroupsPage.tsx';
import GroupDetailPage from './pages/groups/GroupDetailPage.tsx';

// Common pages
import HomePage from './pages/common/HomePage';
import UnauthorizedPage from './pages/common/UnauthorizedPage.tsx';
import './globals.css';

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <SidebarProvider>
                    <Routes>
                        {/* Public routes */}
                        <Route path="/login" element={<LoginPage />} />

                        {/* Protected routes */}
                        <Route
                            path="/"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <HomePage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />

                        {/* Admin routes */}
                        <Route
                            path="/dashboard/courses"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <CoursesPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/courses/:courseId"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <CourseDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <UsersPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users/new"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <CreateUserPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/users/:userId/edit"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <EditUserPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/groups"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <GroupsPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/dashboard/groups/:groupId"
                            element={
                                <ProtectedRoute>
                                    <Layout>
                                        <GroupDetailPage />
                                    </Layout>
                                </ProtectedRoute>
                            }
                        />

                        {/* Error pages */}
                        <Route
                            path="/unauthorized"
                            element={<UnauthorizedPage />}
                        />

                        {/* Catch all - redirect to login */}
                        <Route
                            path="*"
                            element={<Navigate to="/login" replace />}
                        />
                    </Routes>
                </SidebarProvider>
            </AuthProvider>
        </BrowserRouter>
    );
}
