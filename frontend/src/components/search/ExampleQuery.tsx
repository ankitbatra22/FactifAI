
'use client';

interface ExampleQueryProps {
    icon: string;
    text: string;
    onClick: (text: string) => void;
  }
  
  export function ExampleQuery({ icon, text, onClick }: ExampleQueryProps) {
    return (
      <button
        onClick={() => onClick(text)}
        className="flex items-center gap-3 px-4 py-3 
                   bg-[#2A2A2A] rounded-lg
                   hover:bg-[#333333] transition-colors
                   text-left w-full group"
      >
        <span className="text-xl group-hover:scale-110 transition-transform">
          {icon}
        </span>
        <span className="text-gray-300">{text}</span>
      </button>
    );
  }