'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Greeting from '@/components/Greeting';
import { useEffect } from 'react';

const SearchSection = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const [icon, setIcon] = useState('/images/arrow.png');
  const handleSearch = () => {
    if (searchQuery.trim()) {
      router.push(`/search/${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleQueryClick = (query: string) => {
    setSearchQuery(query);
  };

  return (
    // <div
    //   className="absolute z-10 bg-darkgrayColor bg-opacity-95 text-white text-center rounded-[30px] w-[760px] h-[680px] mx-auto left-1/2 transform -translate-x-1/2 overflow-hidden"
    //   style={{ top: "20px" }}
    // >

    // <div
    //   className="absolute z-10 bg-darkgrayColor bg-opacity-95 text-white text-center rounded-[20px] sm:rounded-[30px] w-[94vw] sm:w-[760px] h-[83vh] sm:h-[580px] mx-auto left-1/2 transform -translate-x-1/2 overflow-hidden px-4 sm:px-10 mt-[20px]"
    //   style={{ top: '5vh' }}
    // >
    <div className="absolute z-10 bg-darkgrayColor bg-opacity-80 text-white text-center rounded-[20px] sm:rounded-[30px] w-[94vw] sm:w-[760px] h-[auto] sm:h-[580px] mx-auto left-1/2 transform -translate-x-1/2 overflow-hidden px-4 sm:px-10 top-[45%] -translate-y-1/2 sm:top-[calc(5vh+20px)] sm:translate-y-0">
      <div className="p-10 sm:mt-[8%] mt-[30px] mb-[30px]">
        {/* <h1 className="text-[32px] font-poppins font-normal leading-[42px] tracking-tight"> */}
        {/* <h1 className="text-[20px] sm:text-[32px] leading-[28px] sm:leading-[42px] font-poppins font-normal tracking-tight">
          <span className="font-extrabold italic">brand</span>
          <span className="text-[#6F00FF] font-extrabold italic">
            list
          </span>{' '}
          <span className="font-inter">— это</span>{' '}
          <span className="text-[#6F00FF] font-inter">поисковик</span>
          <br />
          <span className="font-inter">любимых брендов в</span> <br />
          <span className="font-inter">магазинах Казахстана</span>{' '}
        </h1> */}

        {/* <Greeting /> */}
        <div className="text-center max-w-[700px] mx-auto text-white mb-20 mt-8">
          <h1 className="text-[20px] sm:text-[24px] leading-[30px] sm:leading-[36px] font-poppins font-normal">
            Привет — это <span className="font-bangers">BRAND</span>
            <span className="font-bangers text-[#6F00FF]">LIST</span>, твой
            ассистент по поиску
          </h1>
          <h1 className="text-[20px] sm:text-[24px] leading-[30px] sm:leading-[36px] font-poppins font-normal mt-2">
            одежды в магазинах Казахстана.
          </h1>
        </div>

        <div className="mt-[20px] flex justify-center items-center relative w-full w-full sm:max-w-[550px] mx-auto">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Напишите свой запрос"
            className="w-full pl-5 pr-14 py-2 text-[14px] sm:text-lg rounded-full bg-inputColor text-white focus:outline-none placeholder-borderColor"
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            className="absolute right-4 sm:w-[30px] sm:h-[30px] w-[20px] h-[20px] bg-purple-600 text-white rounded-full flex items-center justify-center"
            onClick={handleSearch}
            onMouseEnter={() => setIcon('/images/whitearrow.png')}
            onMouseLeave={() => setIcon('/images/arrow.png')}
          >
            <img
              src={icon}
              alt="Search"
              className="w-[12px] h-[12px] sm:w-[12px] sm:h-[12px]"
            />
          </button>
        </div>

        {/* Popular Queries */}
        <div className="mt-8 text-gray-300 max-w-[550px] mx-auto">
          <p className="w-full text-left text-sm sm:text-[16px] text-borderColor mb-6 ml-[5px]">
            Примеры запросов:
          </p>

          <div className="scroll-hide flex w-full space-x-3 mt-2 px-1">
            {[
              'Хочу Adidas Samba 42 размера до 100000',
              'Кеды 43 размера adidas, белые',
              'Брюки, но не спортивные',
              'Calvin Klein джинсы',
              'Худи, желательно до 130000',
            ].map((s, i) => (
              <div
                key={i}
                onClick={() => handleQueryClick(s)}
                className="flex-shrink-0 bg-inputColor text-borderColor text-left text-[13px] sm:text-[15px] font-[500] px-4 sm:px-7 py-2 sm:py-3 rounded-full cursor-pointer max-w-[200px] sm:max-w-[230px] break-words leading-snug"
              >
                {s}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  useEffect(() => {
    const isMobile = window.innerWidth < 640; // sm breakpoint
    if (!isMobile) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, []);

  return (
    <>
      <Navbar />
      {/* <div className="relative w-full h-screen overflow-hidden bg-black"> */}
      <div className="relative w-full h-screen overflow-hidden bg-black max-w-screen max-h-screen sm:pb-0 pb-[50px]">
        {/* Desktop: animated horizontal gallery */}
        <div className="hidden sm:flex absolute left-0 top-[75px] items-center space-x-[20px] animate-gallery w-[calc(450px*6*2)]">
          {/* <div className="hidden sm:flex absolute top-1/2 left-0 -translate-y-1/2 items-center space-x-[20px] animate-gallery w-[calc(450px*6*2)]"> */}
          {[...Array(3)].map((_, repeatIndex) =>
            [1, 2, 3, 4, 5, 6].map((num) => (
              <img
                key={`${repeatIndex}-${num}`}
                src={`/images/image${num}.png`}
                alt={`Image ${num}`}
                className={`w-[250px] h-[340px] rounded-[30px] object-cover ${
                  num % 2 === 0 ? 'mt-40' : 'mt-20'
                }`}
              />
            ))
          )}
        </div>

        {/* Mobile: static 2x2 grid (2 rows × 2 columns) */}
        {/* <div className="grid sm:hidden grid-cols-2 gap-2 px-2 pt-6 mt-[0px]">
          {[1, 2, 3, 4].map((num) => (
            <img
              key={num}
              src={`/images/image${num}.png`}
              alt={`Image ${num}`}
              className="w-full h-[320px] rounded-[20px] object-cover mt-[30px]"
            />
          ))}
        </div> */}
        {/* Mobile: static 2x2 grid с анимацией */}
        {/* <div className="grid sm:hidden grid-cols-2 gap-2 px-2 pt-6 mt-[0px]">
  //Первый ряд — вправо
  <div className="col-span-2 flex space-x-2 animate-slide-right">
    {[4, 5, 6, 1, 2, 3].map((num) => (
      <img
        key={num}
        src={`/images/image${num}.png`}
        alt={`Image ${num}`}
        className="w-1/2 h-[320px] rounded-[20px] object-cover"
      />
    ))}
  </div>

  //Второй ряд — влево
  <div className="col-span-2 flex space-x-2 animate-slide-left mt-[30px]">
    {[1, 2, 4, 5, 6, 3].map((num) => (
      <img
        key={num}
        src={`/images/image${num}.png`}
        alt={`Image ${num}`}
        className="w-1/2 h-[320px] rounded-[20px] object-cover"
      />
    ))}
  </div>
</div>*/}
        <div className="sm:hidden px-2 flex flex-col justify-center h-screen -mt-[40px]">
          {/* Первый ряд — вправо с начальным смещением */}
          <div className="overflow-hidden">
            <div className="flex w-[200%] animate-slide-right-started-left space-x-2">
              {[4, 5, 6, 1, 2, 3].map((num) => (
                <img
                  key={num}
                  src={`/images/image${num}.png`}
                  alt={`Image ${num}`}
                  className="w-[50%] h-[320px] rounded-[20px] object-cover"
                />
              ))}
            </div>
          </div>

          {/* Второй ряд — влево (оставим как было или тоже подправим под нужную логику) */}
          <div className="overflow-hidden mt-[30px]">
            <div className="flex w-[200%] animate-slide-left space-x-2">
              {[1, 2, 4, 5, 6, 3].map((num) => (
                <img
                  key={num}
                  src={`/images/image${num}.png`}
                  alt={`Image ${num}`}
                  className="w-[50%] h-[320px] rounded-[20px] object-cover"
                />
              ))}
            </div>
          </div>
        </div>

        <SearchSection />
      </div>
    </>
  );
};

export default Home;
