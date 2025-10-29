import { TransitCard } from "./components/TransitCard";
import { Header } from "./components/Header";
import { SearchSection } from "./components/SearchSection";

export default function App() {
  const featuredRoutes = [
    {
      routeNumber: "504",
      routeName: "King Streetcar",
      location: "King St West At Yonge St",
      station: "King Station",
      arrivalTimes: [
        { label: "2 min", isPrimary: true },
        { label: "in 13 mins" },
        { label: "in 27 mins" },
      ],
    },
    {
      routeNumber: "95",
      routeName: "York Mills",
      location: "York Mills Station",
      station: "York Mills Terminal",
      arrivalTimes: [
        { label: "5 min", isPrimary: true },
        { label: "in 18 mins" },
        { label: "in 35 mins" },
      ],
    },
    {
      routeNumber: "320",
      routeName: "Yonge Express",
      location: "Yonge St At Bloor St",
      station: "Bloor-Yonge Station",
      arrivalTimes: [
        { label: "1 min", isPrimary: true },
        { label: "in 8 mins" },
        { label: "in 15 mins" },
      ],
    },
  ];

  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: 'var(--md-sys-color-surface)' }}
    >
      <Header />
      
      {/* Hero Section */}
      <section className="py-16 px-6">
        <SearchSection />
      </section>

      {/* Featured Routes Section */}
      <section className="py-12 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 
              className="text-4xl mb-3"
              style={{ 
                color: 'var(--md-sys-color-on-surface)',
                fontWeight: '700'
              }}
            >
              Popular Routes
            </h2>
            <p 
              className="text-lg"
              style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
            >
              Quick access to frequently used transit routes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredRoutes.map((route, index) => (
              <TransitCard key={index} {...route} />
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer 
        className="mt-16 py-8 px-6 border-t"
        style={{ 
          borderColor: 'var(--md-sys-color-surface-variant)',
          backgroundColor: 'rgba(255, 255, 255, 0.5)'
        }}
      >
        <div className="container mx-auto text-center">
          <p 
            className="text-sm"
            style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
          >
            © 2025 Maple Mover • Canadian Transit Information
          </p>
        </div>
      </footer>
    </div>
  );
}
