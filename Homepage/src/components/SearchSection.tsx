import { Search, Navigation } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";

export function SearchSection() {
  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-3">
        <h2 
          className="text-5xl"
          style={{ 
            color: 'var(--md-sys-color-on-surface)',
            fontWeight: '800'
          }}
        >
          Find Your Route
        </h2>
        <p 
          className="text-xl"
          style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
        >
          Real-time transit information across Canada
        </p>
      </div>

      <div 
        className="p-8 rounded-[32px] shadow-xl space-y-4"
        style={{ 
          backgroundColor: 'var(--md-sys-color-primary-container)',
        }}
      >
        <div className="relative">
          <Search 
            className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5"
            style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
          />
          <Input
            placeholder="Search for routes, stops, or destinations..."
            className="pl-12 h-14 rounded-[20px] border-0 shadow-sm text-lg"
            style={{ 
              backgroundColor: 'white',
              color: 'var(--md-sys-color-on-surface)'
            }}
          />
        </div>
        
        <Button 
          className="w-full h-14 rounded-[20px] shadow-md text-lg gap-2"
          style={{ 
            backgroundColor: 'var(--md-sys-color-primary)',
            color: 'var(--md-sys-color-on-primary)',
            fontWeight: '600'
          }}
        >
          <Navigation className="w-5 h-5" />
          Use My Location
        </Button>
      </div>
    </div>
  );
}
