'use client';

import { useRouter, usePathname } from 'next/navigation';

const Breadcrumb = ({
  breadcrumbs,
}: {
  breadcrumbs: { label: string; href?: string }[];
}) => {
  const router = useRouter();
  const pathname = usePathname();

  // Check if the user is inside the "favorites" section
  const isFavoritesPage = pathname.startsWith('/favorites');

  const handleClick = (href?: string) => {
    if (href) {
      router.push(href);
    }
  };

  return (
    <nav className="px-8 py-4 text-gray-400 font-inter text-[16px] font-normal ml-4 sm:ml-[340px]">
      {isFavoritesPage ? (
        <>
          <span
            className="cursor-pointer hover:text-white"
            onClick={() => handleClick('/home')}
          >
            Поиск
          </span>
          <span className="mx-2">&gt;</span>
          <span
            className="cursor-pointer hover:text-white"
            onClick={() => handleClick('/favorites')}
          >
            Избранное
          </span>
        </>
      ) : (
        breadcrumbs.map((breadcrumb, index) => (
          <span key={index} className="inline-flex items-center">
            <span
              className={`cursor-pointer ${
                breadcrumb.href ? 'hover:text-white' : 'text-white'
              }`}
              onClick={() => handleClick(breadcrumb.href)}
            >
              {decodeURIComponent(breadcrumb.label)}
            </span>
            {index < breadcrumbs.length - 1 && (
              <span className="mx-2">&gt;</span>
            )}
          </span>
        ))
      )}
    </nav>
  );
};

export default Breadcrumb;
