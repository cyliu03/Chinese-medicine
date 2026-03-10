import './globals.css';
import { DiagnosisProvider } from '@/context/DiagnosisContext';

export const metadata = {
  title: '岐黄AI — 中医智能辅助诊疗系统',
  description: '基于深度学习的中医四诊合参智能系统，通过望闻问切采集患者信息，AI辅助推荐方剂，医生审核确保安全有效。',
  keywords: '中医,AI,对症下药,望闻问切,方剂推荐,中药,智能诊疗',
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>
        <DiagnosisProvider>
          <div className="page-container">
            {children}
          </div>
        </DiagnosisProvider>
      </body>
    </html>
  );
}
