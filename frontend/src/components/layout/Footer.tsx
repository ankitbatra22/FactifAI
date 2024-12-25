export function Footer() {
    return (
      <footer className="border-t border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <p className="text-sm text-gray-400 text-center">
            © {new Date().getFullYear()} Research Finder
          </p>
        </div>
      </footer>
    );
  }