import ProductCard from './ProductCard';

interface Product {
    id: number;
    name: string;
  sale_price: number | null;
  first_price?: number | null;
  brand: string | null;
    shop: string;
    images: string[];
  link: string | null;
    category: string[];
    onClick?: () => void;
}

interface ProductGridProps {
  products: Product[];
}

const ProductGrid = ({ products }: ProductGridProps) => {
  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 text-lg font-montserrat">Товары не найдены</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-9 w-full py-8">
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
