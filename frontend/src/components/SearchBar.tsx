'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SearchBarProps {
  initialQuery?: string;
  showFilter?: boolean;
  onFilterClick?: () => void;
}

const SearchBar = ({ initialQuery = '', showFilter = false, onFilterClick }: SearchBarProps) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const router = useRouter();
  const [favoriteCount, setFavoriteCount] = useState<number>(0);

  useEffect(() => {
    const updateFavoriteCount = () => {
      const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      setFavoriteCount(favorites.length);
    };

    updateFavoriteCount();
    window.addEventListener('storage', updateFavoriteCount);
    return () => window.removeEventListener('storage', updateFavoriteCount);
  }, []);

  const handleSearch = () => {
    if (searchQuery.trim()) {
      router.push(`/search/${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-center gap-1.5 sm:gap-2 md:gap-4 w-full px-2 sm:px-4">
        <div className="flex-1 relative max-w-none">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search"
            className="w-full pb-2 border-b-2 border-gray-300 focus:border-black outline-none text-black placeholder-gray-400 text-base sm:text-lg bg-transparent font-montserrat"
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        
        <button
          onClick={handleSearch}
          className="p-2 hover:opacity-70 transition-opacity flex-shrink-0"
          aria-label="Search"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-black"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
        </button>

        {showFilter && onFilterClick && (
          <button
            onClick={onFilterClick}
            className="p-2 hover:opacity-70 transition-opacity flex-shrink-0"
            aria-label="Filter"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-black"
            >
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
            </svg>
          </button>
        )}

        <button
          onClick={() => router.push('/favorites')}
          className="relative p-2 hover:opacity-70 transition-opacity cursor-pointer flex-shrink-0"
          aria-label="Favorites"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-black"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          {favoriteCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-black text-white text-xs px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
              {favoriteCount}
            </span>
          )}
        </button>
      </div>
      <p className="text-gray-400 text-base sm:text-lg font-montserrat mt-1 px-2 sm:px-4">
        Здесь можно найти брендовые вещи в локальных магазинах
      </p>
    </div>
  );
};

export default SearchBar;

