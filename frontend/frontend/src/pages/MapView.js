export default function MapView() {
  const dummyRoutes = [
    { from: "A", to: "B", risk: "Low" },
    { from: "C", to: "D", risk: "High" },
  ];

  return (
    <div className="p-8 grid gap-4">
      {dummyRoutes.map((r, i) => (
        <div key={i} className="border p-4 rounded shadow hover:shadow-lg transition">
          <h2 className="font-bold">{r.from} → {r.to}</h2>
          <p>Risk: <span className={r.risk === "High" ? "text-red-600" : "text-green-600"}>{r.risk}</span></p>
        </div>
      ))}
    </div>
  );
}
