'use client';

import { useState, useEffect } from 'react';
import { trackProductCardClick } from '@/utils/analytics';

interface ProductCardProps {
  product: {
    id: number;
    name: string;
    sale_price: number | null;
    first_price?: number | null;
    brand: string | null;
    shop: string;
    images: string[];
    link: string | null;
    category: string[];
  };
  onClick?: () => void;
  searchQuery?: string;
}

const ProductCard = ({ product, onClick, searchQuery }: ProductCardProps) => {
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    setIsFavorited(favorites.some((fav: { id: number }) => fav.id === product.id));
  }, [product.id]);

  const handleFavoriteToggle = (e: React.MouseEvent) => {
    e.stopPropagation();

    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

    if (isFavorited) {
      favorites = favorites.filter((fav: { id: number }) => fav.id !== product.id);
    } else {
      favorites.push(product);
    }

    localStorage.setItem('favorites', JSON.stringify(favorites));
    setIsFavorited(!isFavorited);
    
    // Trigger storage event for other components
    window.dispatchEvent(new Event('storage'));
  };

  const handleCardClick = () => {
    // Track product card click
    trackProductCardClick({
      ...product,
      searchQuery,
    });
    
    if (onClick) {
      onClick();
    }
  };

  return (
    <div
      className="cursor-pointer flex flex-col h-full"
      onClick={handleCardClick}
    >
      {/* Image with 3:4 aspect ratio */}
      <div className="w-full aspect-[4/5] mb-4 relative overflow-hidden bg-gray-100">
        <img
          src={product.images?.[0] || '/images/no-image.png'}
          alt={product.name}
          className="h-full w-full object-cover"
          onError={(e) => {
            e.currentTarget.src = '/images/no-image.png';
          }}
        />
        <button
          className="absolute top-2 right-2 p-2 hover:opacity-70 transition-opacity"
          onClick={handleFavoriteToggle}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill={isFavorited ? '#000000' : 'none'}
            stroke={isFavorited ? '#000000' : '#000000'}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-black"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
        </button>
      </div>

      {/* Text content - left aligned */}
      <div className="text-left">
        <p className="text-black text-base font-medium mb-1 font-montserrat">{product.name}</p>
        {product.brand && (
          <p className="text-gray-600 text-sm mb-2 font-montserrat">{product.brand}</p>
        )}
        <div className="flex items-baseline gap-2">
          {product.sale_price !== null ? (
            <>
              {product.first_price && product.first_price !== product.sale_price && (
                <p className="text-gray-400 text-xs line-through font-montserrat">
                {product.first_price.toLocaleString()} ₸
                </p>
            )}
              <p className="text-black text-base font-medium font-montserrat">
                {product.sale_price.toLocaleString()} ₸
        </p>
            </>
          ) : (
            <p className="text-black text-base font-medium font-montserrat">
              {product.first_price ? `${product.first_price.toLocaleString()} ₸` : 'Цена не указана'}
        </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
