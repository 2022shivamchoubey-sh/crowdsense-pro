export function KPITile({ label, value, icon, color }) {
  return (
    <div className={`glass-panel rounded-2xl p-6 border-l-4 ${color} transition-all duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]`}>
      <div className="flex justify-between items-center mb-2">
        <p className='text-sm text-slate-400 font-semibold uppercase tracking-wider'>{label}</p>
        <span className='text-2xl opacity-80'>{icon}</span>
      </div>
      <p className='text-5xl font-bold tracking-tight text-white drop-shadow-lg'>{value ?? '--'}</p>
    </div>
  );
}
