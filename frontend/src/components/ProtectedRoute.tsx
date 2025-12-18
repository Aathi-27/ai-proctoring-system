'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser, User } from '@/lib/auth';
import Cookies from 'js-cookie';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: Array<'candidate' | 'invigilator' | 'admin' | 'system_integrator'>;
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const token = Cookies.get('access_token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        
        if (allowedRoles && !allowedRoles.includes(currentUser.role)) {
          router.push('/unauthorized');
          return;
        }
        
        setUser(currentUser);
      } catch (error) {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router, allowedRoles]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
