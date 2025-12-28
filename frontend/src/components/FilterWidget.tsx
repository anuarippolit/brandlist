'use client';

import { useState, useEffect } from 'react';

interface FilterWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: { minPrice?: number; maxPrice?: number; sort?: string }) => void;
  currentSort?: string;
  currentMinPrice?: number;
  currentMaxPrice?: number;
}

const FilterWidget = ({ 
  isOpen, 
  onClose, 
  onApply, 
  currentSort = 'relevance',
  currentMinPrice,
  currentMaxPrice
}: FilterWidgetProps) => {
  const [minPrice, setMinPrice] = useState<number | ''>('');
  const [maxPrice, setMaxPrice] = useState<number | ''>('');
  const [sort, setSort] = useState<string>(currentSort);
  const [showSortDropdown, setShowSortDropdown] = useState(false);

  // Update local state when props change (when widget is reopened)
  useEffect(() => {
    if (isOpen) {
      setMinPrice(currentMinPrice ?? '');
      setMaxPrice(currentMaxPrice ?? '');
      setSort(currentSort);
    }
  }, [isOpen, currentMinPrice, currentMaxPrice, currentSort]);

  if (!isOpen) return null;

  const handleApply = () => {
    onApply({
      minPrice: minPrice !== '' ? Number(minPrice) : undefined,
      maxPrice: maxPrice !== '' ? Number(maxPrice) : undefined,
      sort: sort !== 'relevance' ? sort : undefined,
    });
    onClose();
  };

  const sortOptions = [
    { value: 'relevance', label: 'Без сортировки' },
    { value: 'price_asc', label: 'В порядке возрастания' },
    { value: 'price_desc', label: 'В порядке убывания' },
  ];

  const currentSortLabel = sortOptions.find((opt) => opt.value === sort)?.label || 'No sort';

  return (
    <>
      {/* Blurred background */}
      <div
        className="fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Filter Widget */}
      <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
        <div
          className="bg-white border border-gray-200 rounded-lg shadow-lg p-8 w-full max-w-md mx-4 pointer-events-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Price inputs */}
          <div className="mb-6">
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <input
                  type="number"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value === '' ? '' : Number(e.target.value))}
                  placeholder="Min"
                  className="w-full pb-2 border-b-2 border-gray-300 focus:border-black outline-none text-black placeholder-gray-400 text-lg bg-transparent font-montserrat"
                />
              </div>
              <div className="flex-1">
                <input
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value === '' ? '' : Number(e.target.value))}
                  placeholder="Max"
                  className="w-full pb-2 border-b-2 border-gray-300 focus:border-black outline-none text-black placeholder-gray-400 text-lg bg-transparent font-montserrat"
                />
              </div>
            </div>
          </div>

          {/* Sort dropdown */}
          <div className="mb-6 relative">
            <div className="flex items-center justify-between">
              <span className="text-black text-lg font-montserrat">Сортировать</span>
              <div className="relative">
                <button
                  onClick={() => setShowSortDropdown(!showSortDropdown)}
                  className="text-black text-lg hover:opacity-70 font-montserrat"
                >
                  {currentSortLabel}
                </button>
                {showSortDropdown && (
                  <div className="absolute right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg min-w-[150px] z-10">
                    {sortOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => {
                          setSort(option.value);
                          setShowSortDropdown(false);
                        }}
                        className={`w-full text-left px-4 py-2 hover:bg-black hover:text-white transition-colors font-montserrat ${
                          sort === option.value ? 'bg-black text-white' : 'text-black'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Apply button */}
          <div className="flex justify-end">
            <button
              onClick={handleApply}
              className="bg-black text-white px-8 py-3 rounded-full hover:opacity-90 transition-opacity text-lg font-medium font-montserrat"
            >
              Применить сортировку
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default FilterWidget;

