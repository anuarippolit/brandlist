import Link from 'next/link';
import React, { useState, useEffect } from 'react';

const Navbar = () => {
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

  return (
    <nav className="flex justify-between items-center w-full h-16 px-4 sm:px-8 bg-black text-white">
      {/* Brand name */}
      {/* <div className="flex items-center justify-center ml-[-130px] sm:ml-[340px] sm:justify-start w-full sm:w-auto"> */}
      <div className="flex items-center justify-start ml-2 sm:ml-[340px] sm:mr-[100px] w-auto">
        <Link href="/home" passHref>
          <h1 className="text-[24px] sm:text-[30px] leading-[40px] sm:leading-[52px] tracking-tight cursor-pointer">
            <span className="font-bangers text-white">brand</span>
            <span className="font-bangers text-[#6F00FF]">list</span>
          </h1>
        </Link>
      </div>

      {/* Favorites */}
      <div className="flex items-center gap-4 mr-4 sm:mr-[340px] relative w-auto">
        <Link href="/favorites" passHref>
          <div className="relative">
            <img
              src="/images/heart.png"
              alt="Favorites"
              className="w-[20px] h-[18px] cursor-pointer"
            />
            {favoriteCount > 0 && (
              <span className="absolute -top-2 -right-3 bg-customPurple text-white text-xs px-1.5 py-0.5 rounded-full">
                {favoriteCount}
              </span>
            )}
          </div>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
