import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";

interface ArrivalTime {
  label: string;
  isPrimary?: boolean;
}

interface TransitCardProps {
  routeNumber: string;
  routeName: string;
  location: string;
  station: string;
  arrivalTimes: ArrivalTime[];
}

export function TransitCard({
  routeNumber,
  routeName,
  location,
  station,
  arrivalTimes,
}: TransitCardProps) {
  return (
    <Card className="w-full max-w-md overflow-hidden shadow-lg rounded-[28px] border-0">
      <div className="p-8 space-y-6 bg-gradient-to-b from-white to-purple-50/30">
        {/* Route Number - Large with Material 3 styling */}
        <div className="text-center">
          <div 
            className="inline-flex items-center justify-center rounded-[32px] shadow-md px-8 py-6"
            style={{ backgroundColor: 'var(--md-sys-color-primary-container)' }}
          >
            <span 
              className="text-7xl"
              style={{ 
                color: 'var(--md-sys-color-on-primary-container)',
                fontWeight: '700'
              }}
            >
              {routeNumber}
            </span>
          </div>
        </div>

        {/* Route Name */}
        <div 
          className="text-center px-4 py-3 rounded-[20px]"
          style={{ 
            backgroundColor: 'var(--md-sys-color-secondary-container)',
            color: 'var(--md-sys-color-on-secondary-container)'
          }}
        >
          <span className="text-lg">{routeName}</span>
        </div>

        {/* Arrival Times - Vertical */}
        <div 
          className="space-y-4 p-6 rounded-[24px] shadow-sm"
          style={{ backgroundColor: 'var(--md-sys-color-surface-variant)' }}
        >
          {arrivalTimes.map((time, index) => (
            <div key={index} className="flex flex-col items-center">
              <div
                className={
                  time.isPrimary
                    ? "px-6 py-3 rounded-[16px] shadow-sm"
                    : "px-6 py-2 rounded-[12px]"
                }
                style={
                  time.isPrimary
                    ? {
                        backgroundColor: 'var(--md-sys-color-tertiary-container)',
                        color: 'var(--md-sys-color-on-tertiary-container)',
                      }
                    : {}
                }
              >
                <span
                  className={time.isPrimary ? "text-2xl" : "text-lg"}
                  style={
                    !time.isPrimary
                      ? { color: 'var(--md-sys-color-on-surface-variant)' }
                      : { fontWeight: '600' }
                  }
                >
                  {time.label}
                </span>
              </div>
              {index < arrivalTimes.length - 1 && (
                <span 
                  className="text-2xl my-2"
                  style={{ color: 'var(--md-sys-color-on-surface-variant)', opacity: 0.4 }}
                >
                  •
                </span>
              )}
            </div>
          ))}
        </div>

        {/* Last Stop */}
        <div 
          className="space-y-2 text-center p-5 rounded-[20px]"
          style={{ 
            backgroundColor: 'var(--md-sys-color-secondary-container)',
            color: 'var(--md-sys-color-on-secondary-container)'
          }}
        >
          <p className="text-sm opacity-70">Last stop</p>
          <p className="text-lg">{location}</p>
          <p className="text-sm opacity-70">{station}</p>
        </div>
      </div>
    </Card>
  );
}
