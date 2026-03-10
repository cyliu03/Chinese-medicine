'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
    const pathname = usePathname();

    const isActive = (path) => {
        if (path === '/') return pathname === '/';
        return pathname.startsWith(path);
    };

    return (
        <header className="header">
            <Link href="/" className="header-logo">
                <span className="header-logo-icon">🏥</span>
                <div>
                    <div className="header-title">岐黄AI</div>
                    <div className="header-subtitle">中医智能辅助诊疗系统</div>
                </div>
            </Link>
            <nav className="header-nav">
                <Link
                    href="/"
                    className={`header-nav-link ${isActive('/') && pathname === '/' ? 'active' : ''}`}
                >
                    🏠 首页
                </Link>
                <Link
                    href="/patient"
                    className={`header-nav-link ${isActive('/patient') ? 'active' : ''}`}
                >
                    🩺 患者问诊
                </Link>
                <Link
                    href="/doctor"
                    className={`header-nav-link ${isActive('/doctor') ? 'active' : ''}`}
                >
                    👨‍⚕️ 医生工作台
                </Link>
            </nav>
        </header>
    );
}
