'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import ProductGrid from '@/components/ProductGrid';
import { useRouter } from 'next/navigation';
import Breadcrumb from '@/components/Breadcrumb';

const FavoritesPage = () => {
  const [favorites, setFavorites] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const storedFavorites = JSON.parse(
      localStorage.getItem('favorites') || '[]'
    );
    setFavorites(storedFavorites);
  }, []);

  const handleProductClick = (product: { id: number; name: string }) => {
    router.push(`/search/${encodeURIComponent(product.name)}/${product.id}`);
  };

  const handleFavoriteToggle = (productId: number) => {
    const updatedFavorites = favorites.filter((fav) => fav.id !== productId);
    setFavorites(updatedFavorites);
    localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
  };

  return (
    <div className="bg-black min-h-screen">
      <Navbar />
      <Breadcrumb breadcrumbs={[{ label: '', href: '' }]} />
      {/* <h1 className="text-[35px] font-normal mb-6 ml-4 sm:ml-[365px] mt-[10px] ">Избранное</h1>
      {favorites.length > 0 ? (
        <ProductGrid
        products={favorites.map((product) => ({
          ...product,
          name: product.name.length > 17 ? product.name.slice(0, 17) + "..." : product.name,
          onClick: () => handleProductClick(product),
        }))}
      />      
      ) : (
      <div className="flex flex-grow items-center justify-center">
        <p className="text-gray-400 text-xl">Нет избранных товаров.</p>
      </div>       */}
      <main className="px-8">
        <h1 className="text-[35px] font-normal mb-6 ml-4 sm:ml-[340px] mt-[10px] text-white">
          Избранное
        </h1>
        {favorites.length > 0 ? (
          <ProductGrid
            products={favorites.map((product) => ({
              id: product.id,
              name: product.name,
              brand: product.brand,
              shop: product.shop,
              sale_price: product.sale_price,
              first_price: product.first_price,
              category: product.category,
              link: product.link,
              images: product.images || [], // fallback for card
              onClick: () => handleProductClick(product),
            }))}
          />
        ) : (
          <div className="flex flex-grow items-center justify-center mt-10">
            <p className="text-gray-400 text-xl">Нет избранных товаров.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default FavoritesPage;
