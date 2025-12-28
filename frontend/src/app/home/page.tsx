'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import SearchBar from '@/components/SearchBar';
import BrandsShopsToggle from '@/components/BrandsShopsToggle';
import BrandDictionary from '@/components/BrandDictionary';
import ShopDictionary from '@/components/ShopDictionary';
import Footer from '@/components/Footer';

const Home = () => {
  const [activeTab, setActiveTab] = useState<'brands' | 'shops'>('brands');

  return (
    <div className="bg-black min-h-screen flex flex-col">
      {/* Navbar - separate zone with BRANDLIST */}
      <div className="bg-white pt-12 pb-8">
        <div className="max-w-[calc(100vw-64px)] mx-auto px-4 sm:px-6 md:px-8">
          <Header />
        </div>
      </div>

      {/* Main content block - card container */}
      <div className="flex-1 flex flex-col bg-white" style={{ marginTop: '-1px' }}>
        <div 
          className="mx-4 sm:mx-6 md:mx-8 flex-1 flex flex-col"
          style={{
            backgroundColor: '#f3f0e9',
            boxShadow: 'inset 0 0 2px rgba(0, 0, 0, 0.02)',
            borderTopLeftRadius: '1.5rem',
            borderTopRightRadius: '1.5rem',
            ...(activeTab === 'shops' && {
              borderBottomLeftRadius: '0',
              borderBottomRightRadius: '0',
            }),
          }}
        >
          <div className={`px-4 sm:px-8 md:px-12 lg:px-16 ${activeTab === 'shops' ? 'pt-8 sm:pt-10 md:pt-12 pb-0' : 'py-8 sm:py-10 md:py-12'} flex flex-col flex-1`}>
            <div className="py-6">
              <SearchBar />
            </div>
            <BrandsShopsToggle activeTab={activeTab} onTabChange={setActiveTab} />
            <div className="flex-1">
              {activeTab === 'brands' ? <BrandDictionary /> : <ShopDictionary />}
            </div>
          </div>
        </div>
      </div>
      {activeTab === 'shops' && (
        <div className="bg-[#5291f7] text-white py-3 overflow-hidden w-screen relative" style={{ left: '50%', right: '50%', marginLeft: '-50vw', marginRight: '-50vw' }}>
          <div className="flex whitespace-nowrap animate-scroll-infinite">
            {[...Array(10)].map((_, i) => (
              <span key={i} className="inline-block px-8 text-lg font-montserrat">
                Новые магазины скоро добавятся 🤩
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer - separate zone */}
      <Footer />
    </div>
  );
};

export default Home;
