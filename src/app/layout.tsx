import type { Metadata } from "next";
import { Inter, Noto_Sans_Arabic } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter"
});

const notoSansArabic = Noto_Sans_Arabic({ 
  subsets: ["arabic"],
  variable: "--font-arabic"
});

if (typeof window === 'undefined') {
  globalThis.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
    key: () => null,
    length: 0,
  } as Storage;
}

export const metadata: Metadata = {
  title: "Arabic STT SaaS - Professional Arabic Speech-to-Text Platform",
  description: "Complete self-hosted Arabic speech-to-text platform with advanced editor, speaker diarization, and multi-format export. Optimized for Arabic dialects including Iraqi.",
  keywords: ["Arabic STT", "Speech to Text", "Arabic transcription", "تفريغ صوتي", "نسخ صوتي", "Iraqi Arabic"],
  authors: [{ name: "Arabic STT Team" }],
  openGraph: {
    title: "Arabic STT SaaS - Professional Arabic Speech-to-Text",
    description: "Professional Arabic speech-to-text platform with advanced editing capabilities",
    type: "website",
    locale: "ar_SA"
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#1e40af" />
      </head>
      <body className={`${inter.variable} ${notoSansArabic.variable} antialiased bg-gray-50 font-arabic text-gray-900`}>
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}