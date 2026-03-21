import '@/app/globals.css';
import { AppProvider } from '@/context/AppContext';

export const metadata = {
    title: '岐黄AI · 智能中医诊断系统',
    description: '传承千年中医智慧，融合现代人工智能技术',
};

export default function RootLayout({ children }) {
    return (
        <html lang="zh-CN">
            <head>
                <meta charSet="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </head>
            <body>
                <AppProvider>
                    <div className="page-container">
                        {children}
                    </div>
                </AppProvider>
            </body>
        </html>
    );
}
