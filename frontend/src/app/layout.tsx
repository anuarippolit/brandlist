import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { Analytics } from '@vercel/analytics/react';
import GTMScript from '@/components/GTMScript';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: {
    default: 'BrandList - Поиск брендовой одежды и обуви в Казахстане',
    template: '%s | BrandList',
  },
  description: 'BrandList - поиск брендовой одежды и обуви в магазинах Казахстана. Найдите Adidas, Nike, Puma, Salomon и другие популярные бренды по лучшим ценам. Поиск по брендам, магазинам и категориям.',
  keywords: [
    'BrandList',
    'brandlist',
    'брендовая одежда Казахстан',
    'брендовая обувь Казахстан',
    'магазины одежды Казахстан',
    'Adidas Казахстан',
    'Nike Казахстан',
    'Puma Казахстан',
    'Salomon Казахстан',
    'кроссовки Казахстан',
    'ботинки Казахстан',
    'поиск брендов',
    'скидки на бренды',
    'купить брендовую одежду',
    'купить брендовую обувь',
  ],
  authors: [{ name: 'BrandList' }],
  creator: 'BrandList',
  publisher: 'BrandList',
  metadataBase: new URL('https://brandlist.kz'),
  alternates: {
    canonical: '/',
  },
  icons: {
    icon: '/favicon.ico',
  },
  openGraph: {
    title: 'BrandList - Поиск брендовой одежды и обуви в Казахстане',
    description: 'BrandList - поиск брендовой одежды и обуви в магазинах Казахстана. Найдите Adidas, Nike, Puma и другие популярные бренды.',
    url: 'https://brandlist.kz',
    siteName: 'BrandList',
    locale: 'ru_KZ',
    type: 'website',
    images: [
      {
        url: 'https://brandlist.kz/images/logo.png',
        width: 1200,
        height: 630,
        alt: 'BrandList - Поиск брендовой одежды и обуви',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BrandList - Поиск брендовой одежды и обуви в Казахстане',
    description: 'Найдите брендовую одежду и обувь в магазинах Казахстана',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    // Добавьте здесь коды верификации когда зарегистрируетесь в поисковиках
    // google: 'your-google-verification-code',
    // yandex: 'your-yandex-verification-code',
  },
};

const RootLayout = ({ children }: { children: React.ReactNode }) => {
  const gtmId = process.env.NEXT_PUBLIC_GTM_ID || '';

  const jsonLdWebsite = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'BrandList',
    url: 'https://brandlist.kz',
    description: 'Поиск брендовой одежды и обуви в магазинах Казахстана',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://brandlist.kz/search/{search_term_string}',
      },
      'query-input': 'required name=search_term_string',
    },
  };

  const jsonLdOrganization = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'BrandList',
    url: 'https://brandlist.kz',
    logo: 'https://brandlist.kz/images/logo.png',
    description: 'Поиск брендовой одежды и обуви в магазинах Казахстана',
    sameAs: [],
  };

  return (
    <html lang="ru">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        {/* JSON-LD структурированные данные для лучшего SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLdWebsite),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLdOrganization),
          }}
        />
        <GTMScript gtmId={gtmId} />
        {children}
        <Analytics />
      </body>
    </html>
  );
};

export default RootLayout;
