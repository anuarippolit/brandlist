import Link from 'next/link';
import React from 'react';

// Improved pixel patterns for each letter in "BRANDLIST" - cleaner, more distinguishable
const pixelPatterns: { [key: string]: boolean[][] } = {
  'B': [
    [true, true, true, true, false],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, true, true, true, false],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, true, true, true, false],
  ],
  'R': [
    [true, true, true, true, false],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, true, true, true, false],
    [true, false, true, false, false],
    [true, false, false, true, false],
    [true, false, false, false, true],
  ],
  'A': [
    [false, false, true, false, false],
    [false, true, false, true, false],
    [true, false, false, false, true],
    [true, true, true, true, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
  ],
  'N': [
    [true, false, false, false, true],
    [true, true, false, false, true],
    [true, false, true, false, true],
    [true, false, false, true, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
  ],
  'D': [
    [true, true, true, true, false],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, false, false, false, true],
    [true, true, true, true, false],
  ],
  'L': [
    [true, false, false, false, false],
    [true, false, false, false, false],
    [true, false, false, false, false],
    [true, false, false, false, false],
    [true, false, false, false, false],
    [true, false, false, false, false],
    [true, true, true, true, true],
  ],
  'I': [
    [true, true, true, true, true],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [true, true, true, true, true],
  ],
  'S': [
    [false, true, true, true, true],
    [true, false, false, false, false],
    [true, false, false, false, false],
    [false, true, true, true, false],
    [false, false, false, false, true],
    [false, false, false, false, true],
    [true, true, true, true, false],
  ],
  'T': [
    [true, true, true, true, true],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
    [false, false, true, false, false],
  ],
};

const Header = () => {
  const renderLetter = (letter: string) => {
    const pattern = pixelPatterns[letter] || [];
    return (
      <div className="inline-block flex-shrink-0">
        <div className="grid grid-cols-5 gap-0">
          {pattern.map((row, rowIndex) =>
            row.map((filled, colIndex) => (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`w-3 h-3 sm:w-4 sm:h-4 md:w-5 md:h-5 lg:w-6 lg:h-6 xl:w-7 xl:h-7 flex-shrink-0 ${
                  filled ? 'bg-black' : 'bg-transparent'
                }`}
              />
            ))
          )}
        </div>
      </div>
    );
  };

  return (
    <nav className="w-full py-4 sm:py-6 md:py-8">
      <Link href="/home" passHref>
        <div className="flex items-center justify-center cursor-pointer flex-wrap" style={{ gap: '4px' }}>
          {['B', 'R', 'A', 'N', 'D', 'L', 'I', 'S', 'T'].map((letter, index) => (
            <React.Fragment key={index}>{renderLetter(letter)}</React.Fragment>
          ))}
        </div>
      </Link>
    </nav>
  );
};

export default Header;

