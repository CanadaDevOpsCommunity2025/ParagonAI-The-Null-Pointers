import Dashboard from "./components/Dashboard";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-black to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="mb-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="h-1 w-16 bg-gradient-to-r from-yellow-500 to-amber-600 rounded-full"></div>
            <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-100 to-gray-300">
              Customer Support Triage
            </h1>
          </div>
          <p className="text-xl text-gray-400 font-medium ml-20 tracking-wide">
            AI-powered intelligent ticket analysis and routing system
          </p>
        </header>
        <Dashboard />
      </div>
    </div>
  );
}
