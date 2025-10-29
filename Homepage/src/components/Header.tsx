import { MapPin } from "lucide-react";

export function Header() {
  return (
    <header 
      className="sticky top-0 z-50 backdrop-blur-md border-b"
      style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'var(--md-sys-color-surface-variant)'
      }}
    >
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          <div 
            className="flex items-center justify-center w-12 h-12 rounded-[16px] shadow-md"
            style={{ backgroundColor: 'var(--md-sys-color-primary)' }}
          >
            <MapPin 
              className="w-6 h-6" 
              style={{ color: 'var(--md-sys-color-on-primary)' }}
            />
          </div>
          <div>
            <h1 
              className="text-2xl"
              style={{ 
                color: 'var(--md-sys-color-on-surface)',
                fontWeight: '700'
              }}
            >
              Maple Mover
            </h1>
            <p 
              className="text-sm"
              style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
            >
              Canadian Transit
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
