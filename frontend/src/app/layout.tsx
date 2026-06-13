import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = { title: 'VaultRAG', description: 'Air‑gapped Enterprise KB' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
