import Link from 'next/link';
import { useState } from 'react';
import { DonationModal } from '../common/DonationModal';

export function Header() {
  const [isDonationModalOpen, setIsDonationModalOpen] = useState(false);

  return (
    <>
      <header className="absolute top-0 left-0 w-full p-6 z-40">
        <div className="container mx-auto flex justify-between items-center">
          <Link 
            href="/" 
            className="inline-block text-2xl font-bold 
                       bg-gradient-to-r from-blue-400/90 via-blue-500 to-violet-500 
                       text-transparent bg-clip-text 
                       hover:opacity-90 transition-opacity"
          >
            FactifAI
          </Link>

          <button
            onClick={() => setIsDonationModalOpen(true)}
            className="px-4 py-2 text-sm font-medium
                     bg-gradient-to-r from-blue-500 to-violet-500
                     text-white rounded-lg
                     hover:opacity-90 transition-all
                     transform hover:scale-105"
          >
            Support ❤️
          </button>
        </div>
      </header>

      <DonationModal 
        isOpen={isDonationModalOpen}
        onClose={() => setIsDonationModalOpen(false)}
      />
    </>
  );
}