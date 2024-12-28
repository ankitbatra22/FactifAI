import Link from 'next/link';

export function Header() {
  return (
    <header className="absolute top-0 left-0 w-full p-6 z-50">
      <div className="container mx-auto">
        <Link 
          href="/" 
          className="inline-block text-2xl font-bold 
                     bg-gradient-to-r from-blue-400/90 via-blue-500 to-violet-500 
                     text-transparent bg-clip-text 
                     hover:opacity-90 transition-opacity"
        >
          Factif AI
        </Link>
      </div>
    </header>
  );
}