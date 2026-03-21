'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useApp } from '@/context/AppContext';

export default function Header() {
    const pathname = usePathname();
    const { userType, diagnoses, logout } = useApp();
    const pendingCount = diagnoses.filter(d => d.status === 'pending').length;

    return (
        <header className="header">
            <Link href="/" className="header-logo">
                <div className="header-logo-icon">🏥</div>
                <div>
                    <div className="header-title">岐黄AI</div>
                    <div className="header-subtitle">智能中医诊断系统</div>
                </div>
            </Link>

            <nav className="header-nav">
                <Link 
                    href="/" 
                    className={`header-nav-link ${pathname === '/' ? 'active' : ''}`}
                >
                    首页
                </Link>
                <Link 
                    href="/patient" 
                    className={`header-nav-link ${pathname?.startsWith('/patient') ? 'active' : ''}`}
                >
                    患者端
                </Link>
                <Link 
                    href="/doctor" 
                    className={`header-nav-link ${pathname?.startsWith('/doctor') ? 'active' : ''}`}
                >
                    医生端
                    {pendingCount > 0 && (
                        <span className="nav-badge">{pendingCount}</span>
                    )}
                </Link>
            </nav>
        </header>
    );
}
