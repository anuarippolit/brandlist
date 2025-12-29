'use client';

// Generate or retrieve UUID for user tracking
export const getOrCreateUserId = (): string => {
  if (typeof window === 'undefined') return '';
  
  const STORAGE_KEY = 'brandlist_user_uuid';
  let userId = localStorage.getItem(STORAGE_KEY);
  
  if (!userId) {
    // Generate UUID v4
    userId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
    localStorage.setItem(STORAGE_KEY, userId);
  }
  
  return userId;
};

// Initialize GA4 dataLayer with user ID
export const initGA4 = () => {
  if (typeof window === 'undefined') return;
  
  const userId = getOrCreateUserId();
  
  // Initialize dataLayer if it doesn't exist
  window.dataLayer = window.dataLayer || [];
  
  // Set user ID for GA4
  window.dataLayer.push({
    'user_id': userId,
  });
  
  return userId;
};

// Track custom events
export const trackEvent = (
  eventName: string,
  parameters?: Record<string, any>
) => {
  if (typeof window === 'undefined' || !window.dataLayer) return;
  
  window.dataLayer.push({
    event: eventName,
    ...parameters,
  });
};

// Track product card click
export const trackProductCardClick = (product: {
  id: number;
  name: string;
  brand: string | null;
  sale_price: number | null;
  first_price?: number | null;
  shop: string;
  searchQuery?: string;
}) => {
  trackEvent('product_card_click', {
    product_id: product.id,
    product_name: product.name,
    product_brand: product.brand || '',
    product_price: product.sale_price || product.first_price || 0,
    shop_name: product.shop,
    search_query: product.searchQuery || '',
  });
};

// Track product detail view
export const trackProductDetailView = (product: {
  id: number;
  name: string;
  brand: string | null;
  sale_price: number | null;
  first_price?: number | null;
  shop: string;
}) => {
  trackEvent('view_product_detail', {
    product_id: product.id,
    product_name: product.name,
    product_brand: product.brand || '',
    product_price: product.sale_price || product.first_price || 0,
    shop_name: product.shop,
  });
};

// Track "go to shop" click
export const trackGoToShopClick = (product: {
  id: number;
  name: string;
  brand: string | null;
  sale_price: number | null;
  first_price?: number | null;
  shop: string;
  link: string;
}) => {
  trackEvent('click_go_to_shop', {
    product_id: product.id,
    product_name: product.name,
    product_brand: product.brand || '',
    product_price: product.sale_price || product.first_price || 0,
    shop_name: product.shop,
    shop_link: product.link,
  });
};

// Extend Window interface for TypeScript
declare global {
  interface Window {
    dataLayer: any[];
  }
}

