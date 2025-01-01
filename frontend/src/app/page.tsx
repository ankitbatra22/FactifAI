'use client';

import { Header } from '@/components/layout/Header';
import { SearchBar } from '@/components/search/SearchBar';
import { ExampleQuery } from '@/components/search/ExampleQuery';
import { useRouter } from 'next/navigation';

const EXAMPLE_QUERIES = [
  { icon: "🌱", text: "Can Plants Communicate?" },
  { icon: "🐄", text: "Can Cows Make Friends?" },
  { icon: "🤖", text: "Can robots foster genuine human connections?" },
  { icon: "🎮", text: "Do video games improve cognitive skills?" },
];

export default function Home() {
  const router = useRouter();

  const handleExampleClick = (text: string) => {
    router.push(`/results?q=${encodeURIComponent(text)}`);
  };

  return (
    <div className="min-h-screen bg-[#0D1117] text-white flex flex-col">
      <Header />
      
      <main className="flex-1 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-violet-500/5" />
        
        <div className="container mx-auto px-4 pt-32 pb-16 max-w-3xl relative">
          <div className="space-y-8 text-center">
            <div className="space-y-4">
              <h1 className="text-5xl font-bold font-plus-jakarta bg-gradient-to-r from-blue-400 to-violet-400 text-transparent bg-clip-text">
                What would you like to fact check?
              </h1>
              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Get instant, research-backed answers to your questions using AI
              </p>
            </div>

            <SearchBar />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-12">
              {EXAMPLE_QUERIES.map((query, index) => (
                <ExampleQuery 
                  key={index}
                  icon={query.icon}
                  text={query.text}
                  onClick={handleExampleClick}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 