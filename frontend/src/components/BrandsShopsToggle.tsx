'use client';

interface BrandsShopsToggleProps {
  activeTab: 'brands' | 'shops';
  onTabChange: (tab: 'brands' | 'shops') => void;
}

const BrandsShopsToggle = ({ activeTab, onTabChange }: BrandsShopsToggleProps) => {
  return (
    <div className="flex justify-center w-full px-4">
      <div className="flex gap-2 bg-gray-200 rounded-full p-1 w-full max-w-[300px] my-6 sm:my-8">
        <button
          onClick={() => onTabChange('brands')}
          className={`flex-1 px-4 sm:px-6 py-2.5 sm:py-3 rounded-full font-medium transition-all font-montserrat text-sm sm:text-base ${
            activeTab === 'brands'
              ? 'bg-black text-white'
              : 'bg-transparent text-gray-600'
          }`}
        >
          Brands
        </button>
        <button
          onClick={() => onTabChange('shops')}
          className={`flex-1 px-4 sm:px-6 py-2.5 sm:py-3 rounded-full font-medium transition-all font-montserrat text-sm sm:text-base ${
            activeTab === 'shops'
              ? 'bg-black text-white'
              : 'bg-transparent text-gray-600'
          }`}
        >
          Shops
        </button>
      </div>
    </div>
  );
};

export default BrandsShopsToggle;
