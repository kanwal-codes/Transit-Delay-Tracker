import { TransitCard } from "./components/TransitCard";

export default function App() {
  const sampleBusData = {
    routeNumber: "504",
    routeName: "504-King West",
    location: "King St West At Yonge St West Side",
    station: "King Station",
    arrivalTimes: [
      { label: "13 min", isPrimary: true },
      { label: "in 13 mins" },
      { label: "in 27 mins" },
      { label: "in 33 mins" },
    ],
  };

  return (
    <div 
      className="min-h-screen p-6 flex items-center justify-center"
      style={{ backgroundColor: 'var(--md-sys-color-surface)' }}
    >
      <TransitCard {...sampleBusData} />
    </div>
  );
}
