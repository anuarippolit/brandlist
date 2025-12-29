'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Hook to get current number of columns based on screen size
const useColumnCount = () => {
  const [columnCount, setColumnCount] = useState(4); // Default to desktop

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;
    
    const updateColumnCount = () => {
      const width = window.innerWidth;
      if (width >= 1024) {
        setColumnCount(4); // lg: tablet landscape and desktop
      } else if (width >= 768) {
        setColumnCount(3); // md: tablet portrait
      } else {
        setColumnCount(2); // mobile
      }
    };

    updateColumnCount();
    window.addEventListener('resize', updateColumnCount);
    return () => window.removeEventListener('resize', updateColumnCount);
  }, []);

  return columnCount;
};

interface Shop {
  id: number;
  name: string;
  logo?: string;
}

interface ShopDictionaryProps {
  apiUrl?: string;
}

const ShopDictionary = ({ apiUrl }: ShopDictionaryProps) => {
  const [shops, setShops] = useState<Shop[]>([]);
  const router = useRouter();
  const columnCount = useColumnCount();

  useEffect(() => {
    const fetchShops = async () => {
      try {
        const response = await fetch('/api/shops');
        if (!response.ok) throw new Error('Failed to fetch shops');
        const data = await response.json();
        setShops(data);
      } catch (error) {
        console.error('Error fetching shops:', error);
      }
    };

    fetchShops();
  }, []);

  const handleShopClick = (shopName: string) => {
    router.push(`/search/${encodeURIComponent(shopName)}`);
  };

  // Group shops by first letter
  const groupedShops: { [key: string]: Shop[] } = {};
  shops.forEach((shop) => {
    const firstLetter = shop.name.charAt(0).toUpperCase();
    if (!groupedShops[firstLetter]) {
      groupedShops[firstLetter] = [];
    }
    groupedShops[firstLetter].push(shop);
  });

  // Get all letters and sort them
  const letters = Object.keys(groupedShops).sort();

  // Function to distribute letters across columns
  const distributeLetters = (numColumns: number, isMobile: boolean) => {
    const cols: string[][] = Array(numColumns).fill(null).map(() => []);
    
    if (isMobile && numColumns === 2) {
      // Mobile: A and C in first column, F and S in second column
      letters.forEach((letter) => {
        if (letter === 'A' || letter === 'C') {
          cols[0].push(letter);
        } else if (letter === 'F' || letter === 'S') {
          cols[1].push(letter);
        }
      });
    } else {
      // Desktop/Tablet: balanced distribution
      const totalShops = letters.reduce((sum, letter) => sum + groupedShops[letter].length, 0);
      const targetShopsPerColumn = totalShops / numColumns;
      const columnCounts: number[] = Array(numColumns).fill(0);
      let currentColumn = 0;

      letters.forEach((letter) => {
        const shopCount = groupedShops[letter].length;
        
        // Sequential fill: move to next column when current column has enough shops
        if (currentColumn < numColumns - 1 && 
            columnCounts[currentColumn] > 0 && 
            columnCounts[currentColumn] >= targetShopsPerColumn * 0.8) {
          currentColumn++;
        }
        
        cols[currentColumn].push(letter);
        columnCounts[currentColumn] += shopCount;
      });
    }

    return cols;
  };

  // Compute columns based on actual screen size
  const isMobile = columnCount === 2;
  const columns = distributeLetters(columnCount, isMobile);

  if (shops.length === 0 || letters.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 sm:gap-10 md:gap-12 lg:gap-16 w-full py-6 sm:py-8 pl-4 sm:pl-6 md:pl-8">
      {columns.map((columnLetters, colIndex) => (
        <div key={colIndex} className={`flex flex-col ${colIndex === 0 ? 'pl-2 sm:pl-4' : ''}`}>
          {columnLetters.map((letter) => (
            <div key={letter} className="mb-8 sm:mb-10 md:mb-12">
              <div className="text-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-3 sm:mb-4 md:mb-5 font-playfair italic">{letter}</div>
              <div className="flex flex-col gap-2 sm:gap-3">
                {groupedShops[letter].map((shop) => (
                  <button
                    key={shop.id}
                    onClick={() => handleShopClick(shop.name)}
                    className="text-black text-left text-sm sm:text-base hover:opacity-60 transition-opacity font-montserrat leading-tight"
                    style={{ 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: '1.4',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}
                  >
                    {shop.name}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default ShopDictionary;

