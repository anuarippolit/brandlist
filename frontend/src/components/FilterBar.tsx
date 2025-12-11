import { useState } from 'react';

const FilterBar = ({
  onApplyFilters,
  query,
}: {
  onApplyFilters: (filters: any, page?: number) => void;
  query:string|null;
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSize, setSelectedSize] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string[]>([]);
  const [selectedColor, setSelectedColor] = useState<string[]>([]);
  const [minPrice, setMinPrice] = useState<number | null>(null);
  const [maxPrice, setMaxPrice] = useState<number | null>(null);

  const toggleModal = () => setIsModalOpen(!isModalOpen);

  const formatSize = (size: string) => {
    return size.replace(/[^\d]/g, '');
  };

  const toggleValue = (arr: string[], value: string) =>
    arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value];

  const applyFilters = () => {
    const filters: Record<string, any> = {};

    if (selectedSize.length) filters.size = selectedSize.map(formatSize);
    if (selectedBrand.length) filters.brand = selectedBrand;
    if (selectedCategory.length) filters.category = selectedCategory;
    if (selectedColor.length) filters.color = selectedColor;
    if (minPrice !== null) filters.price_min = String(minPrice);
    if (maxPrice !== null) filters.price_max = String(maxPrice);
    if (query) filters.name = query;


    console.log('Applying Filters:', filters);
    onApplyFilters(filters, 1);
    setIsModalOpen(false);
  };

  return (
    <div className="sm:text-[16px] text-[14px] flex overflow-x-auto gap-2 mb-8 mt-[30px] px-4 sm:px-0 sm:ml-[270px] no-scrollbar">
      <button
        onClick={toggleModal}
        className="border-1 border-borderColor bg-black text-borderColor px-7 py-0.25 rounded-full hover:bg-customPurple hover:text-white"
      >
        Фильтр
      </button>

      {[...selectedCategory, ...selectedBrand, ...selectedSize, ...selectedColor]
        .map((label, index) => (
          <div
            key={index}
            className="whitespace-nowrap border-1 border-borderColor text-white px-7 py-0.5 rounded-full bg-customPurple"
          >
            {label}
          </div>
        ))}

      {(minPrice !== null || maxPrice !== null) && (
        <div className="whitespace-nowrap border-1 border-borderColor text-white px-7 py-0.5 rounded-full bg-customPurple">
          {minPrice || 0} — {maxPrice || '∞'}
        </div>
      )}

      {isModalOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
          onClick={toggleModal}
        >
          <div
            className="relative bg-darkgrayColor text-borderColor rounded-lg p-6 w-[1040px] h-[750px] flex flex-col"
            style={{ border: '1px solid #6B7280' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={toggleModal}
              className="absolute top-4 right-4 text-borderColor hover:text-white"
            >
              ✕
            </button>

            <div className="text-center mb-6 text-2xl font-bold text-white">
              Фильтр
            </div>

            <div className="grid gap-6 overflow-y-auto">
              {/* Категории */}
              <div>
                <div className="text-borderColor mb-2">Категория</div>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Кроссовки',
                    'Верхняя Одежда',
                    'Брюки',
                    'Рубашки',
                    'Майки',
                    'Пиджаки и костюмы',
                    'Джинсы',
                    'Худи и свитшоты',
                    'Футболки',
                    'Спортивные костюмы',
                    'Нижнее белье',
                    'Носки',
                    'Свитеры и кардиганы',
                  ].map((category) => (
                    <button
                      key={category}
                      onClick={() =>
                        setSelectedCategory((prev) =>
                          toggleValue(prev, category)
                        )
                      }
                      className={`px-4 py-0.5 rounded-full ${
                        selectedCategory.includes(category)
                          ? 'bg-customPurple text-white'
                          : 'bg-darkgrayColor border-2 border-borderColor text-borderColor'
                      } hover:bg-customPurple hover:text-white`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {/* Бренды */}
              <div>
                <div className="text-borderColor mb-2">Бренд</div>
                <div className="flex flex-wrap gap-2">
                  {[
                    'AdidasOriginals',
                    'Nike',
                    'Puma',
                    'Karl Lagerfeld',
                    'Reebok',
                    'New Balance',
                    'Asics',
                    'Converse',
                    'Onitsuka Tiger',
                    'Lacoste',
                    'Vans',
                    'Calvin Klein',
                  ].map((brand) => (
                    <button
                      key={brand}
                      onClick={() =>
                        setSelectedBrand((prev) => toggleValue(prev, brand))
                      }
                      className={`px-4 py-0.5 rounded-full ${
                        selectedBrand.includes(brand)
                          ? 'bg-customPurple text-white'
                          : 'bg-darkgrayColor border-2 border-borderColor text-borderColor'
                      } hover:bg-customPurple hover:text-white`}
                    >
                      {brand}
                    </button>
                  ))}
                </div>
              </div>

              {/* Размеры */}
              <div>
                <div className="text-borderColor mb-2">Размер</div>
                <div className="flex flex-wrap gap-2">
                  {[
                    '36',
                    '37',
                    '38',
                    '39',
                    '40',
                    '41',
                    '42',
                    '43',
                    '3',
                    '3.5',
                    '4',
                    '7',
                    '8',
                    '9',
                  ].map((size) => (
                    <button
                      key={size}
                      onClick={() =>
                        setSelectedSize((prev) => toggleValue(prev, size))
                      }
                      className={`px-4 py-0.5 rounded-full ${
                        selectedSize.includes(size)
                          ? 'bg-customPurple text-white'
                          : 'bg-darkgrayColor border-2 border-borderColor text-borderColor'
                      } hover:bg-customPurple hover:text-white`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>

              {/* Цена */}
              <div>
                <div className="text-borderColor mb-2">Цена</div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={minPrice || ''}
                    onChange={(e) => setMinPrice(Number(e.target.value))}
                    placeholder="Мин."
                    className="w-24 p-0.5 bg-darkgrayColor border-2 border-borderColor rounded-full text-borderColor text-sm px-2"
                  />
                  <span className="text-borderColor">—</span>
                  <input
                    type="number"
                    value={maxPrice || ''}
                    onChange={(e) => setMaxPrice(Number(e.target.value))}
                    placeholder="Макс."
                    className="w-24 p-0.5 bg-darkgrayColor border-2 border-borderColor rounded-full text-borderColor text-sm px-2"
                  />
                </div>
              </div>

              {/* Цвета */}
              <div>
                <div className="text-borderColor mb-2">Цвет</div>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Золотой',
                    'Черный',
                    'Белый',
                    'Синий',
                    'Серый',
                    'Зеленый',
                    'Желтый',
                    'Оранжевый',
                    'Красный',
                    'Розовый',
                    'Фиолетовый',
                    'Хаки',
                  ].map((color) => (
                    <button
                      key={color}
                      onClick={() =>
                        setSelectedColor((prev) => toggleValue(prev, color))
                      }
                      className={`px-4 py-2 rounded-full ${
                        selectedColor.includes(color)
                          ? 'bg-customPurple text-white'
                          : 'bg-darkgrayColor border-2 border-borderColor text-borderColor'
                      } hover:bg-customPurple hover:text-white`}
                    >
                      {color}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={applyFilters}
              className="mt-6 px-6 py-3 bg-customPurple text-white rounded-full hover:bg-customPurple"
            >
              Показать результаты
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterBar;
