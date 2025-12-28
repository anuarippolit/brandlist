'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import SearchBar from '@/components/SearchBar';
import ProductGrid from '@/components/ProductGrid';
import Footer from '@/components/Footer';

const FavoritesPage = () => {
  const [favorites, setFavorites] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const storedFavorites = JSON.parse(
      localStorage.getItem('favorites') || '[]'
    );
    setFavorites(storedFavorites);
  }, []);

  useEffect(() => {
    const handleStorageChange = () => {
      const storedFavorites = JSON.parse(
        localStorage.getItem('favorites') || '[]'
      );
      setFavorites(storedFavorites);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <div className="bg-black min-h-screen flex flex-col">
      {/* Navbar - separate zone with Header */}
      <div className="bg-white">
        <div className="max-w-[calc(100vw-64px)] mx-auto px-4 sm:px-6 md:px-8">
          <Header />
        </div>
      </div>

      {/* Main content block - card container */}
      <div className="flex-1 bg-white">
        <div 
          className="mx-4 sm:mx-6 md:mx-8"
          style={{
            backgroundColor: '#f3f0e9',
            boxShadow: 'inset 0 0 2px rgba(0, 0, 0, 0.02)',
            borderTopLeftRadius: '1.5rem',
            borderTopRightRadius: '1.5rem',
          }}
        >
          <div className="px-4 sm:px-8 md:px-12 lg:px-16 py-8 sm:py-10 md:py-12">
            <div className="py-4">
              <SearchBar />
            </div>
            <h1 className="text-3xl font-bold text-black mb-8 mt-8 font-montserrat">Избранное</h1>
            <ProductGrid
              products={favorites.map((product) => ({
                ...product,
                onClick: () => {
                  const query = encodeURIComponent(product.name || '');
                  router.push(`/search/${query}/${product.id}`);
                },
              }))}
            />
          </div>
        </div>
      </div>

      {/* Footer - separate zone */}
      <Footer />
    </div>
  );
};

export default FavoritesPage;
