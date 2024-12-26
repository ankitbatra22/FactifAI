export function SearchLoading() {
    return (
      <div className="text-center space-y-4 py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-blue-500 mb-4" />
        <div className="space-y-2">
          <p className="text-lg text-white/90 font-medium">Indexing millions of research papers</p>
          <p className="text-sm text-gray-400">Finding the most relevant sources for you...</p>
        </div>
      </div>
    );
  }