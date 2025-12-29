'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import SearchBar from '@/components/SearchBar';
import ProductGrid from '@/components/ProductGrid';
import FilterWidget from '@/components/FilterWidget';
import Footer from '@/components/Footer';

interface SearchResultsProps {
  params: Promise<{ query: string }>;
}

const SearchResults = ({ params }: SearchResultsProps) => {
  const router = useRouter();
  const [query, setQuery] = useState<string>('');
  const [products, setProducts] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filters, setFilters] = useState<{
    minPrice?: number;
    maxPrice?: number;
    sort?: string;
  }>({});

  useEffect(() => {
    const init = async () => {
      const resolvedParams = await params;
      const searchQuery = decodeURIComponent(resolvedParams.query || '');
      setQuery(searchQuery);
      setPage(1);
      setProducts([]);
      setFilters({});
    };
    init();
  }, [params]);

  const fetchProducts = useCallback(async (pageNum: number, currentFilters = filters) => {
    if (!query) return;

    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        q: query,
        page: pageNum.toString(),
        per_page: '28',
        ...(currentFilters.sort && { sort: currentFilters.sort }),
        ...(currentFilters.minPrice && { min_price: currentFilters.minPrice.toString() }),
        ...(currentFilters.maxPrice && { max_price: currentFilters.maxPrice.toString() }),
      });

      const response = await fetch(`/api/search?${params}`);
      if (!response.ok) throw new Error(`Failed: ${response.status}`);
      
      const data = await response.json();
      
      if (pageNum === 1) {
        setProducts(data.items || []);
      } else {
        setProducts((prev) => [...prev, ...(data.items || [])]);
      }
      
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('❌ Fetch failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, [query, filters]);

  useEffect(() => {
    if (query) {
      fetchProducts(1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  const handleFilterApply = (newFilters: { minPrice?: number; maxPrice?: number; sort?: string }) => {
    setFilters(newFilters);
    setPage(1);
    fetchProducts(1, newFilters);
  };

  const handleLoadMore = () => {
    if (page < totalPages && !isLoading) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchProducts(nextPage);
    }
  };

  return (
    <div className="bg-black min-h-screen flex flex-col">
      {/* Navbar - separate zone with Header */}
      <div className="bg-white">
        <div className="max-w-[calc(100vw-64px)] mx-auto px-4 sm:px-6 md:px-8">
          <Header />
        </div>
      </div>

      {/* Main content block - card container */}
      <div className="flex-1 bg-white">
        <div 
          className="mx-4 sm:mx-6 md:mx-8"
          style={{
            backgroundColor: '#f3f0e9',
            boxShadow: 'inset 0 0 2px rgba(0, 0, 0, 0.02)',
            borderTopLeftRadius: '1.5rem',
            borderTopRightRadius: '1.5rem',
          }}
        >
          <div className="px-4 sm:px-8 md:px-12 lg:px-16 py-8 sm:py-10 md:py-12">
            <div className="py-4">
              <SearchBar
                initialQuery={query}
                showFilter={true}
                onFilterClick={() => setIsFilterOpen(true)}
              />
            </div>

            <FilterWidget
              isOpen={isFilterOpen}
              onClose={() => setIsFilterOpen(false)}
              onApply={handleFilterApply}
              currentSort={filters.sort || 'relevance'}
              currentMinPrice={filters.minPrice}
              currentMaxPrice={filters.maxPrice}
            />

            <ProductGrid
              products={products.map((p) => ({
                ...p,
                onClick: () => router.push(`/search/${encodeURIComponent(query)}/${p.id}`),
                searchQuery: query,
              }))}
            />

            {isLoading && (
              <div className="text-center py-8">
                <p className="text-gray-400 font-montserrat">Загрузка...</p>
              </div>
            )}

            {page < totalPages && !isLoading && (
              <div className="text-center py-8">
                <button
                  onClick={handleLoadMore}
                  className="bg-black text-white px-8 py-3 rounded-full hover:opacity-90 transition-opacity font-montserrat"
                >
                  Загрузить еще
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer - separate zone */}
      <Footer />
    </div>
  );
};

export default SearchResults;
