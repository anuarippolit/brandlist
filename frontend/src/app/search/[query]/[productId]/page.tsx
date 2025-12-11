'use client';

import { use, useEffect, useState } from 'react';
import Breadcrumb from '@/components/Breadcrumb';
import Navbar from '@/components/Navbar';

interface Product {
  id: number;
  category: string[];
  name: string;
  brand: string;
  description?: string;
  sale_price: number;
  first_price?: number;
  colors: string[];
  images: string[];
  sizes: string[];
  shop: string;
  link: string;
}

interface Props {
  params: Promise<{
    query: string;
    productId: string;
  }>;
}

export default function ProductDetail({ params }: Props) {
  const { query, productId } = use(params);
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/products/${productId}`
        );
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const data = await response.json();
        setProduct(data);

        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        setIsFavorited(
          favorites.some((fav: { id: number }) => fav.id === data.id)
        );
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId, query]);

  const handleFavoriteToggle = () => {
    if (!product) return;
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

    if (isFavorited) {
      favorites = favorites.filter(
        (fav: { id: number }) => fav.id !== product.id
      );
    } else {
      favorites.push(product);
    }

    localStorage.setItem('favorites', JSON.stringify(favorites));
    setIsFavorited(!isFavorited);
  };

  if (loading)
    return <div className="text-white text-center mt-6">Loading...</div>;
  if (!product)
    return (
      <div className="text-gray-400 text-center mt-6">Продукт не найден.</div>
    );

  return (
    <div className="bg-black text-white min-h-screen">
      <Navbar />
      <Breadcrumb
        breadcrumbs={[
          { label: 'Поиск', href: '/home' },
          { label: query || '...', href: `/search/${query}` },
          { label: product.name },
        ]}
      />

      {/* Layout Wrapper */}
      <div className="flex justify-center mt-4 px-4">
        <div className="flex flex-col lg:flex-row gap-[10px] sm:gap-6 w-full max-w-[1050px]">
          {/* Images */}
          <div className="w-full lg:flex-[3] grid grid-rows-2 gap-4">
            {/* First row: 2 columns */}
            <div className="grid grid-cols-2 gap-4">
              {product.images?.slice(0, 2).map((img, index) => (
                <div
                  key={index}
                  className="bg-gray-200 aspect-[3/4] w-full rounded-lg relative overflow-hidden"
                >
                  <img
                    src={img}
                    alt={`${product.name} ${index + 1}`}
                    className="absolute top-0 left-0 w-full h-full object-cover rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src = '/images/no-image.png';
                    }}
                  />
                  {index === 1 && (
                    <button
                      className="absolute top-2 right-2 text-white"
                      onClick={handleFavoriteToggle}
                    >
                      <img
                        src={
                          isFavorited
                            ? '/images/filledheart.png'
                            : '/images/blackheart.png'
                        }
                        alt="Favorite"
                        className="w-[20px] h-[18px]"
                      />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Second row: 3 columns */}
            <div className="grid grid-cols-3 gap-4">
              {product.images?.slice(2, 5).map((img, index) => (
                <div
                  key={index + 2}
                  className="bg-gray-200 aspect-[3/4] w-full rounded-lg relative overflow-hidden"
                >
                  <img
                    src={img}
                    alt={`${product.name} ${index + 3}`}
                    className="absolute top-0 left-0 w-full h-full object-cover rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src = '/images/no-image.png';
                    }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="w-full lg:flex-[2] bg-[#171717] p-6 rounded-lg font-inter h-auto my-[20px] -mt-[80px] sm:mt-0 lg:h-[650px] lg:my-0">
            {/* 1. Brand */}
            <h2 className="text-[20px] font-[500]">{product.brand}</h2>

            {/* 2. Price */}
            <div className="flex gap-3 mt-[14px]">
              {product.first_price &&
                product.first_price !== product.sale_price && (
                  <p className="text-[#919191] line-through text-[16px]">
                    {product.first_price.toLocaleString()} ₸
                  </p>
                )}
              <p className="text-white text-[16px]">
                {product.sale_price.toLocaleString()} ₸
              </p>
            </div>

            {/* 3. Button */}
            <a
              href={product.link}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-customPurple px-8 py-3 rounded-3xl text-white font-[500] hover:bg-purple-500 text-[16px] text-center inline-block mt-[20px]"
            >
              В магазине {product.shop}
            </a>

            {/* 4. Sizes */}
            <div className="mt-[20px] flex flex-wrap gap-2">
              {product?.sizes?.map((size, index) => (
                <span
                  key={index}
                  className="text-[#919191] border border-[#919191] px-3 py-1 rounded-xl text-center text-sm"
                >
                  {size}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
