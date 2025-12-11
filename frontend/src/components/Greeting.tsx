// 'use client';
// import { useEffect, useState } from 'react';

// const Greeting = () => {
//   return (
//     <div className="text-center max-w-[700px] mx-auto text-white px-4 mt-10 min-h-[96px]">
//       {/* LINE 1 (starts immediately, but only visible after delay) */}
//       <div className="overflow-hidden">
//         <span className="reverse-typewriter-first block text-[20px] sm:text-[24px] leading-[30px] sm:leading-[36px] font-poppins font-normal mx-auto text-center max-w-fit">
//           Привет — это{' '}
//           <span className="font-bangers">
//             BRAND<span className="text-[#6F00FF]">LIST</span>
//           </span>
//           , твой ассистент по поиску
//         </span>
//       </div>

//       {/* LINE 2 (starts deleting immediately with caret) */}
//       <div className="overflow-hidden mt-2">
//         <span className="reverse-typewriter-second block text-[20px] sm:text-[24px] leading-[30px] sm:leading-[36px] font-poppins font-normal mx-auto text-center max-w-fit">
//           одежды в магазинах Казахстана.
//         </span>
//       </div>
//     </div>
//   );
// };

// export default Greeting;

'use client';
import { useEffect, useState } from 'react';

const Greeting = () => {
  const [showNewTyping, setShowNewTyping] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowNewTyping(true);
    }, 8000); // wait for both reverse lines to finish
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="text-center max-w-[700px] mx-auto text-white px-4 mt-10 min-h-[160px]">
      {!showNewTyping && (
        <>
          {/* Line 1 (deletes second) */}
          <div className="overflow-hidden">
            <span className="reverse-typewriter-first block text-[20px] sm:text-[24px] leading-[30px] font-poppins font-normal mx-auto text-center max-w-fit">
              Привет — это{' '}
              <span className="font-bangers">
                BRAND<span className="text-[#6F00FF]">LIST</span>
              </span>
              , твой ассистент по поиску
            </span>
          </div>

          {/* Line 2 (deletes first) */}
          <div className="overflow-hidden mt-2">
            <span className="reverse-typewriter-second block text-[20px] sm:text-[24px] leading-[30px] font-poppins font-normal mx-auto text-center max-w-fit">
              одежды в магазинах Казахстана.
            </span>
          </div>
        </>
      )}

      {showNewTyping && (
        <>
          {/* New Typing Block */}
          <div className="overflow-hidden">
            <span className="typewriter-line1 block text-[20px] sm:text-[24px] leading-[30px] font-poppins font-normal mx-auto text-center max-w-fit">
              Просто напиши мне{' '}
              <span className="text-[#6F00FF] font-semibold italic">
                название
              </span>
              , или{' '}
              <span className="text-[#6F00FF] font-semibold italic">
                категорию
              </span>
              ,
            </span>
          </div>
          <div className="overflow-hidden mt-1">
            <span className="typewriter-line2 block text-[20px] sm:text-[24px] leading-[30px] font-poppins font-normal mx-auto text-center max-w-fit">
              <span className="text-[#6F00FF] font-semibold italic">
                {' '}
                бренд
              </span>
              ,{' '}
              <span className="text-[#6F00FF] font-semibold italic">
                размер
              </span>
              ,{' '}
              <span className="text-[#6F00FF] font-semibold italic">цену</span>{' '}
              — или все вместе.
            </span>
          </div>
          <div className="overflow-hidden mt-1">
            <span className="typewriter-line3 block text-[20px] sm:text-[24px] leading-[30px] font-poppins font-normal mx-auto text-center max-w-fit">
              И я найду то, что ты хочешь!
            </span>
          </div>
        </>
      )}
    </div>
  );
};

export default Greeting;
