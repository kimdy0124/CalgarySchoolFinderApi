"use client";

import { useMemo, useState } from "react";

type District = {
  name: string;
  type: string;
};

type School = {
  school_id: number;
  name: string;
  address_line?: string;
  postal_code?: string;
  phone?: string;
  email?: string;
  latitude?: number;
  longitude?: number;
  distance_km?: number;
  district?: District;
};

export default function Home() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

  const [lat, setLat] = useState("51.0486");
  const [lng, setLng] = useState("-114.0708");
  const [radiusKm, setRadiusKm] = useState("10");
  const [districtType, setDistrictType] = useState<string>("");

  const [schools, setSchools] = useState<School[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string>("");

  const canSearch = useMemo(() => {
    const a = Number(lat);
    const b = Number(lng);
    const r = Number(radiusKm);
    return Number.isFinite(a) && Number.isFinite(b) && Number.isFinite(r) && r > 0;
  }, [lat, lng, radiusKm]);

  async function search() {
    if (!canSearch) return;
    setErr("");
    setLoading(true);

    try {
      const qs = new URLSearchParams({
        lat: lat.trim(),
        lng: lng.trim(),
        radius_km: radiusKm.trim(),
      });
      if (districtType) qs.set("district_type", districtType);

      const res = await fetch(`${apiBase}/schools/nearby?${qs.toString()}`);
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`API ${res.status}: ${text || "Request failed"}`);
      }
      const data = await res.json();
      setSchools(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setErr(e?.message ?? "Unknown error");
      setSchools([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-5 py-10">
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            Calgary School Finder
          </h1>
          <p className="text-gray-600">
            MVP UI (Next.js + Tailwind). Next step: Address search + Map.
          </p>
        </header>

        <section className="mt-8 bg-white rounded-2xl shadow-sm border p-5">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <Field label="Latitude">
              <input
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                placeholder="51.0486"
              />
            </Field>

            <Field label="Longitude">
              <input
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                placeholder="-114.0708"
              />
            </Field>

            <Field label="Radius (km)">
              <input
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring"
                value={radiusKm}
                onChange={(e) => setRadiusKm(e.target.value)}
                placeholder="10"
              />
            </Field>

            <Field label="District type">
              <select
                className="w-full border rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring"
                value={districtType}
                onChange={(e) => setDistrictType(e.target.value)}
              >
                <option value="">All</option>
                <option value="Public">Public</option>
                <option value="Catholic">Catholic</option>
                <option value="Charter">Charter</option>
                <option value="Private">Private</option>
              </select>
            </Field>

            <div className="flex items-end">
              <button
                onClick={search}
                disabled={!canSearch || loading}
                className="w-full rounded-lg bg-black text-white px-4 py-2 disabled:opacity-50"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>
          </div>

          {err && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-red-700 text-sm">
              {err}
            </div>
          )}

          <div className="mt-4 text-xs text-gray-500">
            API Base: <span className="font-mono">{apiBase}</span>
          </div>
        </section>

        <section className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Results</h2>
            <div className="text-sm text-gray-600">
              {schools.length} school{schools.length === 1 ? "" : "s"}
            </div>
          </div>

          <div className="mt-4 grid gap-3">
            {schools.map((s) => (
              <div key={s.school_id} className="bg-white rounded-2xl border shadow-sm p-5">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                  <div>
                    <div className="text-lg font-semibold">{s.name}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {s.district?.type ? `${s.district.type} · ` : ""}
                      {s.district?.name ?? ""}
                    </div>
                  </div>

                  <div className="text-sm text-gray-700">
                    {typeof s.distance_km === "number" ? (
                      <span className="inline-flex items-center rounded-full border px-3 py-1">
                        {s.distance_km.toFixed(2)} km
                      </span>
                    ) : null}
                  </div>
                </div>

                <div className="mt-3 text-sm">
                  <div className="text-gray-800">
                    {s.address_line ?? ""}
                    {s.postal_code ? ` (${s.postal_code})` : ""}
                  </div>

                  <div className="mt-2 flex flex-wrap gap-3 text-gray-600">
                    {s.phone && <span>📞 {s.phone}</span>}
                    {s.email && <span>✉️ {s.email}</span>}
                  </div>
                </div>
              </div>
            ))}

            {schools.length === 0 && !loading && !err && (
              <div className="text-gray-600 text-sm">
                Try searching with Calgary downtown coordinates (default values) to see demo results.
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function Field(props: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-600">{props.label}</label>
      {props.children}
    </div>
  );
}
