'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

interface Product {
  id: number;
  category: string[];
  name: string;
  brand: string | null;
  sale_price: number | null;
  first_price?: number | null;
  images: string[];
  link: string | null;
  shop: string;
}

interface Props {
  params: Promise<{
    query: string;
    productId: string;
  }>;
}

export default function ProductDetail({ params }: Props) {
  const { query, productId } = use(params);
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/products/${productId}`);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const data = await response.json();
        setProduct(data);
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  if (loading) {
    return (
      <div className="bg-white min-h-screen">
        <div className="max-w-[1500px] mx-auto px-8">
          <Header />
          <div className="text-center py-12">
            <p className="text-gray-400 font-montserrat">Загрузка...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="bg-white min-h-screen">
        <div className="max-w-[1500px] mx-auto px-8">
          <Header />
          <div className="text-center py-12">
            <p className="text-gray-400 font-montserrat">Продукт не найден.</p>
          </div>
        </div>
      </div>
    );
  }

  const images = product.images || [];
  const mainImage = images[selectedImageIndex] || images[0] || '/images/no-image.png';
  const lastCategory = product.category && product.category.length > 0 
    ? product.category[product.category.length - 1] 
    : null;

  return (
    <div className="bg-white min-h-screen flex flex-col">
      <div className="max-w-[1500px] mx-auto px-8 mb-36 flex-1">
        <Header />
        <div className="py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Left: Images */}
          <div>
            {/* Main big image */}
            <div className="w-full aspect-square mb-4 rounded-lg overflow-hidden bg-gray-100">
              <img
                src={mainImage}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src = '/images/no-image.png';
                }}
              />
            </div>
            
            {/* Thumbnail list */}
            {images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {images.map((img, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 ${
                      selectedImageIndex === index ? 'border-black' : 'border-gray-200'
                    }`}
                  >
                    <img
                      src={img}
                      alt={`${product.name} ${index + 1}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = '/images/no-image.png';
                      }}
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Right: Product Info */}
          <div className="flex flex-col">
            <h1 className="text-2xl font-bold text-black mb-4 font-montserrat text-left">{product.name}</h1>
            
            {product.brand && (
              <p className="text-xl text-gray-600 mb-4 font-montserrat text-left">{product.brand}</p>
            )}

            {lastCategory && (
              <p className="text-lg text-gray-500 mb-4 font-montserrat text-left">{lastCategory}</p>
            )}

            {/* Prices */}
            <div className="flex items-baseline gap-3 mb-6 text-left">
              {product.sale_price !== null ? (
                <>
                  {product.first_price && product.first_price !== product.sale_price && (
                  <p className="text-gray-400 text-lg line-through font-montserrat">
                    {product.first_price.toLocaleString()} ₸
                  </p>
                  )}
                  <p className="text-2xl font-bold text-black font-montserrat">
                    {product.sale_price.toLocaleString()} ₸
                  </p>
                </>
              ) : (
                <p className="text-2xl font-bold text-black font-montserrat">
                  {product.first_price ? `${product.first_price.toLocaleString()} ₸` : 'Цена не указана'}
                </p>
              )}
            </div>

            {/* Buy now button */}
            {product.link && (
              <a
                href={product.link}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black text-white px-12 py-4 rounded-full hover:opacity-90 transition-opacity text-lg font-medium text-center inline-block w-fit font-montserrat mb-4"
              >
                Перейти в магазин
              </a>
            )}

            {/* Brandlist info block */}
            <div className="bg-[#5291f7] text-white px-12 py-4 w-fit mt-16 relative">
              <div className="absolute -top-3 -left-3 w-12 h-12" style={{ borderTop: '6px solid black', borderLeft: '6px solid black' }}></div>
              <div className="absolute -bottom-3 -right-3 w-12 h-12" style={{ borderBottom: '6px solid black', borderRight: '6px solid black' }}></div>
              <div className="text-white text-xl font-montserrat leading-relaxed">
                Проверенно Brandlist на оригинальность товара 🤖
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
