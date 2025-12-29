'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Hook to get current number of columns based on screen size
const useColumnCount = () => {
  const [columnCount, setColumnCount] = useState(5); // Default to desktop

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;
    
    const updateColumnCount = () => {
      const width = window.innerWidth;
      if (width >= 1280) {
        setColumnCount(5); // xl: desktop
      } else if (width >= 1024) {
        setColumnCount(4); // lg: tablet landscape
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

interface Brand {
  brand: string;
  count: number;
}

interface BrandDictionaryProps {
  apiUrl?: string;
}

const BrandDictionary = ({ apiUrl }: BrandDictionaryProps) => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const router = useRouter();
  const columnCount = useColumnCount();

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        const response = await fetch('/api/brands');
        if (!response.ok) throw new Error('Failed to fetch brands');
        const data = await response.json();
        
        // Filter out duplicate brands (case-insensitive), keeping the first occurrence
        const seen = new Set<string>();
        const uniqueBrands = data.filter((brand: Brand) => {
          const lowerKey = brand.brand.toLowerCase();
          if (seen.has(lowerKey)) {
            return false;
          }
          seen.add(lowerKey);
          return true;
        });
        
        // Sort brands alphabetically
        const sorted = uniqueBrands.sort((a: Brand, b: Brand) => a.brand.localeCompare(b.brand));
        setBrands(sorted);
      } catch (error) {
        console.error('Error fetching brands:', error);
      }
    };

    fetchBrands();
  }, []);

  const handleBrandClick = (brandName: string) => {
    router.push(`/search/${encodeURIComponent(brandName)}`);
  };

  // Group brands by first letter
  const groupedBrands: { [key: string]: Brand[] } = {};
  brands.forEach((brand) => {
    const firstLetter = brand.brand.charAt(0).toUpperCase();
    if (!groupedBrands[firstLetter]) {
      groupedBrands[firstLetter] = [];
    }
    groupedBrands[firstLetter].push(brand);
  });

  // Get all letters and sort them
  const letters = Object.keys(groupedBrands).sort();

  if (brands.length === 0 || letters.length === 0) {
    return null;
  }

  // Function to distribute letters across columns
  const distributeLetters = (numColumns: number, isMobile: boolean) => {
    const cols: string[][] = Array(numColumns).fill(null).map(() => []);
    
    if (isMobile && numColumns === 2) {
      // Mobile: A-J in first column, K-Z in second column
      const splitPoint = 'J';
      letters.forEach((letter) => {
        if (letter <= splitPoint) {
          cols[0].push(letter);
        } else {
          cols[1].push(letter);
        }
      });
    } else {
      // Desktop/Tablet: balanced distribution
      const totalBrands = letters.reduce((sum, letter) => sum + groupedBrands[letter].length, 0);
      const targetBrandsPerColumn = totalBrands / numColumns;
      const columnCounts: number[] = Array(numColumns).fill(0);
      let currentColumn = 0;

      letters.forEach((letter) => {
        const brandCount = groupedBrands[letter].length;
        
        // Sequential fill: move to next column when current column has enough brands
        if (currentColumn < numColumns - 1 && 
            columnCounts[currentColumn] > 0 && 
            columnCounts[currentColumn] >= targetBrandsPerColumn * 0.8) {
          currentColumn++;
        }
        
        cols[currentColumn].push(letter);
        columnCounts[currentColumn] += brandCount;
      });
    }

    return cols;
  };

  // Compute columns based on actual screen size
  const isMobile = columnCount === 2;
  const columns = distributeLetters(columnCount, isMobile);

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-8 sm:gap-10 md:gap-12 lg:gap-16 xl:gap-20 w-full py-6 sm:py-8 pl-4 sm:pl-6 md:pl-8">
      {columns.map((columnLetters, colIndex) => (
        <div key={colIndex} className={`flex flex-col ${colIndex === 0 ? 'pl-2 sm:pl-4' : ''}`}>
          {columnLetters.map((letter) => (
            <div key={letter} className="mb-8 sm:mb-10 md:mb-12">
              <div className="text-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-3 sm:mb-4 md:mb-5 font-playfair italic">{letter}</div>
              <div className="flex flex-col gap-2 sm:gap-3">
                {groupedBrands[letter].map((brand) => (
                  <button
                    key={brand.brand}
                    onClick={() => handleBrandClick(brand.brand)}
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
                    {brand.brand}
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

export default BrandDictionary;
