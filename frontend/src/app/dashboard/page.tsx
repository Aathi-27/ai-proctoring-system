'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getCurrentUser, logout, User } from '@/lib/auth';

function DashboardContent() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Exam Proctoring System</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">{user?.full_name}</span>
              <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                {user?.role}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Welcome, {user?.full_name}!</h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-600">Email: {user?.email}</p>
                <p className="text-gray-600">Role: {user?.role}</p>
                <p className="text-gray-600">
                  Account Status: {user?.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>

              {user?.role === 'admin' && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Admin Functions</h3>
                  <p className="text-gray-600">
                    As an admin, you have access to user management and system configuration.
                  </p>
                </div>
              )}

              {user?.role === 'candidate' && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Candidate Dashboard</h3>
                  <p className="text-gray-600">
                    Welcome to your exam dashboard. Your exams will appear here.
                  </p>
                </div>
              )}

              {user?.role === 'invigilator' && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Invigilator Dashboard</h3>
                  <p className="text-gray-600">
                    Monitor assigned exams and candidate activities here.
                  </p>
                </div>
              )}

              {user?.role === 'system_integrator' && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">System Integrator Dashboard</h3>
                  <p className="text-gray-600">
                    Manage system integrations and API access.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
