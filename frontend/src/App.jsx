import { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { KPITile }      from './components/KPITile';
import { LiveChart }    from './components/LiveChart';
import './index.css';

const MAX_HISTORY = 60;

export default function App() {
  const { data, status } = useWebSocket('ws://localhost:8000/ws/analytics');
  const [history, setHistory] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    if (!data) return;
    const point = {
      time:     new Date().toLocaleTimeString(),
      people:   data.total_people,
      vehicles: data.total_vehicles,
    };
    setHistory(h => [...h.slice(-MAX_HISTORY), point]);
  }, [data]);

  // Fetch history every 10 seconds
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/history?limit=10');
        const json = await res.json();
        setHistoricalData(json);
      } catch (err) {
        console.error("Failed to fetch history", err);
      }
    };
    fetchHistory();
    const intv = setInterval(fetchHistory, 10000);
    return () => clearInterval(intv);
  }, []);

  return (
    <div className='min-h-screen p-6 lg:p-10 relative overflow-hidden'>
      {/* Background ambient light effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
      
      <div className="max-w-7xl mx-auto relative z-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className='text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400'>
              Crowd Sense Pro
            </h1>
            <p className="text-slate-400 mt-2 font-medium">Real-Time Traffic & AI Analytics Edge Dashboard</p>
          </div>
          <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700 backdrop-blur-md">
            <span className={`w-3 h-3 rounded-full ${status === 'connected' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-rose-500'}`} />
            <span className='text-sm text-slate-300 font-medium uppercase tracking-wider'>{status}</span>
          </div>
        </header>

        {data?.alert && (
          <div className="bg-rose-500/20 border border-rose-500/50 text-rose-300 p-4 mb-8 rounded-xl shadow-[0_0_20px_rgba(244,63,94,0.2)] backdrop-blur-md flex items-center space-x-3" role="alert">
            <span className="text-2xl">⚠️</span>
            <div>
              <p className="font-bold tracking-wide">CRITICAL DENSITY ALERT</p>
              <p className="text-sm opacity-90">{data.message}</p>
            </div>
          </div>
        )}

        <div className='grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6'>
          <KPITile label='Live People' value={data?.total_people} icon='🚶' color='border-pink-500' />
          <KPITile label='Live Vehicles' value={data?.total_vehicles} icon='🚗' color='border-blue-500' />
          <KPITile label='Density Level' value={data?.density_level} icon='🔥' color='border-amber-400' />
          <KPITile label='Danger Score' value={data?.density_score} icon='📊' color='border-purple-500' />
        </div>

        <div className='grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
          <KPITile label='Zone A (Left)' value={data?.zone_a} icon='🟢' color='border-emerald-500' />
          <KPITile label='Zone B (Right)' value={data?.zone_b} icon='🔵' color='border-cyan-500' />
          <KPITile label='Tripwire (IN)' value={data?.crossed_in} icon='⬇️' color='border-indigo-500' />
          <KPITile label='Tripwire (OUT)' value={data?.crossed_out} icon='⬆️' color='border-teal-500' />
        </div>
        
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          <div className='glass-panel rounded-2xl p-6 lg:col-span-1 flex flex-col'>
            <h2 className='font-bold mb-6 text-slate-200 text-lg tracking-wide uppercase'>Count History</h2>
            <div className="flex-1 min-h-[250px]">
              <LiveChart history={history} />
            </div>
          </div>
          
          <div className='glass-panel rounded-2xl p-6 lg:col-span-2'>
            <div className="flex justify-between items-center mb-6">
              <h2 className='font-bold text-slate-200 text-lg tracking-wide uppercase'>AI Video Feed</h2>
              <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/30">LIVE</span>
            </div>
            {data?.frame ? (
              <div className="relative rounded-xl overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)] border border-slate-700">
                <img src={`data:image/jpeg;base64,${data.frame}`} className='w-full object-cover aspect-video' alt='live AI feed' />
              </div>
            ) : (
              <div className="w-full aspect-video bg-slate-800/50 rounded-xl border border-slate-700 flex items-center justify-center">
                <p className="text-slate-500 font-medium">Waiting for video stream...</p>
              </div>
            )}
          </div>
        </div>

        <div className='glass-panel rounded-2xl p-6'>
            <h2 className='font-bold mb-6 text-slate-200 text-lg tracking-wide uppercase'>Recent Database Records</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/50 text-slate-200 uppercase font-semibold">
                  <tr>
                    <th className="px-6 py-3 rounded-tl-lg">Time</th>
                    <th className="px-6 py-3">People</th>
                    <th className="px-6 py-3">Density Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {historicalData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 font-mono">{new Date(row.timestamp * 1000).toLocaleTimeString()}</td>
                      <td className="px-6 py-4">{row.total_people}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          row.density_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                          row.density_level === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' :
                          row.density_level === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-rose-500/20 text-rose-400'
                        }`}>
                          {row.density_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {historicalData.length === 0 && (
                    <tr>
                      <td colSpan="3" className="px-6 py-4 text-center text-slate-500">No records found. Waiting for db sync...</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
        </div>
      </div>
    </div>
  );
}
