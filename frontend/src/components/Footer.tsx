const Footer = () => {
  return (
    <footer className="bg-black text-white py-12 relative z-40">
      <div className="max-w-[1600px] mx-auto px-8">
        <p className="text-white text-lg font-montserrat text-center">
          Для предложений и вопросов пишите{" "}
          <a 
            href="https://t.me/khannzr" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline"
          >
            tg:@khannzr
          </a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
