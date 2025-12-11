import ProductCard from './ProductCard';

const ProductGrid = ({
  products,
}: {
  products: {
    id: number;
    name: string;
    sale_price: number;
    first_price?: number;
    brand: string;
    shop: string;
    images: string[];
    link: string;
    category: string[];
    onClick?: () => void;
  }[];
}) => {
  return (
    <div
      className="bg-[#171717] p-[32px] rounded-lg grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 w-full sm:max-w-[950px] mx-auto mb-0 px-2 sm:px-8 pt-8"
      style={{ minHeight: '100px' }}
    >
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onClick={product.onClick}
        />
      ))}
    </div>
  );
};

export default ProductGrid;

// import { useEffect, useRef, useState, useCallback } from 'react';
// import ProductCard from './ProductCard';

// const ProductGrid = ({ message }: { message: string }) => {
//   const [products, setProducts] = useState<any[]>([]);
//   const [offset, setOffset] = useState(0);
//   const [hasMore, setHasMore] = useState(true);
//   const [loading, setLoading] = useState(false);
//   const observerRef = useRef<HTMLDivElement | null>(null);

//   const loadMore = useCallback(async () => {
//     if (loading || !hasMore) return;
//     setLoading(true);
//     const res = await fetch(
//       `http://localhost:8000/chat/send?message=${encodeURIComponent(
//         message
//       )}&offset=${offset}&limit=20`
//     );

//     // Log raw response body for debugging
//     const raw = await res.text();
//     console.log('📦 Raw API response:', raw);

//     try {
//       const data = JSON.parse(raw);
//       if (!data.products || !Array.isArray(data.products)) {
//         console.error('❌ Malformed data', data);
//         setLoading(false);
//         return;
//       }

//       setProducts((prev) => [...prev, ...data.products]);
//       setOffset((prev) => prev + 20);
//       setHasMore(data.has_more);
//     } catch (e) {
//       console.error('❌ Failed to parse JSON:', e);
//     }
//     setLoading(false);

//     const data = await res.json();
//     setProducts((prev) => [...prev, ...data.products]);
//     setOffset((prev) => prev + 20);
//     setHasMore(data.has_more);
//     setLoading(false);

//     console.log('🧾 Response:', data); // ⬅️ check what the API actually returns
//   }, [offset, message, loading, hasMore]);

//   useEffect(() => {
//     const observer = new IntersectionObserver(
//       (entries) => {
//         if (entries[0].isIntersecting) {
//           loadMore();
//         }
//       },
//       { threshold: 1 }
//     );
//     const el = observerRef.current;
//     if (el) observer.observe(el);
//     return () => {
//       if (el) observer.unobserve(el);
//     };
//   }, [loadMore]);

//   useEffect(() => {
//     setProducts([]);
//     setOffset(0);
//     setHasMore(true);
//     loadMore(); // initial load
//   }, [message]);

//   return (
//     <div
//       className="bg-[#171717] p-[10px] rounded-lg grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 w-full max-w-[950px] mx-auto mb-5 px-8 pt-8"
//       style={{ minHeight: '100px' }}
//     >
//       {products.map((product) => (
//         <ProductCard
//           key={product.id}
//           product={product}
//           onClick={product.onClick}
//         />
//       ))}
//       {hasMore && <div ref={observerRef} className="h-10 col-span-full" />}
//     </div>
//   );
// };

// export default ProductGrid;
