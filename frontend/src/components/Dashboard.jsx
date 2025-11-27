import React, { useState } from 'react';
import MapComponent from './Map';
import { analyzeMarket } from '../services/api';
import { Search, BarChart2, AlertTriangle, CheckCircle } from 'lucide-react';

const Dashboard = () => {
    const [country, setCountry] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!country) return;
        setLoading(true);
        setError(null);
        try {
            // Pass the country name directly. The backend now handles the lookup.
            const data = await analyzeMarket("XX", country);
            setResult(data);
        } catch (_err) {
            setError("Failed to analyze market. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Market Opportunity Finder</h1>
                <p className="text-gray-600">Identify and score tire recycling opportunities.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Input and Results */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Search className="w-5 h-5 text-blue-600" />
                            Analyze Market
                        </h2>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={country}
                                onChange={(e) => setCountry(e.target.value)}
                                placeholder="Enter country name..."
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            />
                            <button
                                onClick={handleAnalyze}
                                disabled={loading}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                            >
                                {loading ? 'Analyzing...' : 'Go'}
                            </button>
                        </div>
                        {error && <p className="mt-2 text-red-500 text-sm">{error}</p>}
                    </div>

                    {result && (
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-900">{result.country}</h3>
                                    <p className="text-sm text-gray-500">Market Analysis</p>
                                </div>
                                <div className={`px-4 py-2 rounded-lg font-bold text-xl ${result.analysis.score >= 70 ? 'bg-green-100 text-green-700' :
                                    result.analysis.score >= 40 ? 'bg-yellow-100 text-yellow-700' :
                                        'bg-red-100 text-red-700'
                                    }`}>
                                    {result.analysis.score}/100
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">GDP</span>
                                    <span className="font-medium">${(result.data.gdp / 1e9).toFixed(2)}B</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Population</span>
                                    <span className="font-medium">{(result.data.population / 1e6).toFixed(1)}M</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Est. Tire Waste</span>
                                    <span className="font-medium">{result.data.tire_waste.toLocaleString()} units</span>
                                </div>
                            </div>

                            <div className="border-t pt-4">
                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                    <BarChart2 className="w-4 h-4" /> Reasoning
                                </h4>
                                <p className="text-sm text-gray-600">{result.analysis.reasoning}</p>
                            </div>

                            <div className="border-t pt-4">
                                <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-600">
                                    <CheckCircle className="w-4 h-4" /> Opportunities
                                </h4>
                                <ul className="text-sm text-gray-600 list-disc list-inside">
                                    {result.analysis.opportunities.map((opp, i) => (
                                        <li key={i}>{opp}</li>
                                    ))}
                                </ul>
                            </div>

                            <div className="border-t pt-4">
                                <h4 className="font-semibold mb-2 flex items-center gap-2 text-amber-600">
                                    <AlertTriangle className="w-4 h-4" /> Risks
                                </h4>
                                <ul className="text-sm text-gray-600 list-disc list-inside">
                                    {result.analysis.risks.map((risk, i) => (
                                        <li key={i}>{risk}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column: Map */}
                <div className="lg:col-span-2 h-[600px] bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <MapComponent markers={result && result.data.lat && result.data.lng ? [{ lat: result.data.lat, lng: result.data.lng, country: result.country, score: result.analysis.score }] : []} />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
